"""EDA脚本，对应Docs/02-数据集与数据处理方案.md「数据分析与可视化」一节。

用法：
    python -m src.data_pipeline.eda
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

INPUT_PATH = Path("data/processed/essays_clean.csv")
OUTPUT_DIR = Path("data/processed/eda")

# 默认字体（DejaVu Sans）不含中文字形，图里的中文标题/坐标轴会变成方块。
# 按顺序尝试几个常见的中文字体，找到就用；一个都没有就保留默认字体
# （英文能正常显示，只是中文部分会缺字形，不阻塞整个脚本）。
_CJK_FONT_CANDIDATES = [
    "Noto Sans CJK SC",
    "Noto Sans CJK JP",
    "WenQuanYi Zen Hei",
    "SimHei",
    "Microsoft YaHei",
    "PingFang SC",
]
for _font in _CJK_FONT_CANDIDATES:
    if any(_font.lower() in f.name.lower() for f in matplotlib.font_manager.fontManager.ttflist):
        matplotlib.rcParams["font.sans-serif"] = [_font]
        matplotlib.rcParams["axes.unicode_minus"] = False
        break


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"找不到{INPUT_PATH}，请先运行 python -m src.data_pipeline.clean")

    df = pd.read_csv(INPUT_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 各essay_set的作文数量分布
    fig, ax = plt.subplots()
    df["essay_set"].value_counts().sort_index().plot(kind="bar", ax=ax)
    ax.set_title("各essay_set的作文数量")
    ax.set_xlabel("essay_set")
    ax.set_ylabel("数量")
    fig.savefig(OUTPUT_DIR / "essay_count_by_set.png", bbox_inches="tight")
    plt.close(fig)

    # 2. 各essay_set的评分分布（箱线图，不同essay_set分值范围不同，不能混在一起看）
    fig, ax = plt.subplots()
    df.boxplot(column="domain1_score", by="essay_set", ax=ax)
    ax.set_title("各essay_set的评分分布")
    plt.suptitle("")
    fig.savefig(OUTPUT_DIR / "score_boxplot_by_set.png", bbox_inches="tight")
    plt.close(fig)

    # 3. 作文长度 vs 评分散点图
    fig, ax = plt.subplots()
    ax.scatter(df["word_count"], df["domain1_score"], alpha=0.3, s=8)
    ax.set_xlabel("作文词数")
    ax.set_ylabel("评分（原始量纲，跨essay_set不可比）")
    ax.set_title("作文长度与评分的关系")
    fig.savefig(OUTPUT_DIR / "length_vs_score.png", bbox_inches="tight")
    plt.close(fig)

    print(f"EDA图表已保存到 {OUTPUT_DIR}")
    print(df.groupby("essay_set")["domain1_score"].describe())


if __name__ == "__main__":
    main()
