"""认证指定用户后，批量导入JSON题目/作文并走完整LangGraph批改链路。

密码只从环境变量读取，避免写入测试文件和命令行参数：
    $env:HUIBI_BATCH_PASSWORD="..."
    python scripts/batch_review.py --username mcr
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.exam_types import EXAM_TYPE_CONFIG
from src.storage import db


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--input", type=Path, default=Path("data/test/official_rubric_batch.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/official_rubric_batch_result.json"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--case-id", action="append", help="只运行指定case_id，可重复传入")
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def load_cases(path: Path) -> list[dict]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("批量输入必须是非空JSON数组")
    required = {"case_id", "exam_type", "essay_topic", "essay_text"}
    seen = set()
    for index, case in enumerate(cases, 1):
        missing = required - set(case)
        if missing:
            raise ValueError(f"第{index}条缺少字段: {sorted(missing)}")
        if case["case_id"] in seen:
            raise ValueError(f"case_id重复: {case['case_id']}")
        seen.add(case["case_id"])
        if case["exam_type"] not in EXAM_TYPE_CONFIG:
            raise ValueError(f"不支持的考试类型: {case['exam_type']}")
        if len(case["essay_text"].split()) < 20:
            raise ValueError(f"{case['case_id']}作文少于20词")
    return cases


def main() -> int:
    args = parse_args()
    os.chdir(PROJECT_ROOT)
    cases = load_cases(args.input)
    if args.case_id:
        wanted = set(args.case_id)
        cases = [case for case in cases if case["case_id"] in wanted]
        missing = wanted - {case["case_id"] for case in cases}
        if missing:
            raise ValueError(f"未找到case_id: {sorted(missing)}")
    if args.limit:
        cases = cases[: args.limit]

    password = os.environ.get("HUIBI_BATCH_PASSWORD", "")
    if not password or not db.verify_user(args.username, password):
        print("认证失败：请确认用户名及HUIBI_BATCH_PASSWORD环境变量。", file=sys.stderr)
        return 2
    print(f"认证通过：{args.username}；输入校验通过，共{len(cases)}条。")
    if args.validate_only:
        return 0

    from src.agents.graph import build_graph

    graph = build_graph()
    existing_count = len(db.get_user_history(args.username))
    results = []
    for index, case in enumerate(cases, 1):
        payload = {
            "user_id": args.username,
            "essay_text": case["essay_text"],
            "exam_type": case["exam_type"],
            "exam_subtype": case.get("exam_subtype"),
            "essay_topic": case["essay_topic"],
            "history_summary": {"submission_count": existing_count + index - 1},
        }
        print(f"[{index}/{len(cases)}] {case['case_id']} · {case['exam_type']} ...", flush=True)
        try:
            result = graph.invoke(payload)
            results.append({
                "case_id": case["case_id"],
                "exam_type": case["exam_type"],
                "word_count": len(case["essay_text"].split()),
                "is_valid": result.get("is_valid"),
                "score_source": result.get("score_source"),
                "primary_score": result.get("primary_score"),
                "primary_max": result.get("primary_max"),
                "primary_label": result.get("primary_label"),
                "secondary_score": result.get("secondary_score"),
                "secondary_max": result.get("secondary_max"),
                "score_details": result.get("score_details", {}),
                "rubric_score": result.get("official_rubric_score"),
                "rubric_max": result.get("official_rubric_max"),
                "rubric_label": result.get("official_rubric_label"),
                "rubric_dimensions": result.get("official_rubric_scores", {}),
                "feedback": result.get("qualitative_feedback", ""),
                "revision_plan": result.get("revision_plan", ""),
                "parse_error": result.get("rubric_parse_error"),
                "score_error": result.get("score_error"),
            })
        except Exception as exc:  # 单条失败不应阻塞整批，错误写入报告供复核
            results.append({"case_id": case["case_id"], "exam_type": case["exam_type"], "error": str(exc)})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "username": args.username,
        "case_count": len(cases),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    failures = [row for row in results if row.get("error") or row.get("parse_error") or row.get("score_error")]
    print(f"完成：{len(results) - len(failures)}/{len(results)}条成功；报告：{args.output}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
