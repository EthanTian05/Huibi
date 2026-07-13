"""从下载好的ASAP-AES原始数据(data/raw/asap_aes_merged.parquet)里，把每个
essay_set真实的题目(prompt)和评分细则(rubrics)提取出来，生成
data/kb/rubric_essay_set_<N>.md，替换掉Day1里手写的单一占位示例
（rubric_essay_set_1.md），覆盖全部8个essay_set。

这些prompt/rubrics文本来自数据集本身（非gated的HF镜像），不是团队编造的，
但格式是原始英文，直接作为RAG检索内容使用；如果要点上加中文讲解，
可以在这个脚本生成的文件基础上人工补充（保留脚本生成的部分，追加即可）。

用法：
    python -m src.rag.build_rubric_docs
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/asap_aes_merged.parquet")
OUTPUT_DIR = Path("data/kb")


def main():
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"找不到{RAW_PATH}，请先运行 python -m src.data_pipeline.download")

    df = pd.read_parquet(RAW_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for essay_set in sorted(df["essay_set"].unique()):
        sub = df[df["essay_set"] == essay_set]
        prompt = sub["prompt"].dropna().iloc[0] if "prompt" in sub and sub["prompt"].notna().any() else None
        rubrics = sub["rubrics"].dropna().iloc[0] if "rubrics" in sub and sub["rubrics"].notna().any() else None
        score_min, score_max = int(sub["domain1_score"].min()), int(sub["domain1_score"].max())

        lines = [f"# Essay Set {essay_set} 题目与评分细则（来源：ASAP-AES原始数据集）", ""]
        lines.append(f"- 样本数：{len(sub)}")
        lines.append(f"- 原始评分区间：{score_min} ~ {score_max}")
        lines.append("")
        if prompt:
            lines.append("## 题目 (Prompt)")
            lines.append("")
            lines.append(prompt.strip())
            lines.append("")
        if rubrics:
            lines.append("## 评分细则 (Rubrics)")
            lines.append("")
            lines.append(rubrics.strip())
            lines.append("")

        out_path = OUTPUT_DIR / f"rubric_essay_set_{essay_set}.md"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"已生成 {out_path}")


if __name__ == "__main__":
    main()
