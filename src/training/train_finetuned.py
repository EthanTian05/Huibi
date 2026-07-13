"""路径A：微调预训练模型作评分器，对应Docs/03-模型训练与微调方案.md「路径A：微调」。

训练循环严格按"225原则"写（见Docs/03号文档"225原则"一节）：
  - 2层循环：外层遍历epoch，内层遍历batch；
  - 5个核心步骤：optimizer.zero_grad() → forward → 算loss → loss.backward() → optimizer.step()。
在这个基础之上叠加了：验证集早停、梯度裁剪、按essay_set分层的QWK监控。

用法：
    python -m src.training.train_finetuned --model_name distilbert-base-uncased --epochs 3 \
        --output_dir models/essay-scorer-finetuned/v1
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

from src.training.common import load_score_ranges, macro_qwk

TRAIN_PATH = Path("data/processed/train.csv")
VAL_PATH = Path("data/processed/val.csv")
TEST_PATH = Path("data/processed/test.csv")


class EssayDataset(Dataset):
    def __init__(self, df: pd.DataFrame, tokenizer, max_length: int):
        self.essays = df["essay"].astype(str).tolist()
        self.labels = df["score_norm"].astype(float).tolist()
        self.essay_set = df["essay_set"].astype(int).tolist()
        self.domain1_score = df["domain1_score"].astype(int).tolist()
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.essays)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.essays[idx],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "label": torch.tensor(self.labels[idx], dtype=torch.float),
            "essay_set": self.essay_set[idx],
            "domain1_score": self.domain1_score[idx],
        }


class ScorerModel(nn.Module):
    """预训练encoder + 回归头，输出压到[0,1]匹配归一化后的分数。"""

    def __init__(self, model_name: str):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size
        self.dropout = nn.Dropout(0.1)
        self.regressor = nn.Linear(hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_repr = outputs.last_hidden_state[:, 0, :]  # [CLS] token表示
        cls_repr = self.dropout(cls_repr)
        score = torch.sigmoid(self.regressor(cls_repr)).squeeze(-1)
        return score


def evaluate(model, loader, device, score_ranges) -> tuple[float, float, dict]:
    model.eval()
    all_preds, all_labels, all_sets, all_domain = [], [], [], []
    total_loss = 0.0
    criterion = nn.MSELoss()
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            preds = model(input_ids, attention_mask)
            loss = criterion(preds, labels)
            total_loss += loss.item() * len(labels)
            all_preds.extend(preds.cpu().numpy().tolist())
            all_labels.extend(labels.cpu().numpy().tolist())
            all_sets.extend(batch["essay_set"].numpy().tolist() if torch.is_tensor(batch["essay_set"]) else batch["essay_set"])
            all_domain.extend(batch["domain1_score"].numpy().tolist() if torch.is_tensor(batch["domain1_score"]) else batch["domain1_score"])
    avg_loss = total_loss / len(all_labels)
    qwk, per_set_qwk = macro_qwk(np.array(all_preds), np.array(all_domain), np.array(all_sets), score_ranges)
    return avg_loss, qwk, per_set_qwk


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", default="distilbert-base-uncased")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--max_length", type=int, default=256)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--patience", type=int, default=2)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")

    score_ranges = load_score_ranges()
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)

    train_loader = DataLoader(EssayDataset(train_df, tokenizer, args.max_length), batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(EssayDataset(val_df, tokenizer, args.max_length), batch_size=args.batch_size)
    test_loader = DataLoader(EssayDataset(test_df, tokenizer, args.max_length), batch_size=args.batch_size)

    model = ScorerModel(args.model_name).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
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
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)

            optimizer.zero_grad()                                     # 步骤1：梯度清零
            preds = model(input_ids, attention_mask)                  # 步骤2：正向传播
            loss = criterion(preds, labels)                           # 步骤3：损失计算
            loss.backward()                                           # 步骤4：反向传播
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)   # 增强：梯度裁剪
            optimizer.step()                                          # 步骤5：参数更新

            running_loss += loss.item() * len(labels)
        # ===== "225原则"训练循环结束 =====

        train_loss = running_loss / len(train_df)
        val_loss, val_qwk, val_per_set = evaluate(model, val_loader, device, score_ranges)
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

    # 加载最优checkpoint后在测试集上最终评估
    model.load_state_dict(torch.load(output_dir / "pytorch_model.bin", map_location=device))
    test_loss, test_qwk, test_per_set = evaluate(model, test_loader, device, score_ranges)
    print(f"\n最终测试集结果: test_loss={test_loss:.4f} test_QWK(宏平均)={test_qwk:.4f}")
    print(f"各essay_set的QWK: {test_per_set}")

    tokenizer.save_pretrained(output_dir)
    with open(output_dir / "training_log.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "model_name": args.model_name,
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
    print(f"模型/分词器/训练日志已保存到 {output_dir}")


if __name__ == "__main__":
    main()
