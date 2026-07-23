"""Day1手动冒烟测试：只测不依赖langchain/langgraph/psycopg的部分（intake校验、
评分逻辑、语法检查），因为当前开发环境pip被网络环境挡住装不了包（见
Docs/02-Progress.md和CLAUDE.md「环境信息」），这部分先用纯标准库验证跑通。

`test_grammar_check_rules`会真实调用LanguageTool公共API（`grammar_check_node`
内部逻辑），有软性网络依赖——调用失败/超时时`languagetool_check`静默返回空
列表（见`src/agents/grammar_tools.py`），不会让测试报错，只是少测到一部分
真实场景的问题类型，断言本身没有因为网络状态而变脆弱。

**数据库读写测试不在这里**：本轮数据库从SQLite（标准库`sqlite3`）迁移到了
PostgreSQL（需要`psycopg`包+本地跑着PostgreSQL服务），`db.save_submission`/
`db.create_user`等不再是零依赖的，挪到了`scripts/e2e_graph_test.py`（那个
脚本本来就需要pip环境），不要再指望这个脚本覆盖数据库读写。

完整链路（含Graph编排、LLM生成、图片理解、数据库读写）需要在能pip install
的环境里跑`scripts/e2e_graph_test.py`或`streamlit run app.py`手动验证。

用法：
    python scripts/smoke_test_nodes.py
"""
from __future__ import annotations

from src.agents import nodes
from src.exam_types import GENERAL, IELTS, IELTS_TASK1, TOEFL
from src.official_rubrics import normalize_rubric_result, parse_llm_json


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


def test_score_policies():
    ielts = normalize_rubric_result(
        IELTS,
        {"rubric_scores": {"task_response": 7, "coherence_cohesion": 6,
                           "lexical_resource": 7, "grammar_accuracy": 5},
         "feedback_markdown": "ok"},
    )
    assert ielts["primary_score"] == 6.5
    assert normalize_rubric_result(
        TOEFL, {"rubric_scores": {"task_score": 4}, "feedback_markdown": "ok"}
    )["primary_score"] == 4
    general = normalize_rubric_result(
        GENERAL,
        {"rubric_scores": {"content_score": 20, "organization_score": 18,
                           "language_score": 19, "grammar_score": 15},
         "feedback_markdown": "ok"},
    )
    assert general["primary_score"] == 72
    assert general["primary_max"] == 100.0
    ielts_task1 = normalize_rubric_result(
        IELTS,
        {"rubric_scores": {"task_achievement": 6, "coherence_cohesion": 7,
                           "lexical_resource": 6, "grammar_accuracy": 7}},
        exam_subtype=IELTS_TASK1,
    )
    assert ielts_task1["primary_score"] == 6.5
    assert ielts_task1["primary_label"] == "IELTS Writing Task 1 标准对照 Band（0–9）"
    repaired = parse_llm_json(
        '{"rubric_scores":{"task_score":2},"feedback_markdown":"第一行\n第二行"}'
    )
    assert repaired["rubric_scores"]["task_score"] == 2
    assert "第二行" in repaired["feedback_markdown"]
    print("GENERAL/IELTS/TOEFL的LLM量表评分测试 OK")


def test_grammar_check_rules():
    clean = nodes.grammar_check_node({"essay_text": "This is a clean sentence with no issues."})
    assert clean["grammar_errors"] == [], f"不应该有误报: {clean['grammar_errors']}"

    text = "i recieve good grades, but i should of studied more. This is is a test."
    result = nodes.grammar_check_node({"essay_text": text})
    types = {e["type"] for e in result["grammar_errors"]}
    assert "spelling" in types, "应该检测出recieve拼写错误"
    assert "modal_of" in types, "应该检测出should of误用"
    assert "repeated_word" in types, "应该检测出is is重复"
    assert "lowercase_i" in types, "应该检测出小写i"
    print(f"grammar_check_node（规则库）OK: 检测到{len(result['grammar_errors'])}处问题")


if __name__ == "__main__":
    test_intake_validator()
    test_score_policies()
    test_grammar_check_rules()
    print("\n全部Day1无依赖冒烟测试通过。")
