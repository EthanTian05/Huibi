"""Day3收尾两件事，都要在装了torch/transformers/sklearn的机器上跑（本地开发
环境pip装不了这些，见CLAUDE.md「环境信息」），比如retinascope-server：

① 同批次公平对比：`scripts/eval_zero_shot_llm.py`跑的是80条抽样的零样本LLM
   打分，如果直接拿它的QWK去和`training_log.json`里"全量测试集1288+条"的
   微调/自建模型QWK比，分母不一样，不是公平对比。这里用完全相同的80条
   essay_id（由`--sample-ids-json`传入，来自本地跑`eval_zero_shot_llm.py`时
   用相同随机种子重新采样导出的essay_id列表），跑真实的`EssayScorer`
   （微调、自建、或两者融合），算出同样80条上的QWK，才能和零样本结果直接比。

② essay_set 8误差诊断：不重新训练，只是在全量测试集里单独把essay_set==8
   的例子跑一遍真实模型推理，看残差（预测-真实）的均值/方差、是否随真实分数
   系统性偏差（比如高分被压低，这是小样本+大分值范围回归任务的典型症状），
   并对比训练集里各essay_set的样本量，给"为什么这个集合QWK明显更低"一个
   有数据支撑的解释，而不是只说"数据稀疏"四个字。

用法：
    # 四组公平比较时，分别运行 finetuned / custom / ensemble 三次。
    python scripts/eval_same_sample_and_diagnose_set8.py --sample-ids-json sample_ids.json --model finetuned
    python scripts/eval_same_sample_and_diagnose_set8.py --sample-ids-json sample_ids.json --model custom
    python scripts/eval_same_sample_and_diagnose_set8.py --sample-ids-json sample_ids.json --model ensemble
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

TEST_CSV = Path("data/processed/test.csv")
TRAIN_CSV = Path("data/processed/train.csv")


def predict_with_model(scorer: EssayScorer, essay_text: str, essay_set: int, model: str) -> float:
    """返回指定评分路径的归一化预测，避免A/B/融合实验相互混用权重。"""
    if model == "ensemble":
        return scorer.predict(essay_text, essay_set)["score_norm"]

    if model == "finetuned":
        scorer._load_finetuned()
        enc = scorer._finetuned_tokenizer(
            essay_text, truncation=True, max_length=scorer._finetuned_max_length,
            padding="max_length", return_tensors="pt",
        )
        pred = scorer._finetuned(
            enc["input_ids"].to(scorer.device), enc["attention_mask"].to(scorer.device)
        )
        return float(pred.item())

    if model == "custom":
        scorer._load_custom()
        ids = scorer._custom_encode(essay_text, scorer._custom_vocab, scorer._custom_config["max_length"])
        pred = scorer._custom(torch.tensor([ids], dtype=torch.long).to(scorer.device))
        return float(pred.item())

    raise ValueError(f"未知模型模式: {model}")


def run_same_sample_comparison(scorer: EssayScorer, sample_ids_json: str, score_ranges: dict, model: str) -> dict:
    df = pd.read_csv(TEST_CSV)
    with open(sample_ids_json, "r", encoding="utf-8") as f:
        sample_ids = json.load(f)
    ids = [r["essay_id"] for r in sample_ids]

    sub = df[df["essay_id"].isin(ids)].copy()
    assert len(sub) == len(sample_ids), f"应该有{len(sample_ids)}条，实际匹配到{len(sub)}条"

    preds_norm = []
    for _, row in sub.iterrows():
        preds_norm.append(predict_with_model(scorer, row["essay"], int(row["essay_set"]), model))

    preds_norm = np.array(preds_norm)
    essay_set_arr = sub["essay_set"].to_numpy()
    true_scores = sub["domain1_score"].to_numpy()

    avg_qwk, per_set = macro_qwk(preds_norm, true_scores, essay_set_arr, score_ranges)
    method = "trained_weighted_ensemble" if model == "ensemble" else f"trained_{model}"
    return {
        "method": f"{method}_same_80_samples",
        "n_total": int(len(sub)),
        "per_set_qwk": {str(k): v for k, v in sorted(per_set.items())},
        "macro_qwk": avg_qwk,
    }


def run_set8_diagnosis(scorer: EssayScorer) -> dict:
    test_df = pd.read_csv(TEST_CSV)
    train_df = pd.read_csv(TRAIN_CSV)

    train_counts = train_df["essay_set"].value_counts().sort_index()

    set8 = test_df[test_df["essay_set"] == 8].copy()
    preds = []
    for _, row in set8.iterrows():
        result = scorer.predict(row["essay"], 8)
        preds.append(result["score"])
    preds = np.array(preds, dtype=float)
    true = set8["domain1_score"].to_numpy(dtype=float)
    residuals = preds - true

    return {
        "train_set_size_per_essay_set": {str(k): int(v) for k, v in train_counts.items()},
        "set8_n_test_examples": int(len(set8)),
        "set8_true_score_range": [int(true.min()), int(true.max())],
        "set8_true_score_mean_std": [float(true.mean()), float(true.std())],
        "set8_pred_score_mean_std": [float(preds.mean()), float(preds.std())],
        "residual_mean_bias": float(residuals.mean()),
        "residual_std": float(residuals.std()),
        "residual_vs_true_score_corr": (
            float(np.corrcoef(true, residuals)[0, 1]) if len(set8) > 1 else None
        ),
        "note": (
            "residual_vs_true_score_corr明显为负，说明真实高分被系统性低估、真实低分被"
            "系统性高估（回归模型在样本稀疏+分值范围宽的essay_set上常见的'向均值收缩'现象），"
            "train_set_size_per_essay_set可以看set8训练样本量是否确实明显少于其他集合。"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-ids-json", required=True)
    parser.add_argument("--output-dir", default="models")
    parser.add_argument("--model", choices=["finetuned", "custom", "ensemble"], default="ensemble")
    args = parser.parse_args()

    score_ranges = load_score_ranges()
    scorer = EssayScorer()

    same_sample_result = run_same_sample_comparison(scorer, args.sample_ids_json, score_ranges, args.model)
    suffix = "" if args.model == "ensemble" else f"_{args.model}"
    out1 = Path(args.output_dir) / f"same_sample_trained_eval{suffix}.json"
    out1.write_text(json.dumps(same_sample_result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=== 同批次(80条)真实模型对比 ===")
    print(json.dumps(same_sample_result, ensure_ascii=False, indent=2))
    print(f"已保存到 {out1}\n")

    diagnosis = run_set8_diagnosis(scorer)
    out2 = Path(args.output_dir) / "set8_diagnosis.json"
    out2.write_text(json.dumps(diagnosis, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=== essay_set 8 误差诊断 ===")
    print(json.dumps(diagnosis, ensure_ascii=False, indent=2))
    print(f"已保存到 {out2}")


if __name__ == "__main__":
    main()
