"""下载ASAP-AES数据集（不需要Kaggle账号/协议）。

Kaggle官方发布的ASAP-AES数据集需要账号登录/接受比赛协议才能下载，这一步没法
自动化。这个脚本改用HuggingFace Hub上"llm-aes"组织发布的、按essay_set切分的
非gated镜像（来自开源项目 https://github.com/Xiaochr/LLM-AES），四个子集覆盖
全部8个essay_set，字段包含essay/domain1_score/essay_set，部分子集还带rubrics/
prompt/分项trait，可以直接拼起来当作原始数据源使用。

如果你的网络访问不了huggingface.co，脚本默认通过hf-mirror.com镜像下载
（设置了HF_ENDPOINT环境变量）。如果你能正常访问Kaggle、想用官方原始文件，
直接把`training_set_rel3.tsv`放到data/raw/下即可，`clean.py`会优先用那个文件，
不需要跑这个下载脚本。

用法：
    python -m src.data_pipeline.download
"""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

import pandas as pd
from huggingface_hub import hf_hub_download

OUTPUT_PATH = Path("data/raw/asap_aes_merged.parquet")

# (HF仓库名, 该子集里essay_id是否已经有全局唯一的列)
SUBSETS = [
    "llm-aes/asappp-1-2-original",
    "llm-aes/asappp-3-6-original",
    "llm-aes/asap-7-original",
    "llm-aes/asap-8-original",
]

CORE_COLUMNS = ["essay_id", "essay_set", "essay", "domain1_score"]


def download_subset(repo_id: str) -> pd.DataFrame:
    path = hf_hub_download(repo_id=repo_id, filename="data/train-00000-of-00001.parquet", repo_type="dataset")
    df = pd.read_parquet(path)
    return df


def main():
    frames = []
    next_id = 0
    for repo_id in SUBSETS:
        print(f"下载 {repo_id} ...")
        df = download_subset(repo_id)
        if "essay_id" not in df.columns:
            df = df.copy()
            df["essay_id"] = range(next_id, next_id + len(df))
        next_id = int(df["essay_id"].max()) + 1
        df["source_repo"] = repo_id
        frames.append(df)
        print(f"  {len(df)} 条，essay_set取值: {sorted(df['essay_set'].unique().tolist())}")

    merged = pd.concat(frames, ignore_index=True, sort=False)

    missing_core = [c for c in CORE_COLUMNS if c not in merged.columns]
    if missing_core:
        raise RuntimeError(f"合并后缺少核心列: {missing_core}，检查各子集schema是否变化")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(OUTPUT_PATH, index=False)
    print(f"\n合并完成：共{len(merged)}条，覆盖essay_set: {sorted(merged['essay_set'].unique().tolist())}")
    print(f"已保存到 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
