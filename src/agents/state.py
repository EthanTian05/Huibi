"""LangGraph状态定义，对应Docs/01-系统架构与Agent设计.md「State（图状态定义）」。

用total=False是因为State的字段是随着图往下走逐步被各节点填充的，
入口处只有user_id/essay_text/essay_prompt_id是必填的。
"""
from __future__ import annotations

from typing import Optional, TypedDict


class EssayReviewState(TypedDict, total=False):
    user_id: str
    essay_text: str
    essay_prompt_id: int

    is_valid: bool
    reject_reason: Optional[str]

    retrieved_context: list[str]

    quant_score: float
    trait_scores: dict[str, float]

    grammar_errors: list[dict]

    qualitative_feedback: str
    revision_plan: str

    history_summary: Optional[dict]
