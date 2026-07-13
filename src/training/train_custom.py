"""路径B：自定义构建模型（不依赖任何预训练权重，从零训练），对应
Docs/03-模型训练与微调方案.md「路径B：自定义构建」。满足要求文档第6条
"自定义构建模型"加分项——这里的Embedding层是随机初始化的，整个模型的每一个
参数都是从零开始训练出来的，不加载任何HuggingFace/第三方预训练checkpoint。

架构：Embedding(随机初始化) → BiLSTM → Attention池化 → 回归头，是Transformer
之前AES领域的经典架构思路。

训练循环同样严格按"225原则"写（2层循环 + 5个核心步骤），见Docs/03号文档。

用法：
    python -m src.training.train_custom --epochs 10 --output_dir models/essay-scorer-custom/v1
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

from src.training.common import load_score_ranges, macro_qwk

TRAIN_PATH = Path("data/processed/train.csv")
VAL_PATH = Path("data/processed/val.csv")
TEST_PATH = Path("data/processed/test.csv")

PAD_TOKEN, UNK_TOKEN = "<pad>", "<unk>"
TOKEN_PATTERN = re.compile(r"[A-Za-z']+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def build_vocab(essays: list[str], vocab_size: int) -> dict[str, int]:
    counter = Counter()
    for essay in essays:
        counter.update(tokenize(essay))
    most_common = counter.most_common(vocab_size - 2)
    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
    for word, _ in most_common:
        vocab[word] = len(vocab)
    return vocab


def encode(text: str, vocab: dict[str, int], max_length: int) -> list[int]:
    tokens = tokenize(text)[:max_length]
    ids = [vocab.get(t, vocab[UNK_TOKEN]) for t in tokens]
    ids += [vocab[PAD_TOKEN]] * (max_length - len(ids))
    return ids


class EssayDataset(Dataset):
    def __init__(self, df: pd.DataFrame, vocab: dict[str, int], max_length: int):
        self.input_ids = [encode(e, vocab, max_length) for e in df["essay"].astype(str)]
        self.labels = df["score_norm"].astype(float).tolist()
        self.essay_set = df["essay_set"].astype(int).tolist()
        self.domain1_score = df["domain1_score"].astype(int).tolist()

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids": torch.tensor(self.input_ids[idx], dtype=torch.long),
            "label": torch.tensor(self.labels[idx], dtype=torch.float),
            "essay_set": self.essay_set[idx],
            "domain1_score": self.domain1_score[idx],
        }


class BiLSTMAttentionScorer(nn.Module):
    """完全从零初始化的模型：Embedding随机初始化 + BiLSTM + Attention池化 + 回归头。"""

    def __init__(self, vocab_size: int, embed_dim: int = 128, hidden_dim: int = 128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.attn_fc = nn.Linear(hidden_dim * 2, 1)
        self.regressor = nn.Linear(hidden_dim * 2, 1)
        self.dropout = nn.Dropout(0.3)

    def forward(self, input_ids):
        mask = (input_ids != 0).float()  # [B, T]
        embedded = self.embedding(input_ids)  # [B, T, E]
        lstm_out, _ = self.lstm(embedded)  # [B, T, 2H]

        attn_scores = self.attn_fc(lstm_out).squeeze(-1)  # [B, T]
        attn_scores = attn_scores.masked_fill(mask == 0, float("-inf"))
        attn_weights = torch.softmax(attn_scores, dim=1).unsqueeze(-1)  # [B, T, 1]
        pooled = (lstm_out * attn_weights).sum(dim=1)  # [B, 2H]

        pooled = self.dropout(pooled)
        score = torch.sigmoid(self.regressor(pooled)).squeeze(-1)
        return score


def evaluate(model, loader, device, score_ranges) -> tuple[float, float, dict]:
    model.eval()
    all_preds, all_labels, all_sets, all_domain = [], [], [], []
    total_loss = 0.0
    criterion = nn.MSELoss()
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["label"].to(device)
            preds = model(input_ids)
            loss = criterion(preds, labels)
            total_loss += loss.item() * len(labels)
            all_preds.extend(preds.cpu().numpy().tolist())
            all_labels.extend(labels.cpu().numpy().tolist())
            all_sets.extend(batch["essay_set"].numpy().tolist())
            all_domain.extend(batch["domain1_score"].numpy().tolist())
    avg_loss = total_loss / len(all_labels)
    qwk, per_set_qwk = macro_qwk(np.array(all_preds), np.array(all_domain), np.array(all_sets), score_ranges)
    return avg_loss, qwk, per_set_qwk


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--max_length", type=int, default=300)
    parser.add_argument("--vocab_size", type=int, default=20000)
    parser.add_argument("--embed_dim", type=int, default=128)
    parser.add_argument("--hidden_dim", type=int, default=128)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--patience", type=int, default=3)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")

    score_ranges = load_score_ranges()
    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)

    vocab = build_vocab(train_df["essay"].astype(str).tolist(), args.vocab_size)
    print(f"词表大小: {len(vocab)}（只从训练集统计，不看验证/测试集，避免泄漏）")

    train_loader = DataLoader(EssayDataset(train_df, vocab, args.max_length), batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(EssayDataset(val_df, vocab, args.max_length), batch_size=args.batch_size)
    test_loader = DataLoader(EssayDataset(test_df, vocab, args.max_length), batch_size=args.batch_size)

    model = BiLSTMAttentionScorer(len(vocab), args.embed_dim, args.hidden_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.MSELoss()

    history = []
    best_val_qwk = -1.0
    epochs_without_improvement = 0
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ===== "225原则"：2层循环（epoch × batch）+ 5个核心步骤 =====
    for epoch in range(args.epochs):                                  # 外层循环：遍历训练轮次(epoch)
        model.train()
        running_loss = 0.0
        for batch in train_loader:                                    # 内层循环：遍历数据批次(batch)
            input_ids = batch["input_ids"].to(device)
            labels = batch["label"].to(device)

            optimizer.zero_grad()                                     # 步骤1：梯度清零
            preds = model(input_ids)                                  # 步骤2：正向传播
            loss = criterion(preds, labels)                           # 步骤3：损失计算
            loss.backward()                                           # 步骤4：反向传播
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)   # 增强：梯度裁剪
            optimizer.step()                                          # 步骤5：参数更新

            running_loss += loss.item() * len(labels)
        # ===== "225原则"训练循环结束 =====

        train_loss = running_loss / len(train_df)
        val_loss, val_qwk, _ = evaluate(model, val_loader, device, score_ranges)
        print(f"[Epoch {epoch + 1}/{args.epochs}] train_loss={train_loss:.4f} val_loss={val_loss:.4f} val_QWK={val_qwk:.4f}")
        history.append({"epoch": epoch + 1, "train_loss": train_loss, "val_loss": val_loss, "val_qwk": val_qwk})

        if val_qwk > best_val_qwk:
            best_val_qwk = val_qwk
            epochs_without_improvement = 0
            torch.save(model.state_dict(), output_dir / "pytorch_model.bin")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                print(f"验证集QWK连续{args.patience}轮没有提升，提前停止（早停）")
                break

    model.load_state_dict(torch.load(output_dir / "pytorch_model.bin", map_location=device))
    test_loss, test_qwk, test_per_set = evaluate(model, test_loader, device, score_ranges)
    print(f"\n最终测试集结果: test_loss={test_loss:.4f} test_QWK(宏平均)={test_qwk:.4f}")
    print(f"各essay_set的QWK: {test_per_set}")

    with open(output_dir / "vocab.json", "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False)
    with open(output_dir / "model_config.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "vocab_size": len(vocab),
                "embed_dim": args.embed_dim,
                "hidden_dim": args.hidden_dim,
                "max_length": args.max_length,
            },
            f,
        )
    with open(output_dir / "training_log.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "history": history,
                "best_val_qwk": best_val_qwk,
                "test_qwk": test_qwk,
                "test_per_set_qwk": test_per_set,
                "args": vars(args),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"模型/词表/训练日志已保存到 {output_dir}")


if __name__ == "__main__":
    main()
