"""LangGraph各节点实现，对应Docs/01-系统架构与Agent设计.md「节点职责表」。

现状（本轮在训练服务器上补齐了Day2的核心部分）：
- `intake_validator_node`、`feedback_agent_node`、`coach_agent_node`、
  `progress_tracker_node`：真实实现。
- `scoring_tool_node`：真实实现，调用`EssayScorer`（路径A微调DistilBERT +
  路径B自建BiLSTM的融合），模型已经在真实ASAP-AES数据上训练过，测试集QWK
  分别是0.693（路径A）和0.622（路径B），见`models/essay-scorer-*/v1/training_log.json`。
  **分项trait_scores目前是整体分的占位复制，不是单独训练的分项预测**，见
  `src/training/essay_scorer.py`顶部的诚实说明。
- `retrieval_agent_node`：真实实现，检索本轮已构建好的Chroma向量库
  （`data/processed/chroma_kb`，120个chunk，来自8个essay_set的真实rubric/
  prompt + 语法卡片）。
- `grammar_check_node`：仍是Day3占位（还没接`language_tool_python`）。

注意：涉及LLM调用/模型加载的函数把import放在函数体内（懒加载），不放在模块
顶部——这样`intake_validator_node`这类不需要额外依赖的逻辑，可以在没装
langchain-openai/torch的环境里单独导入和单测（见scripts/smoke_test_nodes.py）。
如果`models/essay-scorer-*/v1`或`data/processed/chroma_kb`在本地不存在
（比如刚clone仓库、还没跑训练/建库脚本），`scoring_tool_node`/
`retrieval_agent_node`会自动降级回Day1的占位逻辑，不会直接报错崩溃。
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


CHROMA_KB_DIR = "data/processed/chroma_kb"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
_retriever_cache = None


def retrieval_agent_node(state: EssayReviewState) -> EssayReviewState:
    global _retriever_cache
    from pathlib import Path

    if not Path(CHROMA_KB_DIR).exists():
        # 知识库还没构建（见src/rag/build_kb.py），降级回占位结果，不阻塞主链路。
        return {
            **state,
            "retrieved_context": [
                "[占位] 知识库尚未构建，运行 `python -m src.rag.build_kb` 后这里会是"
                "真实检索到的评分细则/语法规则/范文片段。"
            ],
        }

    if _retriever_cache is None:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import Chroma

        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        _retriever_cache = Chroma(persist_directory=CHROMA_KB_DIR, embedding_function=embeddings)

    query = f"essay_set {state.get('essay_prompt_id')} scoring rubric: {state.get('essay_text', '')[:300]}"
    docs = _retriever_cache.similarity_search(query, k=3)
    return {**state, "retrieved_context": [d.page_content for d in docs]}


_scorer_cache = None


def scoring_tool_node(state: EssayReviewState) -> EssayReviewState:
    global _scorer_cache
    from pathlib import Path

    finetuned_exists = Path("models/essay-scorer-finetuned/v1").exists()
    custom_exists = Path("models/essay-scorer-custom/v1").exists()

    if not (finetuned_exists or custom_exists):
        # 两条评分模型都还没训练好（见src/training/train_finetuned.py /
        # train_custom.py），降级回Day1的占位启发式，不阻塞主链路，但明确标注
        # 这不是真实评分能力。
        word_count = len(state.get("essay_text", "").split())
        heuristic_score = max(0.0, min(1.0, word_count / 400))
        return {
            **state,
            "quant_score": heuristic_score,
            "trait_scores": {"content": heuristic_score, "organization": heuristic_score, "language": heuristic_score},
        }

    if _scorer_cache is None:
        from src.training.essay_scorer import EssayScorer

        _scorer_cache = EssayScorer()

    result = _scorer_cache.predict(state.get("essay_text", ""), state.get("essay_prompt_id", 1))
    return {**state, "quant_score": result["score_norm"], "trait_scores": result["traits"]}


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
