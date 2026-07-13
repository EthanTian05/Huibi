"""LangGraph状态图定义，对应Docs/01-系统架构与Agent设计.md的架构图和
状态转移图（stateDiagram-v2）。跑`app.py`或`scripts/`下的手动测试脚本
之前，先确认.env里的LLM Key已配置好（见Docs/RUNNING.md）。
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.agents import nodes
from src.agents.state import EssayReviewState


def route_after_intake(state: EssayReviewState) -> str:
    return "retrieval_agent" if state.get("is_valid") else "short_circuit_reject"


def build_graph():
    graph = StateGraph(EssayReviewState)

    graph.add_node("intake_validator", nodes.intake_validator_node)
    graph.add_node("retrieval_agent", nodes.retrieval_agent_node)
    graph.add_node("scoring_tool", nodes.scoring_tool_node)
    graph.add_node("grammar_check", nodes.grammar_check_node)
    graph.add_node("feedback_agent", nodes.feedback_agent_node)
    graph.add_node("coach_agent", nodes.coach_agent_node)
    graph.add_node("progress_tracker", nodes.progress_tracker_node)
    graph.add_node("short_circuit_reject", nodes.short_circuit_reject_node)

    graph.set_entry_point("intake_validator")
    graph.add_conditional_edges(
        "intake_validator",
        route_after_intake,
        {
            "retrieval_agent": "retrieval_agent",
            "short_circuit_reject": "short_circuit_reject",
        },
    )
    graph.add_edge("retrieval_agent", "scoring_tool")
    graph.add_edge("scoring_tool", "grammar_check")
    graph.add_edge("grammar_check", "feedback_agent")
    graph.add_edge("feedback_agent", "coach_agent")
    graph.add_edge("coach_agent", "progress_tracker")
    graph.add_edge("progress_tracker", END)
    graph.add_edge("short_circuit_reject", END)

    return graph.compile()
