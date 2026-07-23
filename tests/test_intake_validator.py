"""IntakeValidatorNode：作文长度校验，零依赖（只用到stdlib）。"""
from src.agents import nodes


def test_rejects_too_short():
    result = nodes.intake_validator_node({"essay_text": "too short"})
    assert result["is_valid"] is False
    assert "至少需要" in result["reject_reason"]


def test_rejects_too_long():
    text = " ".join(["word"] * (nodes.MAX_WORDS + 1))
    result = nodes.intake_validator_node({"essay_text": text})
    assert result["is_valid"] is False
    assert "请控制在" in result["reject_reason"]


def test_accepts_boundary_min_words():
    text = " ".join(["word"] * nodes.MIN_WORDS)
    result = nodes.intake_validator_node({"essay_text": text})
    assert result["is_valid"] is True
    assert result["reject_reason"] is None


def test_accepts_boundary_max_words():
    text = " ".join(["word"] * nodes.MAX_WORDS)
    result = nodes.intake_validator_node({"essay_text": text})
    assert result["is_valid"] is True
