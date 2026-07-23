"""Day1端到端验证：真实调用build_graph().invoke()，包括真实的DeepSeek调用，
不是只测语法。之前在本地开发环境因为pip装不上，这个脚本没能跑起来；现在有
能pip install的环境（本地用`uv`能绕开这个环境的pip SSLEOFError，见CLAUDE.md
「环境信息」），用这个脚本验证整条链路。

数据库读写测试（`test_db_roundtrip`/`test_auth_roundtrip`）也在这个脚本里：
本轮数据库从SQLite迁移到PostgreSQL后，`src/storage/db.py`需要`psycopg`包，
不再是`scripts/smoke_test_nodes.py`能覆盖的零依赖范围。这两个测试连的是
`POSTGRES_DB=huibi_test`（下面在导入前设置好环境变量），不会碰生产库`huibi`
里的真实数据，每次跑之前会先清空这两张表，不用手动清理。

用法（需要本地先跑着PostgreSQL，`pg_ctl start`）：
    PYTHONPATH=. python scripts/e2e_graph_test.py
"""
from __future__ import annotations

import os

# 必须在import src.storage.db之前设置，_build_dsn()读的是运行时环境变量；
# 用独立的测试库，不会碰生产库`huibi`的真实数据。
os.environ["POSTGRES_DB"] = os.environ.get("POSTGRES_TEST_DB", "huibi_test")

from src.agents.graph import build_graph
from src.exam_types import GENERAL, IELTS, IELTS_TASK1, TOEFL
from src.storage import db

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


def _truncate_test_tables() -> None:
    """每次跑数据库测试前清空`huibi_test`库的两张表，保证测试可重复跑、
    不会因为用户名UNIQUE约束或历史记录累积而失败（迁移前SQLite版本每次
    测试用一个全新的临时文件，效果等价，只是换了个实现方式）。"""
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE submissions, users RESTART IDENTITY")
    conn.commit()
    conn.close()


def test_db_roundtrip():
    _truncate_test_tables()
    state = {
        "user_id": "test_user",
        "exam_type": GENERAL,
        "official_rubric_scores": {"内容与任务完成": 20, "结构与衔接": 18,
                                    "语言运用与词汇": 19, "语法准确性": 15},
        "qualitative_feedback": "test feedback",
        "revision_plan": "test plan",
        "score_source": "llm_rubric",
        "primary_score": 72,
        "primary_max": 100.0,
        "primary_label": "通用英语写作能力对照评分",
        "score_details": {"内容与任务完成": 20},
    }
    db.save_submission(state)
    db.save_submission({**state, "primary_score": 80})

    history = db.get_user_history("test_user")
    assert len(history) == 2, f"应该有2条记录，实际{len(history)}条"
    assert history[0]["primary_score"] == 72
    assert history[1]["primary_score"] == 80
    assert history[0]["official_rubric_scores"]["内容与任务完成"] == 20
    assert history[0]["score_details"]["内容与任务完成"] == 20
    print("db.save_submission / get_user_history 往返测试 OK（PostgreSQL JSONB字段）")


def test_auth_roundtrip():
    """db.create_user/verify_user，PBKDF2密码哈希（纯标准库hashlib/secrets）。"""
    _truncate_test_tables()

    ok, msg = db.create_user("alice", "password123")
    assert ok, msg
    ok2, msg2 = db.create_user("alice", "password123")
    assert ok2 is False, "重复用户名应该注册失败"
    assert "已存在" in msg2

    ok3, msg3 = db.create_user("bob", "123")
    assert ok3 is False, "密码太短应该注册失败"

    assert db.verify_user("alice", "password123") is True
    assert db.verify_user("alice", "wrongpassword") is False
    assert db.verify_user("nobody", "whatever") is False
    print("db.create_user / verify_user 登录注册往返测试 OK")


def _run_case(graph, name: str, essay_text: str, exam_type: str, user_id: str) -> dict:
    print(f"\n=== {name} ===")
    try:
        result = graph.invoke({"user_id": user_id, "essay_text": essay_text, "exam_type": exam_type})
        print("is_valid:", result.get("is_valid"))
        if result.get("is_valid") is False:
            print("reject_reason:", result.get("reject_reason"))
        else:
            print("primary_score:", result.get("primary_score"), "/", result.get("primary_max"))
            print("official_rubric_scores:", result.get("official_rubric_scores"))
            print("grammar_errors数量:", len(result.get("grammar_errors", [])))
        return result
    except Exception as e:
        print(f"!!! 抛出异常: {type(e).__name__}: {e}")
        raise


