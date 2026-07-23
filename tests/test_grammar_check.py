"""GrammarCheckNode：本地正则规则库检测（LanguageTool公共API是软性网络依赖，
调用失败/超时时静默返回空列表，见src/agents/grammar_tools.py，不会让下面
这些断言变得脆弱——它们只依赖本地规则库一定能检测到的错误类型）。"""
from src.agents import nodes


def test_clean_sentence_has_no_errors():
    result = nodes.grammar_check_node({"essay_text": "This is a clean sentence with no issues."})
    assert result["grammar_errors"] == []


def test_detects_common_error_types():
    text = "i recieve good grades, but i should of studied more. This is is a test."
    result = nodes.grammar_check_node({"essay_text": text})
    types = {e["type"] for e in result["grammar_errors"]}
    assert "spelling" in types
    assert "modal_of" in types
    assert "repeated_word" in types
    assert "lowercase_i" in types


def test_errors_are_sorted_by_position():
    text = "i recieve good grades, but i should of studied more."
    result = nodes.grammar_check_node({"essay_text": text})
    positions = [e["position"][0] for e in result["grammar_errors"]]
    assert positions == sorted(positions)
