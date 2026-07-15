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
- `grammar_check_node`：Day3已实现，纯Python正则规则库（不是`language_tool_python`，
  见函数上方注释说明为什么选规则库而非该依赖）。

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
        import warnings

        warnings.warn(
            f"{CHROMA_KB_DIR} 不存在，retrieval_agent_node降级为占位结果。"
            f"先跑 `python -m src.rag.build_rubric_docs && python -m src.rag.build_kb` 构建知识库。"
        )
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
        # 两条评分模型都还没训练好/还没下载（见src/training/train_finetuned.py /
        # train_custom.py，或者跑 `python scripts/download_models.py` 从GitHub
        # Release下载已训练好的权重），降级回Day1的占位启发式，不阻塞主链路，
        # 但明确标注这不是真实评分能力。
        import warnings

        warnings.warn(
            "models/essay-scorer-{finetuned,custom}/v1 都不存在，scoring_tool_node降级为"
            "词数启发式占位评分（不代表真实评分能力）。跑 `python scripts/download_models.py` "
            "下载已训练好的权重，或参考RUNNING.md重新训练。"
        )
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


import re
import statistics

# 规则库方案（而非language_tool_python）：language_tool_python需要打包的Java版
# LanguageTool引擎（下载约200MB+要求本机装Java），在部署服务器121.41.238.92
# 磁盘只剩9.3G、且未确认装了Java的情况下风险偏高，4天工期临近Day4部署，
# 选风险更低的纯Python规则库方案，不引入新的pip依赖，见Docs/TODO.md本轮决策记录。
_MISSPELLINGS = {
    "recieve": "receive", "seperate": "separate", "definately": "definitely",
    "occured": "occurred", "wich": "which", "untill": "until",
    "goverment": "government", "enviroment": "environment", "arguement": "argument",
    "begining": "beginning", "concious": "conscious", "wether": "whether",
    "neccessary": "necessary", "accomodate": "accommodate", "acheive": "achieve",
    "publically": "publicly", "priviledge": "privilege",
    "thier": "their", "becuase": "because", "diffrent": "different",
    "alot": "a lot", "truely": "truly", "excelent": "excellent",
}

# (pattern, type, message, case_sensitive) —— case_sensitive=True的规则不加IGNORECASE，
# 否则像"lowercase_i"这类依赖大小写本身的规则会对已经正确大写的文本产生误判。
_GRAMMAR_PATTERNS: list[tuple[str, str, str, bool]] = [
    (r"\b(\w+)\s+\1\b", "repeated_word", "重复用词", False),
    (r"\bshould of\b", "modal_of", "情态动词后误用of，应为have（should have）", False),
    (r"\bwould of\b", "modal_of", "情态动词后误用of，应为have（would have）", False),
    (r"\bcould of\b", "modal_of", "情态动词后误用of，应为have（could have）", False),
    (r"\b(?:don'?t|doesn'?t|didn'?t|can'?t|won'?t|isn'?t|aren'?t)\b[^.!?]{0,40}?\bno(?:ne|thing|body)?\b",
     "double_negative", "双重否定", False),
    (r"(?<![\w'])i(?![\w'])", "lowercase_i", "第一人称单数I应大写", True),
    (r"\s+[,.!?;:]", "space_before_punct", "标点符号前多余的空格", False),
    (r"[,.!?;:](?=[A-Za-z])", "no_space_after_punct", "标点符号后缺少空格", False),
]


def _check_sentence_capitalization(text: str) -> list[dict]:
    errors = []
    for m in re.finditer(r"(?:^|[.!?]\s+)([a-z])", text):
        errors.append({
            "type": "capitalization",
            "position": [m.start(1), m.end(1)],
            "context": text[max(0, m.start(1) - 15):m.end(1) + 15],
            "message": "句首字母应大写",
            "suggestion": m.group(1).upper(),
        })
    return errors


