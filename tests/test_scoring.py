"""official_rubrics.py：LLM返回的rubric_scores按考试类型转换成对照分/展示分，
零依赖（只用到stdlib的json/math），不涉及真实LLM调用。"""
import pytest

from src.exam_types import GENERAL, IELTS, IELTS_TASK1, TOEFL
from src.official_rubrics import normalize_rubric_result, parse_llm_json


def test_ielts_task2_averages_four_bands():
    result = normalize_rubric_result(
        IELTS,
        {"rubric_scores": {"task_response": 7, "coherence_cohesion": 6,
                            "lexical_resource": 7, "grammar_accuracy": 5}},
    )
    assert result["primary_score"] == 6.5
    assert result["primary_max"] == 9.0
    assert result["primary_label"] == "IELTS Writing Task 2 标准对照 Band（0–9）"


def test_ielts_task1_uses_task_achievement_key():
    result = normalize_rubric_result(
        IELTS,
        {"rubric_scores": {"task_achievement": 6, "coherence_cohesion": 7,
                            "lexical_resource": 6, "grammar_accuracy": 7}},
        exam_subtype=IELTS_TASK1,
    )
    assert result["primary_score"] == 6.5
    assert result["primary_label"] == "IELTS Writing Task 1 标准对照 Band（0–9）"


def test_toefl_single_task_score():
    result = normalize_rubric_result(TOEFL, {"rubric_scores": {"task_score": 4}})
    assert result["primary_score"] == 4
    assert result["primary_max"] == 5.0


def test_general_sums_four_dimensions_to_100():
    result = normalize_rubric_result(
        GENERAL,
        {"rubric_scores": {"content_score": 20, "organization_score": 18,
                            "language_score": 19, "grammar_score": 15}},
    )
    assert result["primary_score"] == 72
    assert result["primary_max"] == 100.0
    assert len(result["official_rubric_scores"]) == 4


def test_missing_required_key_raises():
    with pytest.raises(ValueError, match="缺少字段"):
        normalize_rubric_result(TOEFL, {"rubric_scores": {}})


def test_scores_are_clamped_to_valid_range():
    # LLM偶尔会给出超出量表范围的值（比如GENERAL给了30分，量表上限是25），
    # normalize必须夹到合法区间，不能原样透传一个不可能出现在真实量表里的分数。
    result = normalize_rubric_result(
        GENERAL,
        {"rubric_scores": {"content_score": 30, "organization_score": -5,
                            "language_score": 19, "grammar_score": 15}},
    )
    assert result["official_rubric_scores"]["内容与任务完成"] == 25
    assert result["official_rubric_scores"]["结构与衔接"] == 0


def test_parse_llm_json_repairs_surrounding_text():
    # 真实LLM响应偶尔会在JSON前后带说明文字，parse_llm_json需要能提取出中间
    # 的合法JSON部分，不能因为多余文字直接判定解析失败。
    raw = 'here is the result:\n{"rubric_scores":{"task_score":2}}\nhope this helps'
    parsed = parse_llm_json(raw)
    assert parsed["rubric_scores"]["task_score"] == 2


def test_parse_llm_json_tolerates_unescaped_newlines_in_strings():
    raw = '{"rubric_scores":{"task_score":2},"feedback_markdown":"line one\nline two"}'
    parsed = parse_llm_json(raw)
    assert "line two" in parsed["feedback_markdown"]
