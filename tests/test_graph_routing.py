"""LangGraph路由函数是纯逻辑（读state字段、返回下一个节点名字符串），不涉及
真实调用，但导入src.agents.graph需要langgraph包（轻量，不像torch/transformers
那样重）。本地这个开发环境没装langgraph时用pytest.importorskip跳过，CI里
装了完整跑，两边都不会因为这一个文件影响其它测试文件。"""
import pytest

pytest.importorskip("langgraph")

from src.agents.graph import route_after_critic, route_after_intake  # noqa: E402


def test_route_after_intake_valid_goes_to_image_analysis():
    assert route_after_intake({"is_valid": True}) == "image_analysis"


def test_route_after_intake_invalid_goes_to_reject():
    assert route_after_intake({"is_valid": False}) == "short_circuit_reject"


def test_route_after_critic_approved_goes_to_coach():
    assert route_after_critic({"critic_approved": True}) == "coach_agent"


def test_route_after_critic_rejected_goes_back_to_feedback():
    assert route_after_critic({"critic_approved": False}) == "feedback_agent"


def test_route_after_critic_missing_key_defaults_to_approved():
    # critic_agent_node理论上总会设置critic_approved，但路由函数本身对
    # 缺失这个key要有合理默认值（放行而不是报错），防御性处理。
    assert route_after_critic({}) == "coach_agent"


def test_build_graph_registers_all_nodes():
    from src.agents.graph import build_graph

    graph = build_graph()
    node_names = set(graph.get_graph().nodes.keys())
    expected = {
        "intake_validator", "image_analysis", "retrieval_agent", "grammar_check",
        "feedback_agent", "critic_agent", "coach_agent", "progress_tracker",
        "short_circuit_reject",
    }
    assert expected.issubset(node_names)
