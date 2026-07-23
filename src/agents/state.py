"""LangGraph状态定义，对应Docs/01-系统架构与Agent设计.md「State（图状态定义）」。

用total=False是因为State的字段是随着图往下走逐步被各节点填充的，
入口处只有user_id/essay_text是必填的。
"""
from __future__ import annotations

from typing import Optional, TypedDict


# 定义 LangGraph 节点间传递的作文、评分、反馈与辅导状态字段。
class EssayReviewState(TypedDict, total=False):
    user_id: str
    essay_text: str
    exam_type: Optional[str]
    exam_subtype: Optional[str]
    essay_topic: Optional[str]

    essay_image_b64: Optional[str]  # IELTS Task 1上传的图表/图片，base64编码
    image_analysis: Optional[str]   # 图片理解模型（GLM-4V-Flash）对图片内容的结构化描述
    image_analysis_error: Optional[str]

    is_valid: bool
    reject_reason: Optional[str]

    retrieved_context: list[str]

    grammar_errors: list[dict]

    qualitative_feedback: str
    feedback_dimensions: dict
    overall_summary: str
    revision_plan: str
    coach_plan: dict

    official_rubric_score: float
    official_rubric_max: float
    official_rubric_label: str
    official_rubric_scores: dict[str, float]

    score_source: str
    primary_score: Optional[float]
    primary_max: Optional[float]
    primary_label: Optional[str]
    secondary_score: Optional[float]
    secondary_max: Optional[float]
    secondary_label: Optional[str]
    score_details: dict
    score_error: Optional[str]

    # CriticAgentNode反思循环：对feedback_agent_node生成的定性反馈做一次质量
    # 复核，不合格则打回feedback_agent_node重新生成，见src/agents/graph.py
    # 的route_after_critic()。critic_revision_count封顶1次重试，不是无限循环。
    critic_approved: Optional[bool]
    critic_notes: Optional[str]
    critic_revision_count: int

    history_summary: Optional[dict]
