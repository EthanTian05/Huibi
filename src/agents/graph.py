"""LangGraph状态图定义，对应Docs/01-系统架构与Agent设计.md的架构图和
状态转移图（stateDiagram-v2）。跑`app.py`或`scripts/`下的手动测试脚本
之前，先确认.env里的LLM Key已配置好（见Docs/03-RUNNING.md）。
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.agents import nodes
from src.agents.state import EssayReviewState


# 判断文章长短，不通过直接pass
def route_after_intake(state: EssayReviewState) -> str:
    return "image_analysis" if state.get("is_valid") else "short_circuit_reject"


# CriticAgentNode反思循环的路由：复核通过（或已经打回重写过1次）就继续走
# coach_agent，否则回到feedback_agent重新生成定性反馈——critic_agent_node
# 自己保证revision_count封顶1次，这里不需要再重复判断次数。
def route_after_critic(state: EssayReviewState) -> str:
    return "coach_agent" if state.get("critic_approved", True) else "feedback_agent"


# LangGraph 主流程
def build_graph():
    graph = StateGraph(EssayReviewState)
    #9个节点
    graph.add_node("intake_validator", nodes.intake_validator_node)
    graph.add_node("image_analysis", nodes.image_analysis_node)
    graph.add_node("retrieval_agent", nodes.retrieval_agent_node)
    graph.add_node("grammar_check", nodes.grammar_check_node)
    graph.add_node("feedback_agent", nodes.feedback_agent_node)
    graph.add_node("critic_agent", nodes.critic_agent_node)
    graph.add_node("coach_agent", nodes.coach_agent_node)
    graph.add_node("progress_tracker", nodes.progress_tracker_node)
    graph.add_node("short_circuit_reject", nodes.short_circuit_reject_node)

    graph.set_entry_point("intake_validator")
    #2个条件路由
    graph.add_conditional_edges(
        "intake_validator",
        route_after_intake,
        {
            "image_analysis": "image_analysis",
            "short_circuit_reject": "short_circuit_reject",
        },
    )
    graph.add_edge("image_analysis", "retrieval_agent")
    graph.add_edge("retrieval_agent", "grammar_check")
    graph.add_edge("grammar_check", "feedback_agent")
    graph.add_edge("feedback_agent", "critic_agent")
    graph.add_conditional_edges(
        "critic_agent",
        route_after_critic,
        {
            "coach_agent": "coach_agent",
            "feedback_agent": "feedback_agent",
        },
    )
    graph.add_edge("coach_agent", "progress_tracker")
    graph.add_edge("progress_tracker", END)
    graph.add_edge("short_circuit_reject", END)

    return graph.compile()
