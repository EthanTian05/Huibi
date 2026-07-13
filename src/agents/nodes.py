"""LangGraph各节点实现，对应Docs/01-系统架构与Agent设计.md「节点职责表」。

Day1现状：
- `intake_validator_node`、`feedback_agent_node`、`coach_agent_node`、
  `progress_tracker_node` 是真实实现。
- `retrieval_agent_node`、`scoring_tool_node`、`grammar_check_node` 是
  Day2占位实现（RAG知识库和评分模型还没构建/训练好），返回结果里明确
  标注了"[Day2占位]"，不要在没看这个文件之前就以为它们是真的评分/检索结果。

注意：涉及LLM调用的函数把`from src.agents.llm import ...`放在函数体内
（懒加载），不放在模块顶部——这样`intake_validator_node`/`scoring_tool_node`/
`grammar_check_node`/db读写这些不需要langchain的逻辑，可以在没装
langchain-openai的环境里单独导入和单测（见scripts/smoke_test_nodes.py）。
"""
from __future__ import annotations

from src.agents.state import EssayReviewState
from src.storage import db

MIN_WORDS = 20
MAX_WORDS = 1000


def intake_validator_node(state: EssayReviewState) -> EssayReviewState:
    text = state.get("essay_text", "")
    word_count = len(text.split())
    if word_count < MIN_WORDS:
        return {
            **state,
            "is_valid": False,
            "reject_reason": f"作文过短（{word_count}词），至少需要{MIN_WORDS}词",
        }
    if word_count > MAX_WORDS:
        return {
            **state,
            "is_valid": False,
            "reject_reason": f"作文过长（{word_count}词），请控制在{MAX_WORDS}词以内",
        }
    return {**state, "is_valid": True, "reject_reason": None}


def retrieval_agent_node(state: EssayReviewState) -> EssayReviewState:
    # Day2 TODO：接入Chroma向量库，按essay_prompt_id检索rubric/语法卡片/范文
    # 片段，见Docs/01-系统架构与Agent设计.md「RAG知识库设计」和src/rag/build_kb.py。
    placeholder = [
        "[Day2占位] 知识库尚未构建，这里应该是按essay_prompt_id检索到的"
        "评分细则/语法规则/范文片段。",
    ]
    return {**state, "retrieved_context": placeholder}


def scoring_tool_node(state: EssayReviewState) -> EssayReviewState:
    # Day2 TODO：接入EssayScorer（微调BERT系路径A + 自建BiLSTM路径B融合），
    # 见Docs/03-模型训练与微调方案.md。
    # 下面是占位启发式：按词数给一个粗略的0-1分数，只是为了让后续Agent节点
    # 有输入可用，完全不代表真实评分能力，答辩时不能拿这个当成果展示。
    word_count = len(state.get("essay_text", "").split())
    heuristic_score = max(0.0, min(1.0, word_count / 400))
    return {
        **state,
        "quant_score": heuristic_score,
        "trait_scores": {
            "content": heuristic_score,
            "organization": heuristic_score,
            "language": heuristic_score,
        },
    }


def grammar_check_node(state: EssayReviewState) -> EssayReviewState:
    # Day2/3 TODO：接入language_tool_python或规则库，见
    # Docs/01-系统架构与Agent设计.md「Agent使用的工具清单」。
    return {**state, "grammar_errors": []}


FEEDBACK_PROMPT = """你是一名经验丰富的英语写作老师，面向中国的英语学习者（四六级/考研英语/雅思写作场景）。
请根据下面的作文内容、参考评分细则/检索片段、量化评分，给出结构化的中文定性反馈。

作文原文：
{essay_text}

参考评分细则/检索片段：
{retrieved_context}

量化评分（0-1，仅供参考，Day2接入真实评分模型前不代表实际水平）：{quant_score}

请按以下结构输出：
1. 优点（Strengths）：具体指出2-3处写得好的地方，引用原文片段。
2. 不足（Weaknesses）：具体指出2-3处需要改进的地方，引用原文片段。
3. 语法与用词建议：如果有明显的语法/用词问题，逐条列出"原句 → 建议修改 → 为什么"；
   如果没有检测到具体语法错误，就针对整体用词/句式给建议。

用中文回答，语气鼓励但具体、可操作，不要空泛的套话。"""


def feedback_agent_node(state: EssayReviewState) -> EssayReviewState:
    from src.agents.llm import get_chat_model_with_fallback

    llm = get_chat_model_with_fallback()
    prompt = FEEDBACK_PROMPT.format(
        essay_text=state.get("essay_text", ""),
        retrieved_context="\n".join(state.get("retrieved_context", [])),
        quant_score=state.get("quant_score", "未知"),
    )
    response = llm.invoke(prompt)
    return {**state, "qualitative_feedback": response.content}


COACH_PROMPT = """你是一名英语写作辅导教练。基于下面这份对某篇作文的定性反馈，
以及该学生的历史提交摘要（如果有），给出：
1. 一个简短的、有优先级的修改行动清单（最多3条）；
2. 1~2道针对该学生当前最主要弱项的针对性练习题（可以是"用XX语法点重写这句话"这类小题）。

定性反馈：
{qualitative_feedback}

该学生历史提交摘要：
{history_summary}

用中文回答，具体、可执行，不要空泛的套话。"""


def coach_agent_node(state: EssayReviewState) -> EssayReviewState:
    from src.agents.llm import get_chat_model_with_fallback

    llm = get_chat_model_with_fallback()
    prompt = COACH_PROMPT.format(
        qualitative_feedback=state.get("qualitative_feedback", ""),
        history_summary=state.get("history_summary") or "（该学生暂无历史提交记录）",
    )
    response = llm.invoke(prompt)
    return {**state, "revision_plan": response.content}


def progress_tracker_node(state: EssayReviewState) -> EssayReviewState:
    db.save_submission(state)
    return state


def short_circuit_reject_node(state: EssayReviewState) -> EssayReviewState:
    return state
