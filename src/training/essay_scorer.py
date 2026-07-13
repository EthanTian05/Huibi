"""EssayScorer：把路径A(微调)和路径B(自定义构建)两个训练好的评分模型封装成
统一推理接口，供src/agents/nodes.py里的scoring_tool_node调用。

**关于分项评分(trait_scores)的诚实说明**：当前两条训练脚本
（train_finetuned.py / train_custom.py）只训练了"整体分"这一个回归目标
（对应ASAP-AES的domain1_score，也是QWK官方评估的对象）。原计划里的"多头
分项输出"（内容/结构/语言）因为不同essay_set的trait标注字段完全不一致
（部分子集有content/organization/word_choice/sentence_fluency/conventions，
部分子集只有rater1_trait1~6，部分子集完全没有trait标注），要做成规范的多任务
学习需要额外的掩码损失设计，属于Day3/4的增量工作，本轮没有做。这里的
`trait_scores`是从整体分复制出来的占位值，不是单独训练出来的分项预测，
文档和代码里都要如实说明这一点，不能当成"已完成的多头训练"来汇报。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import torch

from src.training.common import load_score_ranges

FINETUNED_DIR = Path("models/essay-scorer-finetuned/v1")
CUSTOM_DIR = Path("models/essay-scorer-custom/v1")


class EssayScorer:
    def __init__(self, device: Optional[str] = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.score_ranges = load_score_ranges()
        self._finetuned = None
        self._finetuned_tokenizer = None
        self._custom = None
        self._custom_vocab = None
        self._custom_config = None

    def _load_finetuned(self):
        if self._finetuned is not None:
            return
        from transformers import AutoTokenizer

        from src.training.train_finetuned import ScorerModel

        with open(FINETUNED_DIR / "training_log.json", "r", encoding="utf-8") as f:
            log = json.load(f)
        model_name = log["model_name"]
        model = ScorerModel(model_name)
        model.load_state_dict(torch.load(FINETUNED_DIR / "pytorch_model.bin", map_location=self.device))
        model.to(self.device).eval()
        self._finetuned = model
        self._finetuned_tokenizer = AutoTokenizer.from_pretrained(FINETUNED_DIR)
        self._finetuned_max_length = log["args"]["max_length"]

    def _load_custom(self):
        if self._custom is not None:
            return
        from src.training.train_custom import BiLSTMAttentionScorer, encode

        with open(CUSTOM_DIR / "vocab.json", "r", encoding="utf-8") as f:
            self._custom_vocab = json.load(f)
        with open(CUSTOM_DIR / "model_config.json", "r", encoding="utf-8") as f:
            self._custom_config = json.load(f)
        model = BiLSTMAttentionScorer(
            self._custom_config["vocab_size"], self._custom_config["embed_dim"], self._custom_config["hidden_dim"]
        )
        model.load_state_dict(torch.load(CUSTOM_DIR / "pytorch_model.bin", map_location=self.device))
        model.to(self.device).eval()
        self._custom = model
        self._custom_encode = encode

    def _denormalize(self, score_norm: float, essay_set: int) -> float:
        r = self.score_ranges[int(essay_set)]
        raw = score_norm * (r["max"] - r["min"]) + r["min"]
        return float(min(max(raw, r["min"]), r["max"]))

    @torch.no_grad()
    def predict(self, essay_text: str, essay_set: int) -> dict:
        """返回{"score": 原始量纲的整体分, "score_norm": 0-1分数,
        "traits": {content/organization/language占位值}, "source": "ensemble"}。
        """
        scores_norm = []

        if FINETUNED_DIR.exists():
            self._load_finetuned()
            enc = self._finetuned_tokenizer(
                essay_text, truncation=True, max_length=self._finetuned_max_length,
                padding="max_length", return_tensors="pt",
            )
            pred = self._finetuned(enc["input_ids"].to(self.device), enc["attention_mask"].to(self.device))
            scores_norm.append(float(pred.item()))

        if CUSTOM_DIR.exists():
            self._load_custom()
            ids = self._custom_encode(essay_text, self._custom_vocab, self._custom_config["max_length"])
            input_ids = torch.tensor([ids], dtype=torch.long).to(self.device)
            pred = self._custom(input_ids)
            scores_norm.append(float(pred.item()))

        if not scores_norm:
            raise RuntimeError(
                "两条评分模型都没有训练好的权重（models/essay-scorer-finetuned/v1 和 "
                "models/essay-scorer-custom/v1 都不存在），请先跑 src/training/ 下的训练脚本。"
            )

        avg_norm = sum(scores_norm) / len(scores_norm)
        score = self._denormalize(avg_norm, essay_set)

        return {
            "score": score,
            "score_norm": avg_norm,
            # 占位：三个维度目前都是整体分的复制，不是分别训练出来的分项预测，见本文件顶部说明
            "traits": {"content": avg_norm, "organization": avg_norm, "language": avg_norm},
            "source": "ensemble" if len(scores_norm) == 2 else ("finetuned" if FINETUNED_DIR.exists() else "custom"),
        }
