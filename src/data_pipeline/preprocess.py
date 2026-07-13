"""数据预处理：分数归一化、训练/验证/测试划分，对应Docs/02号文档「数据预处理」
一节和Docs/03号文档「225原则」一节里提到的按essay_set分层8:1:1划分。

用法：
    python -m src.data_pipeline.preprocess
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

INPUT_PATH = Path("data/processed/essays_clean.csv")
OUTPUT_DIR = Path("data/processed")


def normalize_scores(df: pd.DataFrame) -> pd.DataFrame:
    """按essay_set分别把domain1_score归一化到[0,1]，因为各essay_set的分值范围不同。"""
    df = df.copy()
    df["score_norm"] = df.groupby("essay_set")["domain1_score"].transform(
        lambda s: (s - s.min()) / (s.max() - s.min())
    )
    return df


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"找不到{INPUT_PATH}，请先运行 python -m src.data_pipeline.clean")

    df = pd.read_csv(INPUT_PATH)
    df = normalize_scores(df)

    train_df, temp_df = train_test_split(
        df, test_size=0.2, stratify=df["essay_set"], random_state=42
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, stratify=temp_df["essay_set"], random_state=42
    )

    train_df.to_csv(OUTPUT_DIR / "train.csv", index=False)
    val_df.to_csv(OUTPUT_DIR / "val.csv", index=False)
    test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)

    print(f"划分完成：train={len(train_df)}, val={len(val_df)}, test={len(test_df)}（按essay_set分层8:1:1）")


if __name__ == "__main__":
    main()