def test_edge_cases(graph):
    """覆盖MIN/MAX_WORDS边界、语法错误密集这几类之前没测过的边界情况，
    确认不会让Graph在中途抛异常崩溃。
    """
    r1 = _run_case(graph, "边界1：正好20词（MIN_WORDS边界，应通过校验）", BOUNDARY_SHORT_ESSAY, GENERAL, "edge_user_1")
    assert r1.get("is_valid") is True, "正好20词应该通过校验"

    r2 = _run_case(graph, "边界2：正好1000词（MAX_WORDS边界，应通过校验）", BOUNDARY_LONG_ESSAY, GENERAL, "edge_user_2")
    assert r2.get("is_valid") is True, "正好1000词应该通过校验"

    r3 = _run_case(graph, "边界3：1001词（超过MAX_WORDS，应被拒绝）", TOO_LONG_ESSAY, GENERAL, "edge_user_3")
    assert r3.get("is_valid") is False, "1001词应该被拒绝"

    r4 = _run_case(graph, "边界4：语法错误密集的作文（grammar_check_node压力测试）", MANY_ERRORS_ESSAY, GENERAL, "edge_user_4")
    assert r4.get("is_valid") is True
    assert len(r4.get("grammar_errors", [])) >= 5, "这篇作文应该检测出至少5处语法问题"

    r5 = _run_case(graph, "边界5：IELTS Task 2 打分（LLM量表路径）", SAMPLE_ESSAY, IELTS, "edge_user_5")
    assert r5.get("is_valid") is True
    assert r5.get("score_error") is None, f"IELTS评分不应该报错：{r5.get('score_error')}"
    assert 0 <= r5.get("primary_score", -1) <= 9, "IELTS Band应该在0-9之间"

    r6 = _run_case(graph, "边界6：TOEFL 单题打分（LLM量表路径）", SAMPLE_ESSAY, TOEFL, "edge_user_6")
    assert r6.get("is_valid") is True
    assert r6.get("score_error") is None, f"TOEFL评分不应该报错：{r6.get('score_error')}"
    assert 0 <= r6.get("primary_score", -1) <= 5, "TOEFL单题分应该在0-5之间"

    print("\n=== 边界7：IELTS Task 1（图片理解+Task Achievement量表） ===")
    import base64
    import io

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # 现场画一张有真实数据的折线图（matplotlib已经是requirements.txt里的
    # 依赖，不需要额外装包），验证图片理解→打分→反馈全链路不崩溃。
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.plot([2018, 2019, 2020, 2021, 2022], [12, 15, 14, 18, 25], marker="o", label="Coffee")
    ax.plot([2018, 2019, 2020, 2021, 2022], [30, 28, 26, 22, 19], marker="s", label="Tea")
    ax.set_xlabel("Year")
    ax.set_ylabel("Consumption (kg per capita)")
    ax.legend()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    fake_chart_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    r7 = graph.invoke({
        "user_id": "edge_user_7", "essay_text": SAMPLE_ESSAY, "exam_type": IELTS,
        "exam_subtype": IELTS_TASK1, "essay_image_b64": fake_chart_b64,
    })
    assert r7.get("is_valid") is True
    print("image_analysis:", (r7.get("image_analysis") or "")[:150])
    print("image_analysis_error:", r7.get("image_analysis_error"))
    assert r7.get("score_error") is None, f"IELTS Task1评分不应该报错：{r7.get('score_error')}"
    assert 0 <= r7.get("primary_score", -1) <= 9, "IELTS Task1 Band应该在0-9之间"
    assert r7.get("primary_label") == "IELTS Writing Task 1 标准对照 Band（0–9）"

    print("\n全部边界案例测试通过，Graph在这几类输入下都没有抛异常。")


def main():
    print("=== 测试0：PostgreSQL数据库读写（huibi_test库） ===")
    test_db_roundtrip()
    test_auth_roundtrip()

    graph = build_graph()

    print("\n=== 测试1：正常长度作文，GENERAL类型（应该走完整链路，真实调用DeepSeek）===")
    _truncate_test_tables()

    result = graph.invoke(
        {
            "user_id": "e2e_test_user",
            "essay_text": SAMPLE_ESSAY,
            "exam_type": GENERAL,
        }
    )
    print("is_valid:", result.get("is_valid"))
    print("primary_score:", result.get("primary_score"), "/", result.get("primary_max"))
    print("official_rubric_scores:", result.get("official_rubric_scores"))
    print("qualitative_feedback (前200字):", result.get("qualitative_feedback", "")[:200])
    print("revision_plan (前200字):", result.get("revision_plan", "")[:200])
    print("critic_approved:", result.get("critic_approved"), "critic_revision_count:", result.get("critic_revision_count"))

    assert result.get("is_valid") is True
    assert result.get("score_error") is None, f"GENERAL评分不应该报错：{result.get('score_error')}"
    assert result.get("official_rubric_scores") and len(result["official_rubric_scores"]) == 4, \
        "GENERAL应该返回四维度评分"
    assert result.get("qualitative_feedback"), "定性反馈不应该为空"
    assert result.get("revision_plan"), "辅导建议不应该为空"
    # CriticAgentNode反思循环应该真的跑过（不管这次是否触发重写），
    # critic_approved应该有明确的True/False，不是None（None意味着这个节点
    # 根本没执行，说明图的路由接错了）。
    assert result.get("critic_approved") is not None, "critic_agent_node应该已经跑过一轮复核"
    assert result.get("critic_revision_count", 0) <= 1, "反思循环重试次数不应该超过1次"

    history = db.get_user_history("e2e_test_user")
    assert len(history) == 1, f"应该有1条历史记录，实际{len(history)}条"
    print("PostgreSQL历史记录 OK:", history)

    print("\n=== 测试2：过短作文（应该被短路拒绝，不调用LLM）===")
    result2 = graph.invoke(
        {
            "user_id": "e2e_test_user_2",
            "essay_text": TOO_SHORT_ESSAY,
            "exam_type": GENERAL,
        }
    )
    print("is_valid:", result2.get("is_valid"))
    print("reject_reason:", result2.get("reject_reason"))
    assert result2.get("is_valid") is False
    assert "qualitative_feedback" not in result2 or not result2.get("qualitative_feedback")

    print("\n=== 测试3：边界/异常案例 ===")
    test_edge_cases(graph)

    print("\n全部端到端测试通过（含真实DeepSeek调用）。")


if __name__ == "__main__":
    main()