def _check_misspellings(text: str) -> list[dict]:
    errors = []
    for m in re.finditer(r"[A-Za-z']+", text):
        word = m.group(0)
        fix = _MISSPELLINGS.get(word.lower())
        if fix:
            errors.append({
                "type": "spelling",
                "position": [m.start(), m.end()],
                "context": text[max(0, m.start() - 15):m.end() + 15],
                "message": f"疑似拼写错误：{word}",
                "suggestion": fix,
            })
    return errors


def _heuristic_content_organization_penalty(text: str) -> tuple[float, float]:
    """用可观察的文本信号（词汇丰富度、分段/句长结构）给content/organization
    算一个启发式扣分，而不是让它们一直等于整体分的纯复制。**这仍然不是训练出来
    的多头预测**——只是比"完全不看文本、直接复制整体分"更有信号支撑的近似，
    答辩时要讲清楚这个区别（见Docs/03-模型训练与微调方案.md顶部说明）。
    """
    words = re.findall(r"[A-Za-z']+", text.lower())
    word_count = max(len(words), 1)

    # content：词汇丰富度（type-token ratio）过低，说明用词重复、内容单薄
    unique_ratio = len(set(words)) / word_count
    content_penalty = max(0.0, min(0.3, (0.35 - unique_ratio) * 1.5)) if unique_ratio < 0.35 else 0.0

    # organization：段落数过少（大段无分段）、或句长几乎没有变化（缺乏结构层次）
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    sentence_lengths = [len(s.split()) for s in sentences]

    organization_penalty = 0.0
    if len(paragraphs) <= 1 and word_count > 150:
        organization_penalty += 0.15
    if len(sentence_lengths) >= 3 and statistics.pstdev(sentence_lengths) < 2.0:
        organization_penalty += 0.1
    organization_penalty = min(0.3, organization_penalty)

    return content_penalty, organization_penalty


def grammar_check_node(state: EssayReviewState) -> EssayReviewState:
    """纯Python正则规则库的轻量语法检查，覆盖常见ESL错误类型（重复用词、
    情态动词+of误用、双重否定、句首大小写、标点空格、常见拼写错误），
    不是完整的语法解析器，比语言学意义上"全面"的NLP语法检查工具覆盖面窄，
    但零新增依赖、可控、适合4天工期+磁盘紧张的部署服务器。
    """
    text = state.get("essay_text", "")
    errors: list[dict] = []
    errors.extend(_check_sentence_capitalization(text))
    errors.extend(_check_misspellings(text))
    for pattern, err_type, message, case_sensitive in _GRAMMAR_PATTERNS:
        flags = 0 if case_sensitive else re.IGNORECASE
        for m in re.finditer(pattern, text, flags=flags):
            errors.append({
                "type": err_type,
                "position": [m.start(), m.end()],
                "context": text[max(0, m.start() - 15):m.end() + 15],
                "message": message,
                "suggestion": None,
            })
    errors.sort(key=lambda e: e["position"][0])

    # 用真实检测到的语法错误密度 + 词汇/结构启发式信号调整trait_scores三项，
    # 不再是整体分的纯复制。**仍然不是训练出来的多头预测**——只是从"完全不看
    # 文本内容"变成"有可观察信号支撑的启发式近似"，答辩时要讲清楚这个区别，
    # 不能说成"已完成多头训练"，见src/training/essay_scorer.py顶部说明。
    trait_scores = dict(state.get("trait_scores") or {})
    word_count = max(len(text.split()), 1)
    content_penalty, organization_penalty = _heuristic_content_organization_penalty(text)

    if "language" in trait_scores:
        error_rate = len(errors) / word_count
        language_penalty = min(0.5, error_rate * 5)
        trait_scores["language"] = max(0.0, min(1.0, trait_scores["language"] - language_penalty))
    if "content" in trait_scores:
        trait_scores["content"] = max(0.0, min(1.0, trait_scores["content"] - content_penalty))
    if "organization" in trait_scores:
        trait_scores["organization"] = max(0.0, min(1.0, trait_scores["organization"] - organization_penalty))

    return {**state, "grammar_errors": errors, "trait_scores": trait_scores}


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
