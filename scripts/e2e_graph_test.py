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

    print("\n全部端到端测试通过（含真实DeepSeek调用）。")


if __name__ == "__main__":
    main()
