"""训练/评估共用的工具：QWK指标计算、分数反归一化，对应
Docs/03-模型训练与微调方案.md「训练配置」里"QWK"评估指标的说明。

ASAP-AES官方比赛用的就是QWK（Quadratic Weighted Kappa），且是"每个essay_set
分别算一次QWK，再取平均"，不是把所有essay_set的分数混在一起算——因为不同
essay_set的分值范围、评分粒度完全不同，混在一起算QWK没有意义。这里的
`macro_qwk`函数就是照这个口径实现的。
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import cohen_kappa_score

SCORE_RANGES_PATH = Path("data/processed/score_ranges.json")


def load_score_ranges() -> dict:
    with open(SCORE_RANGES_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


def denormalize(score_norm: np.ndarray, essay_set: np.ndarray, score_ranges: dict) -> np.ndarray:
    """把模型输出的[0,1]分数按各自essay_set的(min,max)反归一化回原始整数量纲。"""
    out = np.zeros_like(score_norm, dtype=float)
    for i, (s, es) in enumerate(zip(score_norm, essay_set)):
        r = score_ranges[int(es)]
        out[i] = s * (r["max"] - r["min"]) + r["min"]
    return np.round(np.clip(out, [score_ranges[int(es)]["min"] for es in essay_set],
                             [score_ranges[int(es)]["max"] for es in essay_set])).astype(int)


def macro_qwk(pred_score_norm: np.ndarray, true_domain1_score: np.ndarray, essay_set: np.ndarray,
              score_ranges: dict) -> tuple[float, dict]:
    """按essay_set分别算QWK，再宏平均。返回(平均QWK, 每个essay_set的QWK字典)。"""
    pred_original = denormalize(pred_score_norm, essay_set, score_ranges)
    per_set_qwk = {}
    for es in sorted(set(essay_set.tolist())):
        mask = essay_set == es
        if mask.sum() < 2:
            continue
        qwk = cohen_kappa_score(true_domain1_score[mask], pred_original[mask], weights="quadratic")
        per_set_qwk[int(es)] = float(qwk)
    avg_qwk = float(np.mean(list(per_set_qwk.values()))) if per_set_qwk else float("nan")
    return avg_qwk, per_set_qwk
