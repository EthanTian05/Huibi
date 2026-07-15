"""Day1端到端验证：真实调用build_graph().invoke()，包括真实的DeepSeek调用，
不是只测语法。之前在本地开发环境因为pip装不上，这个脚本没能跑起来；
现在有能pip install的服务器了，用这个脚本验证整条链路。

用法：
    PYTHONPATH=. python scripts/e2e_graph_test.py
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from src.agents.graph import build_graph

SAMPLE_ESSAY = """
Computers have become one of the most important tools in modern education and daily life.
Some people think that young students should not be allowed to use computers because it
distracts them from studying, but I believe computers actually help students learn better
if they are used correctly.

First, computers give students access to a huge amount of information. Instead of only
reading one textbook, a student can search for many sources and compare different opinions.
This makes learning more active and interesting.

Second, computers teach useful skills for the future. Many jobs today require people to
use software, write emails, or analyze data. If students start practicing these skills early,
they will be more prepared when they grow up.

Of course, computers should be used with rules. Parents and teachers should limit the time
spent on games and social media so that students still spend enough time on real studying
and outdoor activities.

In conclusion, computers are a powerful tool for education, not an enemy of it. With the
right guidance, they can make students smarter and more capable in the future.
""".strip()

TOO_SHORT_ESSAY = "Computers are good."

BOUNDARY_SHORT_ESSAY = " ".join(["word"] * 20)  # 正好20词，等于MIN_WORDS边界
BOUNDARY_LONG_ESSAY = " ".join(["word"] * 1000)  # 正好1000词，等于MAX_WORDS边界
TOO_LONG_ESSAY = " ".join(["word"] * 1001)  # 超过MAX_WORDS一词，应该被拒绝

MANY_ERRORS_ESSAY = """
i think computers is is good for students. i recieve alot of information from the internet
and i dont have no problem using it. computers should of been introduced earlier in schools
becuase they help students learn.i think every student need a computer for thier education.
""".strip()

SET8_ESSAY = """
The story begins on a quiet morning when Maria discovered an old letter hidden inside her
grandmother's writing desk. The paper was yellowed with age, and the ink had faded, but she
could still make out a few words that changed everything she thought she knew about her family.

As she read further, Maria realized the letter was written during a time of great difficulty,
when her grandmother had to make an impossible choice between staying with her family or
pursuing an opportunity that would change the course of their lives forever.

The narrative unfolds slowly, revealing layer after layer of family history that had been kept
secret for decades. Maria's journey to understand her grandmother's decision teaches her about
sacrifice, courage, and the complicated nature of love within a family.

By the end of the story, Maria comes to appreciate the strength it took for her grandmother to
make that choice, and she begins to see her own life decisions in a completely new light.
""".strip()


def _run_case(graph, name: str, essay_text: str, essay_prompt_id: int, user_id: str) -> dict:
    print(f"\n=== {name} ===")
    try:
        result = graph.invoke({"user_id": user_id, "essay_text": essay_text, "essay_prompt_id": essay_prompt_id})
        print("is_valid:", result.get("is_valid"))
        if result.get("is_valid") is False:
            print("reject_reason:", result.get("reject_reason"))
        else:
            print("quant_score:", result.get("quant_score"))
            print("trait_scores:", result.get("trait_scores"))
            print("grammar_errors数量:", len(result.get("grammar_errors", [])))
        return result
    except Exception as e:
        print(f"!!! 抛出异常: {type(e).__name__}: {e}")
        raise


def test_edge_cases(graph):
    """Day3新增：覆盖MIN/MAX_WORDS边界、语法错误密集、essay_set 8（宽分值范围）
    这几类之前没测过的边界情况，确认不会让Graph在中途抛异常崩溃。
    """
    r1 = _run_case(graph, "边界1：正好20词（MIN_WORDS边界，应通过校验）", BOUNDARY_SHORT_ESSAY, 1, "edge_user_1")
    assert r1.get("is_valid") is True, "正好20词应该通过校验"

    r2 = _run_case(graph, "边界2：正好1000词（MAX_WORDS边界，应通过校验）", BOUNDARY_LONG_ESSAY, 1, "edge_user_2")
    assert r2.get("is_valid") is True, "正好1000词应该通过校验"

    r3 = _run_case(graph, "边界3：1001词（超过MAX_WORDS，应被拒绝）", TOO_LONG_ESSAY, 1, "edge_user_3")
    assert r3.get("is_valid") is False, "1001词应该被拒绝"

    r4 = _run_case(graph, "边界4：语法错误密集的作文（grammar_check_node压力测试）", MANY_ERRORS_ESSAY, 1, "edge_user_4")
    assert r4.get("is_valid") is True
    assert len(r4.get("grammar_errors", [])) >= 5, "这篇作文应该检测出至少5处语法问题"
    assert r4["trait_scores"]["language"] < r4["trait_scores"]["content"] or r4["trait_scores"]["language"] < 0.5, \
        "语法错误密集应该拉低language分项"

    r5 = _run_case(graph, "边界5：essay_set 8（分值范围最宽0-60）", SET8_ESSAY, 8, "edge_user_5")
    assert r5.get("is_valid") is True
    assert 0 <= r5.get("quant_score", -1) <= 1, "score_norm应该在0-1之间"

    print("\n全部边界案例测试通过，Graph在这几类输入下都没有抛异常。")


def main():
    graph = build_graph()

    print("=== 测试1：正常长度作文（应该走完整链路，真实调用DeepSeek）===")
    with tempfile.TemporaryDirectory() as tmp:
        import src.storage.db as db_module

        db_module.DEFAULT_DB_PATH = Path(tmp) / "test.db"

        result = graph.invoke(
            {
                "user_id": "e2e_test_user",
                "essay_text": SAMPLE_ESSAY,
                "essay_prompt_id": 1,
            }
        )
        print("is_valid:", result.get("is_valid"))
        print("quant_score:", result.get("quant_score"))
        print("trait_scores:", result.get("trait_scores"))
        print("qualitative_feedback (前200字):", result.get("qualitative_feedback", "")[:200])
        print("revision_plan (前200字):", result.get("revision_plan", "")[:200])

        assert result.get("is_valid") is True
        assert result.get("qualitative_feedback"), "定性反馈不应该为空"
        assert result.get("revision_plan"), "辅导建议不应该为空"

        history = db_module.get_user_history("e2e_test_user", db_path=db_module.DEFAULT_DB_PATH)
        assert len(history) == 1, f"应该有1条历史记录，实际{len(history)}条"
        print("SQLite历史记录 OK:", history)

    print("\n=== 测试2：过短作文（应该被短路拒绝，不调用LLM）===")
    result2 = graph.invoke(
        {
            "user_id": "e2e_test_user_2",
            "essay_text": TOO_SHORT_ESSAY,
            "essay_prompt_id": 1,
        }
    )
    print("is_valid:", result2.get("is_valid"))
    print("reject_reason:", result2.get("reject_reason"))
    assert result2.get("is_valid") is False
    assert "qualitative_feedback" not in result2 or not result2.get("qualitative_feedback")

    print("\n=== 测试3：边界/异常案例（Day3新增）===")
    test_edge_cases(graph)

    print("\n全部端到端测试通过（含真实DeepSeek调用）。")


if __name__ == "__main__":
    main()
