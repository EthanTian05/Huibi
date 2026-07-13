"""Day1手动冒烟测试：只测不依赖langchain/langgraph的部分（intake校验、
评分占位启发式、SQLite读写），因为当前开发环境pip被网络环境挡住装不了包
（见Docs/Progress.md和CLAUDE.md「环境信息」），这部分先用纯标准库验证跑通。

完整链路（含Graph编排、LLM生成）需要在能pip install的环境里跑
`streamlit run app.py`手动验证。

用法：
    python scripts/smoke_test_nodes.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from src.agents import nodes
from src.storage import db


def test_intake_validator():
    short_state = {"essay_text": "too short"}
    result = nodes.intake_validator_node(short_state)
    assert result["is_valid"] is False, "过短作文应该被拒绝"
    print("intake_validator（过短）OK:", result["reject_reason"])

    long_text = " ".join(["word"] * 50)
    normal_state = {"essay_text": long_text}
    result = nodes.intake_validator_node(normal_state)
    assert result["is_valid"] is True
    print("intake_validator（正常长度）OK")


def test_scoring_tool_stub():
    state = {"essay_text": " ".join(["word"] * 200)}
    result = nodes.scoring_tool_node(state)
    assert 0.0 <= result["quant_score"] <= 1.0
    assert set(result["trait_scores"].keys()) == {"content", "organization", "language"}
    print("scoring_tool_node（占位启发式）OK:", result["quant_score"])


def test_grammar_check_stub():
    result = nodes.grammar_check_node({"essay_text": "anything"})
    assert result["grammar_errors"] == []
    print("grammar_check_node（占位）OK")


def test_db_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        state = {
            "user_id": "test_user",
            "essay_prompt_id": 1,
            "quant_score": 0.75,
            "trait_scores": {"content": 0.8, "organization": 0.7, "language": 0.75},
            "qualitative_feedback": "test feedback",
            "revision_plan": "test plan",
        }
        db.save_submission(state, db_path=db_path)
        db.save_submission({**state, "quant_score": 0.85}, db_path=db_path)

        history = db.get_user_history("test_user", db_path=db_path)
        assert len(history) == 2, f"应该有2条记录，实际{len(history)}条"
        assert history[0]["quant_score"] == 0.75
        assert history[1]["quant_score"] == 0.85
        assert history[0]["trait_scores"]["content"] == 0.8
        print("db.save_submission / get_user_history 往返测试 OK")


if __name__ == "__main__":
    test_intake_validator()
    test_scoring_tool_stub()
    test_grammar_check_stub()
    test_db_roundtrip()
    print("\n全部Day1无依赖冒烟测试通过。")
