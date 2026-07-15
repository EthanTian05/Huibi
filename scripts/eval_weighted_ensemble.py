"""用验证集选择A/B非等权融合权重，再在固定的80条测试样本上报告结果。

不能用测试样本本身挑权重，否则会产生测试集泄漏。权重定义为：
    score_norm = w * score_A + (1 - w) * score_B
其中A是微调DistilBERT、B是自建BiLSTM+Attention。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from src.training.common import load_score_ranges, macro_qwk
from src.training.essay_scorer import EssayScorer


def predict_both(scorer: EssayScorer, df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """对同一批文本分别得到A、B的归一化预测。"""
    scorer._load_finetuned()
    scorer._load_custom()
    preds_a, preds_b = [], []

    with torch.no_grad():
        for _, row in df.iterrows():
            text = row["essay"]
            enc = scorer._finetuned_tokenizer(
                text, truncation=True, max_length=scorer._finetuned_max_length,
                padding="max_length", return_tensors="pt",
            )
            pred_a = scorer._finetuned(
                enc["input_ids"].to(scorer.device), enc["attention_mask"].to(scorer.device)
            )
            ids = scorer._custom_encode(text, scorer._custom_vocab, scorer._custom_config["max_length"])
            pred_b = scorer._custom(torch.tensor([ids], dtype=torch.long).to(scorer.device))
            preds_a.append(float(pred_a.item()))
            preds_b.append(float(pred_b.item()))
    return np.array(preds_a), np.array(preds_b)


def qwk_for_weight(preds_a, preds_b, df: pd.DataFrame, score_ranges: dict, weight_a: float) -> tuple[float, dict]:
    preds = weight_a * preds_a + (1.0 - weight_a) * preds_b
    return macro_qwk(preds, df["domain1_score"].to_numpy(), df["essay_set"].to_numpy(), score_ranges)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--val-csv", default="data/processed/val.csv")
    parser.add_argument("--test-csv", default="data/processed/test.csv")
    parser.add_argument("--sample-ids-json", required=True)
    parser.add_argument("--output", default="models/weighted_ensemble_eval.json")
    parser.add_argument("--step", type=float, default=0.05)
    args = parser.parse_args()

    score_ranges = load_score_ranges()
    scorer = EssayScorer()
    val_df = pd.read_csv(args.val_csv)
    test_df = pd.read_csv(args.test_csv)
    sample_ids = json.loads(Path(args.sample_ids_json).read_text(encoding="utf-8"))
    ids = [row["essay_id"] for row in sample_ids]
    test_sample = test_df[test_df["essay_id"].isin(ids)].copy()
    assert len(test_sample) == len(ids), "测试集样本数量与sample_ids不一致"

    val_a, val_b = predict_both(scorer, val_df)
    weights = np.round(np.arange(0.0, 1.0 + args.step / 2, args.step), 6)
    candidates = []
    for weight_a in weights:
        qwk, _ = qwk_for_weight(val_a, val_b, val_df, score_ranges, float(weight_a))
        candidates.append({"weight_a": float(weight_a), "weight_b": float(1 - weight_a), "val_macro_qwk": qwk})
    best = max(candidates, key=lambda row: row["val_macro_qwk"])

    test_a, test_b = predict_both(scorer, test_sample)
    test_qwk, test_per_set = qwk_for_weight(test_a, test_b, test_sample, score_ranges, best["weight_a"])
    equal_qwk, _ = qwk_for_weight(test_a, test_b, test_sample, score_ranges, 0.5)
    result = {
        "selection_protocol": "在验证集网格搜索权重；固定后仅在80条测试样本上评估",
        "n_validation": int(len(val_df)),
        "n_test_sample": int(len(test_sample)),
        "weight_grid_step": args.step,
        "validation_candidates": candidates,
        "selected_weight": best,
        "test_macro_qwk": test_qwk,
        "test_per_set_qwk": {str(k): v for k, v in sorted(test_per_set.items())},
        "test_equal_weight_macro_qwk": equal_qwk,
    }
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
