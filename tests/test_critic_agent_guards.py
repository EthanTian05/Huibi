"""CriticAgentNode有两条不需要调用LLM的短路分支（重试次数已封顶/反馈本身
为空），这两条在真实Graph里也是零成本路径，可以在不触碰任何网络调用的
情况下验证。"合格与否"这条真正需要LLM判断质量的分支需要真实调用DeepSeek，
不在这个零依赖套件的覆盖范围内，见scripts/e2e_graph_test.py。"""
from src.agents import nodes


def test_second_revision_force_approves_without_llm_call():
    # revision_count已经是1（说明已经打回重写过一次），不管这次质量如何都
    # 应该无条件放行，且不应该走到需要LLM的代码路径（如果真的调用了LLM，
    # 这个测试在没有网络/API Key的CI环境里会直接抛异常而不是安静通过）。
    state = {
        "essay_text": "placeholder",
        "overall_summary": "占位",
        "feedback_dimensions": {"内容主旨": {"strengths": "x", "improvements": "y", "tips": []}},
        "critic_revision_count": 1,
    }
    result = nodes.critic_agent_node(state)
    assert result["critic_approved"] is True
    assert result["critic_notes"] is None


def test_empty_feedback_dimensions_skips_llm_call():
    state = {
        "essay_text": "placeholder",
        "overall_summary": "",
        "feedback_dimensions": {},
        "critic_revision_count": 0,
    }
    result = nodes.critic_agent_node(state)
    assert result["critic_approved"] is True
    assert result["critic_notes"] is None


def test_missing_revision_count_defaults_to_zero_not_error():
    # state["critic_revision_count"]在提交的第一轮压根不存在（EssayReviewState
    # 是total=False的TypedDict），不能因为这个key缺失就报KeyError。
    state = {"essay_text": "placeholder", "feedback_dimensions": {}}
    result = nodes.critic_agent_node(state)
    assert result["critic_approved"] is True
