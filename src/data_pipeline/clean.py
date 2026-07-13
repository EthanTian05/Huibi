"""ASAP-AES数据清洗脚本，对应Docs/02-数据集与数据处理方案.md「数据清洗」一节。

前置条件：需要先手动从Kaggle ASAP (Automated Student Assessment Prize) 比赛页面
下载数据集（见Docs/00-项目总览.md「参考资料」），Kaggle要求账号登录/接受比赛协议，
这一步无法自动化，需要A手动完成。下载后把官方发布的`training_set_rel3.tsv`
放到 data/raw/ 目录下。

用法：
    python -m src.data_pipeline.clean
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/training_set_rel3.tsv")
OUTPUT_PATH = Path("data/processed/essays_clean.csv")

MIN_WORDS = 20
ANONYMIZED_TOKEN_PATTERN = re.compile(
    r"@(PERSON|ORGANIZATION|LOCATION|DATE|TIME|MONEY|PERCENT|CAPS|NUM)\d*"
)


def clean_text(text: str) -> str:
    """还原ASAP-AES里的匿名占位符，规整常见的Windows-1252特殊字符。"""
    text = ANONYMIZED_TOKEN_PATTERN.sub("[NAME]", text)
    text = (
        text.replace("\x91", "'")
        .replace("\x92", "'")
        .replace("\x93", '"')
        .replace("\x94", '"')
    )
    return text.strip()


def main():
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"找不到{RAW_PATH}，请先从Kaggle ASAP-AES比赛页面手动下载数据集，"
            f"把training_set_rel3.tsv放到这个路径（见Docs/00-项目总览.md「参考资料」）。"
        )

    df = pd.read_csv(RAW_PATH, sep="\t", encoding="latin-1")

    before = len(df)
    df = df.dropna(subset=["domain1_score"])
    df["essay"] = df["essay"].astype(str).map(clean_text)
    df["word_count"] = df["essay"].str.split().map(len)
    df = df[df["word_count"] >= MIN_WORDS]
    df = df.drop_duplicates(subset=["essay_id"])
    after = len(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    keep_cols = ["essay_id", "essay_set", "essay", "word_count", "domain1_score"]
    trait_cols = [c for c in df.columns if c not in keep_cols and "score" in c.lower()]
    df[keep_cols + trait_cols].to_csv(OUTPUT_PATH, index=False)

    print(f"清洗完成：{before} -> {after} 条（剔除了{before - after}条空评分/过短/重复样本）")
    print(f"已保存到 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
