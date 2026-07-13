"""ASAP-AES数据清洗脚本，对应Docs/02-数据集与数据处理方案.md「数据清洗」一节。

两种数据来源二选一（自动探测，Kaggle官方文件优先）：
1. Kaggle官方`training_set_rel3.tsv`——需要账号登录/接受比赛协议手动下载，
   放到`data/raw/training_set_rel3.tsv`（见Docs/00-项目总览.md「参考资料」）。
2. HuggingFace镜像合并文件——不需要Kaggle账号，跑`python -m src.data_pipeline.download`
   会自动下载并生成`data/raw/asap_aes_merged.parquet`。

用法：
    python -m src.data_pipeline.clean
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

KAGGLE_RAW_PATH = Path("data/raw/training_set_rel3.tsv")
HF_MERGED_PATH = Path("data/raw/asap_aes_merged.parquet")
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


def load_raw() -> pd.DataFrame:
    if KAGGLE_RAW_PATH.exists():
        print(f"使用Kaggle官方文件: {KAGGLE_RAW_PATH}")
        return pd.read_csv(KAGGLE_RAW_PATH, sep="\t", encoding="latin-1")
    if HF_MERGED_PATH.exists():
        print(f"使用HuggingFace镜像合并文件: {HF_MERGED_PATH}")
        return pd.read_parquet(HF_MERGED_PATH)
    raise FileNotFoundError(
        f"找不到{KAGGLE_RAW_PATH}也找不到{HF_MERGED_PATH}。"
        f"要么从Kaggle ASAP-AES比赛页面手动下载training_set_rel3.tsv放到data/raw/，"
        f"要么运行 `python -m src.data_pipeline.download` 自动下载非gated的HF镜像。"
    )


def main():
    df = load_raw()

    before = len(df)
    df = df.dropna(subset=["domain1_score"])
    df["essay"] = df["essay"].astype(str).map(clean_text)
    df["word_count"] = df["essay"].str.split().map(len)
    df = df[df["word_count"] >= MIN_WORDS]
    df = df.drop_duplicates(subset=["essay_id"])
    after = len(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    keep_cols = ["essay_id", "essay_set", "essay", "word_count", "domain1_score"]
    extra_cols = [c for c in df.columns if c not in keep_cols and c != "source_repo"]
    df[keep_cols + extra_cols].to_csv(OUTPUT_PATH, index=False)

    print(f"清洗完成：{before} -> {after} 条（剔除了{before - after}条空评分/过短/重复样本）")
    print(f"已保存到 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
