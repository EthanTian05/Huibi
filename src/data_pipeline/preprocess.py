"""数据预处理：分数归一化、训练/验证/测试划分，对应Docs/02号文档「数据预处理」
一节和Docs/03号文档「225原则」一节里提到的按essay_set分层8:1:1划分。

用法：
    python -m src.data_pipeline.preprocess
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

INPUT_PATH = Path("data/processed/essays_clean.csv")
OUTPUT_DIR = Path("data/processed")
SCORE_RANGES_PATH = OUTPUT_DIR / "score_ranges.json"


def normalize_scores(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """按essay_set分别把domain1_score归一化到[0,1]，因为各essay_set的分值范围不同。
    同时把每个essay_set的(min,max)存下来，推理/评估时要用它把模型输出的0-1分数
    反归一化回原始量纲（QWK是在原始整数评分上算的，不能直接用0-1分数算）。
    """
    df = df.copy()
    ranges = df.groupby("essay_set")["domain1_score"].agg(["min", "max"]).to_dict("index")
    ranges = {int(k): {"min": int(v["min"]), "max": int(v["max"])} for k, v in ranges.items()}
    df["score_norm"] = df.groupby("essay_set")["domain1_score"].transform(
        lambda s: (s - s.min()) / (s.max() - s.min())
    )
    return df, ranges


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"找不到{INPUT_PATH}，请先运行 python -m src.data_pipeline.clean")

    df = pd.read_csv(INPUT_PATH)
    df, score_ranges = normalize_scores(df)

    train_df, temp_df = train_test_split(
        df, test_size=0.2, stratify=df["essay_set"], random_state=42
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, stratify=temp_df["essay_set"], random_state=42
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(OUTPUT_DIR / "train.csv", index=False)
    val_df.to_csv(OUTPUT_DIR / "val.csv", index=False)
    test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)
    with open(SCORE_RANGES_PATH, "w", encoding="utf-8") as f:
        json.dump(score_ranges, f, ensure_ascii=False, indent=2)

    print(f"划分完成：train={len(train_df)}, val={len(val_df)}, test={len(test_df)}（按essay_set分层8:1:1）")
    print(f"每个essay_set的原始分数区间已保存到 {SCORE_RANGES_PATH}（QWK评估时反归一化要用）")


if __name__ == "__main__":
    main()
