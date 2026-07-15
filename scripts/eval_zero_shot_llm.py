"""Day3 A：LLM"零样本直接打分" vs 我们微调/自建评分模型的QWK对比。

背景：项目的核心设计决策之一是"评分必须来自小组自己训练的模型，不能直接
调用大模型API打分"（见CLAUDE.md"不要重新踩的坑"第1条）。这个脚本用真实
DeepSeek调用，让大模型在完全不训练、只凭prompt的情况下直接给作文打分，
和`models/essay-scorer-*/v1/training_log.json`里记录的真实微调/自建模型
测试集QWK做对比，用真实数据支撑这个设计决策，而不是空口白话。

不依赖langchain（本地开发环境pip装不了langchain-openai），直接用标准库
urllib调用OpenAI兼容的Chat Completions接口，写法参考`scripts/check_llm_key.py`。
也不依赖sklearn（本地没装），QWK用numpy手写实现。

采样范围：8个essay_set各随机采样10条（共80条，固定随机种子42），不是
测试集全量评估（1288+条全量跑DeepSeek成本/时间过高，不适合4天工期），
如实在结果里标注"抽样评估"，答辩时不要说成是全量测试集结果。

用法：
    python scripts/eval_zero_shot_llm.py [--n-per-set 10] [--test-csv path]

前置：test.csv不在本地仓库里（gitignore，训练服务器上生成），需要先从
retinascope-server上scp下来，或者自己跑一遍preprocess.py生成。
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
SCORE_RANGES_PATH = REPO_ROOT / "data/processed/score_ranges.json"
OUTPUT_PATH = REPO_ROOT / "models/zero_shot_llm_eval.json"

SCORE_PROMPT = """你是一位资深英语写作评分员，正在给ASAP-AES数据集的essay_set {essay_set}评分。
官方评分范围是{min_score}到{max_score}分（整数，闭区间）。
请只根据这篇作文本身的写作质量（内容、结构、语言）给出一个整数分数，不需要输出评分理由。

作文原文：
{essay_text}

严格按下面这一行格式输出，不要有其他内容：
SCORE: <一个{min_score}到{max_score}之间的整数>"""


def load_dotenv(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def call_chat_completions(base_url: str, api_key: str, model: str, prompt: str, max_tokens: int = 1024) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def parse_score(content: str, min_score: int, max_score: int) -> int | None:
    m = re.search(r"SCORE:\s*(-?\d+)", content)
    if not m:
        nums = re.findall(r"-?\d+", content)
        if not nums:
            return None
        m_value = int(nums[-1])
    else:
        m_value = int(m.group(1))
    return max(min_score, min(max_score, m_value))


def quadratic_weighted_kappa(y_true: list[int], y_pred: list[int], min_rating: int, max_rating: int) -> float:
    """标准QWK实现（不依赖sklearn，本地开发环境没装sklearn，见CLAUDE.md环境信息）。"""
    n = max_rating - min_rating + 1
    y_true_idx = [t - min_rating for t in y_true]
    y_pred_idx = [p - min_rating for p in y_pred]

    O = np.zeros((n, n))
    for t, p in zip(y_true_idx, y_pred_idx):
        O[t, p] += 1

    w = np.fromfunction(lambda i, j: ((i - j) ** 2) / ((n - 1) ** 2 if n > 1 else 1), (n, n))

    act_hist = np.bincount(y_true_idx, minlength=n).astype(float)
    pred_hist = np.bincount(y_pred_idx, minlength=n).astype(float)
    E = np.outer(act_hist, pred_hist)
    E = E / E.sum() * O.sum() if E.sum() > 0 else E

    num = (w * O).sum()
    den = (w * E).sum()
    return float(1 - num / den) if den != 0 else 1.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-per-set", type=int, default=10)
    parser.add_argument("--test-csv", type=str, default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    env = {**__import__("os").environ, **load_dotenv(REPO_ROOT / ".env")}
    api_key = env.get("DEEPSEEK_API_KEY")
    base_url = env.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = env.get("DEEPSEEK_MODEL_NAME", "deepseek-chat")
    if not api_key or api_key.startswith("your_"):
        raise RuntimeError("DEEPSEEK_API_KEY未配置，检查.env")

    test_csv = Path(args.test_csv) if args.test_csv else None
    if test_csv is None:
        candidates = [
            REPO_ROOT / "data/processed/test.csv",
            Path.home() / "test.csv",
        ]
        test_csv = next((c for c in candidates if c.exists()), None)
    if test_csv is None or not test_csv.exists():
        raise FileNotFoundError(
            "找不到test.csv，本地仓库gitignore了这个文件（训练服务器生成的）。"
            "先从retinascope-server scp下来，或用--test-csv指定路径。"
        )

    with open(SCORE_RANGES_PATH, "r", encoding="utf-8") as f:
        score_ranges = {int(k): v for k, v in json.load(f).items()}

    df = pd.read_csv(test_csv)
    sample = (
        df.groupby("essay_set", group_keys=False)[df.columns.tolist()]
        .apply(lambda g: g.sample(n=min(args.n_per_set, len(g)), random_state=args.seed))
        .reset_index(drop=True)
    )
    print(f"抽样{len(sample)}条（每个essay_set最多{args.n_per_set}条），开始调用{model}零样本打分...")

    y_true_by_set: dict[int, list[int]] = {}
    y_pred_by_set: dict[int, list[int]] = {}
    failures = 0

    for i, row in sample.iterrows():
        essay_set = int(row["essay_set"])
        r = score_ranges[essay_set]
        prompt = SCORE_PROMPT.format(
            essay_set=essay_set, min_score=r["min"], max_score=r["max"], essay_text=row["essay"],
        )
        try:
            content = call_chat_completions(base_url, api_key, model, prompt)
            pred = parse_score(content, r["min"], r["max"])
        except urllib.error.HTTPError as e:
            print(f"[{i}] HTTP错误: {e.code}, essay_set={essay_set}")
            pred = None
        except Exception as e:
            print(f"[{i}] 调用失败: {type(e).__name__}: {e}")
            pred = None

        if pred is None:
            failures += 1
            continue

        y_true_by_set.setdefault(essay_set, []).append(int(row["domain1_score"]))
        y_pred_by_set.setdefault(essay_set, []).append(pred)
        print(f"[{i+1}/{len(sample)}] essay_set={essay_set} true={int(row['domain1_score'])} llm_zero_shot={pred}")
        time.sleep(0.3)

    per_set_qwk = {}
    for essay_set, y_true in y_true_by_set.items():
        y_pred = y_pred_by_set[essay_set]
        r = score_ranges[essay_set]
        per_set_qwk[essay_set] = quadratic_weighted_kappa(y_true, y_pred, r["min"], r["max"])

    macro_qwk = float(np.mean(list(per_set_qwk.values()))) if per_set_qwk else float("nan")

    result = {
        "method": "llm_zero_shot_prompting",
        "model": model,
        "n_per_set": args.n_per_set,
        "n_total_sampled": len(sample),
        "n_failures": failures,
        "seed": args.seed,
        "per_set_qwk": {str(k): v for k, v in sorted(per_set_qwk.items())},
        "macro_qwk": macro_qwk,
        "comparison": {
            "finetuned_distilbert_test_qwk": 0.6931410426487992,
            "custom_bilstm_test_qwk": 0.6224375713005985,
        },
    }
    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n=== 结果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n已保存到 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
