from __future__ import annotations

from src.agents.state import EssayReviewState

MIN_WORDS = 20
MAX_WORDS = 1000


def _warn_json_parse_failure(node_name: str, exc: Exception, raw_content: str) -> None:
    """LLM返回的JSON解析失败时统一记一条诊断warning，写进streamlit.log。
    """
    import json
    import warnings

    raw_content = raw_content or ""
    if isinstance(exc, json.JSONDecodeError):
        start = max(0, exc.pos - 150)
        end = min(len(raw_content), exc.pos + 150)
        context = raw_content[start:end]
        warnings.warn(
            f"{node_name}的JSON解析失败于字符位置{exc.pos}（{exc.msg}），"
            f"原始响应总长度={len(raw_content)}，出错位置前后文={context!r}"
        )
    else:
        warnings.warn(
            f"{node_name}的JSON解析失败（{exc}），原始响应总长度={len(raw_content)}，"
            f"开头片段={raw_content[:200]!r}"
        )


# 节点1：统计作文词数，不符合要求则pass
def intake_validator_node(state: EssayReviewState) -> EssayReviewState:
    """入口闸门：只让词数在规定区间内的作文进入后续昂贵链路。"""
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


IMAGE_ANALYSIS_PROMPT = """你是IELTS Writing Task 1的图表识图助手。这张图片是Task 1
题目附带的图表/表格/流程图/地图，请客观、准确地描述图片里的信息，不要评价、不要
猜测题目要求，只输出图片本身包含的事实信息，供后续单独的评阅环节核对作文描述是否
准确：
- 图表类型（柱状图/折线图/饼图/表格/流程图/地图等）
- 涉及哪些类别/时间点/地区等维度，具体数值或比例（尽量给出数字，不确定的标注"约"）
- 明显的趋势、最大值/最小值、显著的对比或转折点
只输出客观描述，用中文，200-350字，不要输出Markdown标题或列表符号，纯段落文本。"""


# 节点：图片理解（仅IELTS Task 1上传图片时执行，其余情况原样透传state）
def image_analysis_node(state: EssayReviewState) -> EssayReviewState:
    image_b64 = state.get("essay_image_b64")
    if not image_b64:
        return state

    from langchain_core.messages import HumanMessage

    from src.agents.llm import get_vision_chat_model

    message = HumanMessage(content=[
        {"type": "text", "text": IMAGE_ANALYSIS_PROMPT},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
    ])
    try:
        response = get_vision_chat_model().invoke([message])
        analysis = (response.content or "").strip()
        if not analysis:
            raise ValueError("图片理解模型返回了空内容")
        return {**state, "image_analysis": analysis, "image_analysis_error": None}
    except Exception as exc:  # noqa: BLE001 - 图片理解是新引入的外部调用，故意宽捕获
        import warnings

        warnings.warn(f"image_analysis_node图片理解失败：{exc}")
        return {
            **state,
            "image_analysis": None,
            "image_analysis_error": f"图片理解失败：{exc}",
        }


CHROMA_KB_DIR = "data/processed/chroma_kb"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
_retriever_cache = None


#节点2： 从Chroma检索与题目、考试类型匹配的评分细则，作为 LLM 反馈依据。
def retrieval_agent_node(state: EssayReviewState) -> EssayReviewState:
    """检索题型细则；专属细则无命中时才回退到全库。"""
    global _retriever_cache
    from pathlib import Path

    if not Path(CHROMA_KB_DIR).exists():
        # src/rag/build_kb.py
        import warnings

        warnings.warn(
            f"{CHROMA_KB_DIR} 不存在，retrieval_agent_node降级为占位结果。"
            f"先在data/kb/下补充评分细则/语法卡片素材，再跑 `python -m src.rag.build_kb` 构建知识库。"
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

        try:
            # 向量库在部署前已构建，运行时只应读取已缓存的 embedding 模型。
            # 不允许在 Streamlit 请求线程中访问 Hugging Face：该连接一旦被框架
            # 生命周期关闭，就会出现 "client has been closed"，并让整条批改链路失败。
            embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={"local_files_only": True},
            )
            _retriever_cache = Chroma(
                persist_directory=CHROMA_KB_DIR,
                embedding_function=embeddings,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            import warnings

            warnings.warn(
                f"无法从本地缓存加载 RAG 向量模型，检索节点降级：{exc}",
                RuntimeWarning,
            )
            return {
                **state,
                "retrieved_context": [
                    "[降级] RAG 向量模型当前不可用；本次反馈未引用题型知识库。"
                ],
            }

    query = (
        f"{state.get('exam_type', '')} scoring rubric. "
        f"Topic: {state.get('essay_topic', '')[:200]} "
        f"Essay: {state.get('essay_text', '')[:300]}"
    )

    # 有exam_type时优先在该考试类型专属的评分细则文件里检索（按source元数据过滤）
    # ASAP-AES原始rubric
    docs = []
    exam_type = state.get("exam_type")
    if exam_type:
        from src.exam_types import rubric_file_for_exam_type

        rubric_file = rubric_file_for_exam_type(exam_type)
        if rubric_file:
            docs = _retriever_cache.similarity_search(query, k=3, filter={"source": rubric_file})

    if not docs:
        docs = _retriever_cache.similarity_search(query, k=3)

    return {**state, "retrieved_context": [d.page_content for d in docs]}


import re

# 规则库方案
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


# 节点4：本地正则规则库 + LanguageTool公共API双重检查语法错误，供反馈节点引用。
def grammar_check_node(state: EssayReviewState) -> EssayReviewState:
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

    from src.agents.grammar_tools import languagetool_check

    # LanguageTool覆盖面比本地正则规则库广得多（真正的语法引擎，不是关键词匹配），
    # 但调用失败/限流时`languagetool_check`会静默返回空列表，不影响本地规则库
    # 这部分已经查到的结果。和正则结果按区间去重，避免同一处错误报两遍。
    existing_spans = [tuple(e["position"]) for e in errors]
    for lt_error in languagetool_check(text):
        lt_start, lt_end = lt_error["position"]
        if any(lt_start < end and lt_end > start for start, end in existing_spans):
            continue
        errors.append(lt_error)

    errors.sort(key=lambda e: e["position"][0])

    return {**state, "grammar_errors": errors}


# Few-shot校准示例：每种考试类型给一个"作文片段+正确评分+评分理由"，帮模型
# 校准打分尺度（避免笼统作文给太高分、或对语法小瑕疵扣分过重）并演示JSON键名，
# 不是解决JSON格式问题本身（那个已经靠normalize_rubric_result()提前校验+
# 重试1次解决了，见feedback_agent_node）。按exam_type/exam_subtype只挑一条
# 相关示例塞进prompt，不会把四种类型的示例都塞进去，控制token开销。
_SCORE_FEW_SHOT_EXAMPLES: dict[str, str] = {
    "GENERAL": """校准示例——作文片段："Computers are good for learning because they give
students access to a lot of information. They also teach useful skills like using
software and writing emails. If students use computers in a good way, they will
become better learners."（观点笼统、缺少具体例证、词汇重复度高，但语法基本正确）
对应评分：{"rubric_scores": {"content_score": 15, "organization_score": 16, "language_score": 13, "grammar_score": 20}}
评分理由：内容分不高是因为论点笼统、没有具体例子支撑，不是跑题；语言分不高是因为
"good"/"useful"这类模糊词重复出现、缺乏精准词汇；语法分较高是因为句子结构正确、
没有明显错误——四个维度要分开判断，不能因为某一维度弱就连带拉低其它维度。""",
    "TOEFL": """校准示例——作文片段（Academic Discussion任务）："I agree with Professor
Lee because online classes save time. Students don't need to travel to campus. Also
online classes are cheaper."（回应了讨论方向但展开单薄、缺少具体理由和例证、句式单一）
对应评分：{"rubric_scores": {"task_score": 3}}
评分理由：任务方向正确、属于"部分成功"，但展开有限、缺乏具体论证和例子、语言能力
单一，对应"部分成功，展开或语言能力存在明显限制"的3分描述；没有达到4分要求的
"总体成功、展开充分"。""",
    "IELTS": """校准示例——作文片段（Task 2）："Some people think technology makes people
lazy. I do not agree with this. Technology help us do many things fast. For example
computer can help student study better and find information quick."（立场清楚但只有
一个论点、展开有限；"technology help"/"find information quick"等主谓一致和词形错误
较明显）
对应评分：{"rubric_scores": {"task_response": 5, "coherence_cohesion": 5, "lexical_resource": 5, "grammar_accuracy": 4}}
评分理由：立场明确但论证单薄，对应Band 5"观点相关但发展不充分"；语法分更低一档是
因为主谓一致/词形错误较为频繁，但没有严重到影响理解，符合Band 4的部分描述。""",
    "IELTS_TASK1": """校准示例——作文片段（图表描述）："The chart show the number of
visitors. In 2010 it was high. Then it become more high in 2015. Overview, the trend
is increasing."（有overview但位置/用法不规范、数据描述模糊缺少具体数值、时态和
主谓一致有错误）
对应评分：{"rubric_scores": {"task_achievement": 4, "coherence_cohesion": 4, "lexical_resource": 4, "grammar_accuracy": 4}}
评分理由：有overview但描述模糊、缺少具体数据支撑，对应"关键特征报告不够准确"；
"it become more high"这类错误较明显地影响流畅度，四项均落在Band 4区间，不是
Task Achievement单独拖累其它维度。""",
}


def _score_few_shot_example(exam_type: str, exam_subtype: str | None) -> str:
    from src.exam_types import GENERAL, IELTS, IELTS_TASK1, TOEFL

    if exam_type == IELTS and exam_subtype == IELTS_TASK1:
        key = "IELTS_TASK1"
    elif exam_type == IELTS:
        key = "IELTS"
    elif exam_type == TOEFL:
        key = "TOEFL"
    else:
        key = "GENERAL"
    return _SCORE_FEW_SHOT_EXAMPLES.get(key, _SCORE_FEW_SHOT_EXAMPLES["GENERAL"])


SCORE_RUBRIC_PROMPT = """你是英语写作模拟评阅员的打分模块，只需要给出数值评分，
不需要任何文字说明或反馈。必须只按给定的公开评分描述评阅。

作文类型：{exam_type}
任务子类型：{exam_subtype}
作文题目：{essay_topic}
{image_context}
作文原文：
{essay_text}

公开评分描述：
{rubric_instruction}

{few_shot_example}

只返回一个合法JSON对象，不要使用Markdown代码围栏，也不要在JSON外写任何内容：
{{
  "rubric_scores": {{按上方"公开评分描述"里要求的键和值输出官方评分}}
}}
这是依据公开量表的模拟对照，不得自称正式考官或考试机构成绩；上面的校准示例只是
帮你把握评分尺度，本次评分只能依据当前这篇作文原文，不能照抄示例的分数。"""

FEEDBACK_ONLY_PROMPT = """你是英语写作模拟评阅员，负责给出定性反馈。数值评分已经
由另一个模型单独给出，这里不需要你输出任何分数。

作文类型：{exam_type}
任务子类型：{exam_subtype}
作文题目：{essay_topic}
{image_context}
作文原文：
{essay_text}

参考评分细则/检索片段：
{retrieved_context}

公开评分描述（仅供参考写作标准，不需要你打分）：
{rubric_instruction}

语法检查工具（本地规则库+LanguageTool）实际检测到的问题列表（写grammar维度
反馈时以这份真实检测结果为主要依据，不要凭自己重新通读一遍猜测；如果这份
列表是空的，说明工具没检测到明显问题，可以正常评价语法总体表现）：
{grammar_tool_findings}
{critic_revision_note}
请按下面4个通用维度给出详细反馈（键名固定为content/coherence/language/grammar，
不要漏掉任何一个维度），每个维度内容要丰富具体（不用担心篇幅，学生需要充分的
讲解）：
- content（内容主旨）：论点是否清楚、切题、论证是否充分
- coherence（结构与衔接）：段落安排、逻辑推进、过渡衔接
- language（语言运用）：词汇丰富度、用词准确性、表达是否地道；如果需要确认某个
  具体单词的释义/同义词/地道用法，可以调用`dictionary_lookup`工具查证后再写进
  反馈，不确定的词才需要查，常见词不用每个都查
- grammar（语法多样性与准确性）：句式多样性、语法准确性、标点使用

只返回一个合法JSON对象，不要使用Markdown代码围栏，也不要在JSON外写任何内容；
字符串内容里如果需要引用或强调某个具体的词、短语或句子，请用中文的直角引号
或书名号（例如「」或《》），不要用英文半角双引号，因为字符串内部出现未转义
的英文双引号会破坏JSON格式、导致整份内容解析失败：
{{
  "overall_summary": "2-3句话的总体评价，说清楚这篇作文最突出的优点和最需要改进的一点，给正在等结果的学生看的第一段话",
  "dimension_feedback": {{
    "content": {{
      "strengths": "内容主旨维度的优势点，2-3句话具体展开，引用作文原文片段作为证据",
      "improvements": "内容主旨维度最值得改进的地方，2-3句话具体展开，引用作文原文片段作为证据",
      "tips": [{{"title": "改进方向的简短标题", "comment": "具体怎么改，2-3句话讲清楚做法和原因", "example": "给出一个具体的改写示例"}}]
    }},
    "coherence": {{结构与衔接维度，同上结构}},
    "language": {{语言运用维度，同上结构}},
    "grammar": {{语法多样性与准确性维度，同上结构}}
  }}
}}
每个维度给2~3条tips，具体可执行、附带实际改写示例。

这是依据公开量表的模拟对照，不得自称正式考官或考试机构成绩。"""


# 节点5：打分（DeepSeek V4 Pro）+ 定性反馈（DeepSeek/GLM，语言维度可查词典）分开调用，各自解析
def feedback_agent_node(state: EssayReviewState) -> EssayReviewState:
    from src.agents.llm import get_chat_model_with_fallback, get_primary_chat_model, get_scoring_chat_model
    from src.exam_types import GENERAL
    from src.official_rubrics import (
        normalize_rubric_result,
        parse_llm_json,
        rubric_instruction,
    )

    exam_type = state.get("exam_type") or GENERAL
    exam_subtype_raw = state.get("exam_subtype")
    exam_subtype = exam_subtype_raw or "不适用"
    essay_topic = state.get("essay_topic") or "未提供"
    essay_text = state.get("essay_text", "")
    rubric_text = rubric_instruction(exam_type, exam_subtype_raw)

    image_analysis = state.get("image_analysis")
    image_context = (
        f"图片内容描述（图片理解模型对本题所附图表/图片的客观描述，供核对作文数据\n描述是否准确，你看不到原图，只能依据这段描述判断）：\n{image_analysis}\n"
        if image_analysis
        else ""
    )

    grammar_errors = state.get("grammar_errors") or []
    if grammar_errors:
        findings_lines = [f"- {e.get('message', '')}：「{e.get('context', '')}」" for e in grammar_errors[:20]]
        grammar_tool_findings = "\n".join(findings_lines)
    else:
        grammar_tool_findings = "（本地规则库+LanguageTool均未检测到明显问题）"

    # 打分固定走DeepSeek V4 Pro（get_scoring_chat_model()）；定性反馈仍走DeepSeek/GLM。
    # 两次调用独立try/except，一次失败不会连累另一次已经拿到的结果被丢弃。
    score_payload: dict = {}
    score_raw = ""
    score_prompt = SCORE_RUBRIC_PROMPT.format(
        exam_type=exam_type,
        exam_subtype=exam_subtype,
        essay_topic=essay_topic,
        essay_text=essay_text,
        image_context=image_context,
        rubric_instruction=rubric_text,
        few_shot_example=_score_few_shot_example(exam_type, exam_subtype_raw),
    )
    # 偶发漏掉rubric量表要求的某个键（比如IELTS Task1的task_achievement）时，
    # 同一个prompt重试一次通常就能拿到完整字段，比直接判定"本次打分失败"更
    # 划算，最多重试1次（2次机会）。
    for attempt in range(2):
        try:
            score_llm = get_scoring_chat_model().bind(
                response_format={"type": "json_object"}
            )
            score_raw = score_llm.invoke(score_prompt).content
            parsed = parse_llm_json(score_raw)
            if "rubric_scores" not in parsed and parsed:
                # 分数键直接摊平在顶层、没套"rubric_scores"这层嵌套的兜底，
                # 即使prompt里给了嵌套的JSON示例，偶尔还是会发生。
                parsed = {"rubric_scores": parsed}
            # 提前校验一次是否包含该考试类型要求的全部键，缺字段这里就能发现，
            # 不用等到下面normalize_rubric_result才报错、错过重试机会。
            normalize_rubric_result(exam_type, parsed, exam_subtype=exam_subtype_raw)
            score_payload = parsed
            break
        except Exception as exc:  # noqa: BLE001
            if attempt == 0:
                continue
            _warn_json_parse_failure("feedback_agent_node（打分）", exc, score_raw)

    # critic_agent_node复核不通过时会把具体问题写进state["critic_notes"]、
    # 图往回打到这个节点重新生成，见src/agents/graph.py的route_after_critic()。
    # 这里注意：重新生成时打分也会跟着重跑一遍（feedback_agent_node没有单独
    # 拆出"只重跑反馈、复用上一轮分数"的路径）——critic只复核定性反馈质量、
    # 不复核分数，重新打分理论上是多余的一次调用，但拆分需要额外在state里
    # 缓存原始英文键的rubric_scores（当前只保留转成中文展示名之后的
    # score_details，无法逆向还原），复杂度换来的收益不成正比，这条重试路径
    # 本身就封顶1次（见critic_agent_node），接受这一次重复打分的成本。
    critic_notes = state.get("critic_notes")
    critic_revision_note = (
        f"上一轮反馈未通过质量复核，具体问题：{critic_notes}\n"
        "请在这一轮重新生成时明确修正上述问题，不要重复同样的空泛表述。\n"
        if critic_notes
        else ""
    )
    feedback_prompt = FEEDBACK_ONLY_PROMPT.format(
        exam_type=exam_type,
        exam_subtype=exam_subtype,
        essay_topic=essay_topic,
        essay_text=essay_text,
        image_context=image_context,
        retrieved_context="\n".join(state.get("retrieved_context", [])),
        rubric_instruction=rubric_text,
        grammar_tool_findings=grammar_tool_findings,
        critic_revision_note=critic_revision_note,
    )

    def _generate_feedback_with_tools() -> str:
        # language维度写反馈时可以查词典核实具体用词，和coach_agent_node同样的
        # 工具调用写法（get_primary_chat_model()而不是get_chat_model_with_fallback()，
        # 绑工具+fallback一起用没有实测过，不确定行为，索性只在主力模型上绑工具，
        # 主力模型本身失败时下面except块整体降级成不查词的单次调用）。
        from langchain_core.messages import HumanMessage, ToolMessage

        from src.agents.tools import dictionary_lookup

        # strict=True是真实调用报错才发现必须加的：response_format=json_object
        # 和bind_tools一起用时，openai SDK底层会走结构化输出的"auto-parse"校验
        # 路径，这条路径要求每个工具的function schema都标了strict才允许自动解析，
        # 不加会在真实请求时报"`dictionary_lookup` is not strict"，本地没装
        # 真实langchain_openai/openai包之前完全测不出这个问题。
        llm_with_tools = get_primary_chat_model().bind_tools([dictionary_lookup], strict=True).bind(
            response_format={"type": "json_object"}
        )
        messages = [HumanMessage(content=feedback_prompt)]
        ai_message = llm_with_tools.invoke(messages)
        messages.append(ai_message)
        for _ in range(2):
            tool_calls = getattr(ai_message, "tool_calls", None)
            if not tool_calls:
                break
            for call in tool_calls:
                result = dictionary_lookup.invoke(call["args"])
                messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
            ai_message = llm_with_tools.invoke(messages)
            messages.append(ai_message)
        return ai_message.content

    feedback_payload: dict = {}
    feedback_raw = ""
    try:
        feedback_raw = _generate_feedback_with_tools()
        feedback_payload = parse_llm_json(feedback_raw)
    except Exception as exc:  # noqa: BLE001
        import warnings

        warnings.warn(f"feedback_agent_node（定性反馈，工具调用路径）失败（{exc}），降级为不查词的普通生成重试一次。")
        try:
            feedback_llm = get_chat_model_with_fallback().bind(response_format={"type": "json_object"})
            feedback_raw = feedback_llm.invoke(feedback_prompt).content
            feedback_payload = parse_llm_json(feedback_raw)
        except Exception as exc2:  # noqa: BLE001
            _warn_json_parse_failure("feedback_agent_node（定性反馈，重试后仍失败）", exc2, feedback_raw)

    try:
        rubric_result = normalize_rubric_result(
            exam_type,
            {**score_payload, **feedback_payload},
            word_count=len(essay_text.split()),
            exam_subtype=exam_subtype_raw,
        )
    except (TypeError, ValueError, KeyError) as exc:
        rubric_result = {
            "qualitative_feedback": "本次评分响应格式异常，未生成可用数值分。",
            "feedback_dimensions": {},
            "overall_summary": "",
            "official_rubric_scores": {},
            "official_rubric_label": None,
            "official_rubric_score": None,
            "official_rubric_max": None,
            "score_source": "llm_rubric",
            "primary_score": None,
            "primary_max": None,
            "primary_label": None,
            "score_details": {},
            "score_error": str(exc),
            "rubric_parse_error": str(exc),
        }
    return {**state, **rubric_result, "score_error": rubric_result.get("score_error")}


CRITIC_PROMPT = """你是英语写作反馈的质量审核员，负责在反馈交付给学生之前做一次
复核，不是重新评阅这篇作文。请判断下面这份反馈是否合格，合格标准：
1. 反馈是否具体引用了作文原文里的实际内容/句子作为证据，而不是"内容丰富""语言
   流畅"这类不结合原文的空泛套话；
2. 总体评价（overall_summary）和四个维度的优势点/待改进是否互相一致，没有明显
   自相矛盾（比如总体说"论证充分"但content维度又说"缺乏论证"）；
3. 各维度的tips是否具体可执行，而不是"多练习""多积累词汇"这类空洞建议。

作文原文：
{essay_text}

待审核的反馈：
总体评价：{overall_summary}
{dimension_feedback_text}

只返回一个合法JSON对象，不要使用Markdown代码围栏，也不要在JSON外写任何内容：
{{
  "approved": true或false,
  "notes": "如果不合格，具体指出哪里不合格、应该怎么改；如果合格，留空字符串"
}}
从严要求但不要吹毛求疵——只有真的空泛/自相矛盾/不可执行才判不合格，不要因为
反馈不够长或者你自己想要更多细节就判不合格。"""


# 节点：CriticAgentNode反思循环，复核feedback_agent_node产出的定性反馈质量，
# 不合格则由src/agents/graph.py的route_after_critic()打回feedback_agent_node
# 重新生成（封顶1次重试，不是无限循环）。只复核定性反馈，不复核数值评分——
# 打分已经有自己的"缺字段重试"机制，且评分对错更适合靠公开量表本身的客观
# 描述约束，不是"像不像空泛套话"这种适合LLM复核的问题。
def critic_agent_node(state: EssayReviewState) -> EssayReviewState:
    revision_count = state.get("critic_revision_count") or 0
    if revision_count >= 1:
        # 已经打回重写过1次，不管这次质量如何都直接放行，避免反思循环无限
        # 重试拖慢响应时间、推高成本——和打分节点"最多重试1次"是同一个尺度。
        return {**state, "critic_approved": True, "critic_notes": None}

    feedback_dimensions = state.get("feedback_dimensions") or {}
    if not feedback_dimensions:
        # 反馈本身生成失败（上游已经拿到空结果）时，critic复核没有意义，
        # 直接放行——这种情况该报的错已经在feedback_agent_node里报过了。
        return {**state, "critic_approved": True, "critic_notes": None}

    from src.agents.llm import get_chat_model_with_fallback
    from src.official_rubrics import parse_llm_json

    dimension_lines = [
        f"【{label}】优势点：{dim.get('strengths', '')}；待改进：{dim.get('improvements', '')}"
        for label, dim in feedback_dimensions.items()
    ]
    prompt = CRITIC_PROMPT.format(
        essay_text=state.get("essay_text", ""),
        overall_summary=state.get("overall_summary", ""),
        dimension_feedback_text="\n".join(dimension_lines),
    )
    try:
        critic_llm = get_chat_model_with_fallback().bind(response_format={"type": "json_object"})
        raw = critic_llm.invoke(prompt).content
        result = parse_llm_json(raw)
        approved = bool(result.get("approved", True))
        notes = str(result.get("notes") or "").strip() if not approved else None
    except Exception as exc:  # noqa: BLE001 - 复核本身失败不应该拖垮整条链路，直接放行
        import warnings

        warnings.warn(f"critic_agent_node复核失败（{exc}），本次跳过复核直接放行。")
        approved, notes = True, None

    return {
        **state,
        "critic_approved": approved,
        "critic_notes": notes,
        "critic_revision_count": revision_count + (0 if approved else 1),
    }


COACH_PROMPT = """你是一名英语写作辅导教练。基于下面这份对某篇作文的定性反馈，
以及该学生的历史提交摘要（如果有），生成一份结构化的修改计划，并额外创作一篇
同题目的高分范文供学生对照学习。

定性反馈：
{qualitative_feedback}

作文题目：
{essay_topic}

该学生历史提交摘要：
{history_summary}

如果修改建议、练习题或范文里会用到某个具体单词/词组的释义、同义词或地道例句，
你可以调用`dictionary_lookup`工具查证后再写进去，不要凭空编造词义或用法；
不确定的词才需要查，常见词不用每个都查。

内容要丰富具体，不用担心篇幅。只返回一个合法JSON对象，不要使用Markdown代码
围栏，也不要在JSON外写任何内容；字符串内容里如果需要引用或强调某个具体的词、
短语或句子，请用中文的直角引号或书名号（例如「」或《》），不要用英文半角
双引号，因为字符串内部出现未转义的英文双引号会破坏JSON格式、导致整份内容
解析失败：
{{
  "action_items": [
    {{"title": "改进方向的简短标题", "detail": "具体改什么、为什么，2-3句话讲清楚"}}
  ],
  "exercises": [
    {{"title": "练习标题", "instruction": "具体练习内容/要求，比如'用过去完成时重写这句话：……'"}}
  ],
  "model_essay": {{
    "title": "给这篇范文拟一个简短标题",
    "text": "一篇针对同一题目的高分范文全文，250-350词，语言地道、结构清晰、论证充分",
    "highlights": ["范文里值得学习的写作技巧点，1-2句话说清楚好在哪", "..."]
  }}
}}
action_items给2~3条，按优先级排序；exercises给1~2条；model_essay必须生成，
highlights给2~3条。这是AI根据本次反馈现场创作的范文，不是真实考生作文，
不得自称官方范文或真实高分卷。"""


def build_coach_plan(payload: dict) -> dict:
    """把LLM返回的辅导计划原始dict，防御性规整成
    ``{action_items, exercises, model_essay}``——任何字段缺失/类型不对都不
    报错，只是对应内容留空，避免格式异常拖垮整个辅导环节。"""
    payload = payload or {}

    def _list_of(key: str, item_keys: tuple[str, ...]) -> list[dict]:
        items = []
        for raw_item in payload.get(key) or []:
            if not isinstance(raw_item, dict):
                continue
            entry = {k: str(raw_item.get(k) or "").strip() for k in item_keys}
            if any(entry.values()):
                items.append(entry)
        return items

    model_essay_raw = payload.get("model_essay")
    model_essay_raw = model_essay_raw if isinstance(model_essay_raw, dict) else {}
    highlights = [
        str(h).strip() for h in (model_essay_raw.get("highlights") or []) if str(h).strip()
    ]

    return {
        "action_items": _list_of("action_items", ("title", "detail")),
        "exercises": _list_of("exercises", ("title", "instruction")),
        "model_essay": {
            "title": str(model_essay_raw.get("title") or "").strip(),
            "text": str(model_essay_raw.get("text") or "").strip(),
            "highlights": highlights,
        },
    }


def flatten_coach_plan(coach_plan: dict) -> str:
    """把结构化的``coach_plan``拍平成一段Markdown文本，供没有卡片渲染能力的
    旧历史记录兜底展示。"""
    lines = []
    action_items = coach_plan.get("action_items") or []
    if action_items:
        lines.append("### 优先修改清单")
        for item in action_items:
            lines.append(f"- **{item['title']}**：{item['detail']}")
    exercises = coach_plan.get("exercises") or []
    if exercises:
        lines.append("### 针对性练习")
        for item in exercises:
            lines.append(f"- **{item['title']}**：{item['instruction']}")
    model_essay = coach_plan.get("model_essay") or {}
    if model_essay.get("text"):
        lines.append(f"### 高分范文：{model_essay.get('title') or '参考范文'}")
        lines.append(model_essay["text"])
        for highlight in model_essay.get("highlights") or []:
            lines.append(f"- {highlight}")
    return "\n".join(lines)

# 节点6：结合当前反馈和历史摘要，生成下一步可执行练习计划+同题高分范文
def coach_agent_node(state: EssayReviewState) -> EssayReviewState:

    from langchain_core.messages import HumanMessage, ToolMessage

    from src.agents.llm import get_chat_model_with_fallback, get_primary_chat_model
    from src.agents.tools import dictionary_lookup
    from src.official_rubrics import parse_llm_json

    prompt = COACH_PROMPT.format(
        qualitative_feedback=state.get("qualitative_feedback", ""),
        essay_topic=state.get("essay_topic") or "未提供",
        history_summary=state.get("history_summary") or "（该学生暂无历史提交记录）",
    )

    def _generate_with_tools() -> str:
        # 强制JSON对象输出，
        # strict=True是真实调用报错才发现必须加的：response_format=json_object
        # 和bind_tools一起用时，openai SDK底层会走结构化输出的"auto-parse"校验
        # 路径，这条路径要求每个工具的function schema都标了strict才允许自动解析，
        # 不加会在真实请求时报"`dictionary_lookup` is not strict"，本地没装
        # 真实langchain_openai/openai包之前完全测不出这个问题。
        llm_with_tools = get_primary_chat_model().bind_tools([dictionary_lookup], strict=True).bind(
            response_format={"type": "json_object"}
        )
        messages = [HumanMessage(content=prompt)]
        ai_message = llm_with_tools.invoke(messages)
        messages.append(ai_message)

        # 调用第三方工具
        for _ in range(2):
            tool_calls = getattr(ai_message, "tool_calls", None)
            if not tool_calls:
                break
            for call in tool_calls:
                result = dictionary_lookup.invoke(call["args"])
                messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
            ai_message = llm_with_tools.invoke(messages)
            messages.append(ai_message)
        return ai_message.content

    def _finish(coach_plan: dict) -> EssayReviewState:
        revision_plan = flatten_coach_plan(coach_plan).strip()
        return {
            **state,
            "coach_plan": coach_plan,
            "revision_plan": revision_plan or "本次未能生成结构化辅导计划，请重新提交。",
        }

    raw_content = ""
    try:
        raw_content = _generate_with_tools()
        coach_plan = build_coach_plan(parse_llm_json(raw_content))
    except Exception as exc:
        import warnings

        warnings.warn(f"coach_agent_node首次生成/解析失败（{exc}），降级为不查词的普通生成重试一次。")
        try:
            raw_content = (
                get_chat_model_with_fallback()
                .bind(response_format={"type": "json_object"})
                .invoke(prompt)
                .content
            )
            coach_plan = build_coach_plan(parse_llm_json(raw_content))
        except Exception as exc2:
            _warn_json_parse_failure("coach_agent_node（重试后仍失败）", exc2, raw_content)
            coach_plan = {"action_items": [], "exercises": [], "model_essay": {}}

    return _finish(coach_plan)


# 节点7：将本次批改的分数、画像、反馈和辅导计划保存到历史记录。
def progress_tracker_node(state: EssayReviewState) -> EssayReviewState:
    """把完整批改结果落库，供历史趋势和下一次个性化建议复用。"""
    from src.storage import db  # 懒加载：db.py需要psycopg，见该文件顶部说明

    db.save_submission(state)
    return state


def short_circuit_reject_node(state: EssayReviewState) -> EssayReviewState:
    return state


KB_QA_PROMPT = """你是一名英语写作知识库助手，面向中国的英语学习者（通用英语写作/
托福/雅思写作场景）。请只根据下面检索到的知识库片段回答用户的问题，不要编造
片段里没有的内容；如果片段里没有能回答这个问题的信息，直接说"知识库里没有找到
相关内容"，不要凭空编造。

检索到的知识库片段：
{retrieved_context}

用户问题：{question}

用中文回答，具体、可操作，如果引用了片段里的规则/评分标准，可以直接引用原文。"""

GENERAL_WRITING_QA_PROMPT = """你是一名英语写作辅导老师。知识库没有足够信息回答下面的
问题，请使用你的通用英语写作知识给出简明、准确、可操作的中文回答。不要假装这来自
知识库；如果问题与英语写作无关，明确说明你只能协助英语写作学习。

用户问题：{question}
"""

_KB_MISS_MARKERS = ("知识库里没有找到", "没有找到相关内容", "未找到相关内容")


def answer_kb_question(question: str, exam_type: str | None = None) -> str:
    """独立的知识库问答入口，供`pages/2_工作台.py`“写作知识库问答”页调用。

    不复用`retrieval_agent_node`/`feedback_agent_node`（那两个是LangGraph
    节点，输入输出格式是`EssayReviewState`，为一次完整的"提交批改"服务），
    这里是更轻量的"问题进、答案出"的直接调用，检索逻辑复用同一个Chroma库
    和exam_type过滤规则，但不需要走完整的Graph。
    """
    from src.agents.llm import get_chat_model_with_fallback

    fake_state: EssayReviewState = {"essay_text": question, "essay_topic": question}
    if exam_type:
        fake_state["exam_type"] = exam_type
    retrieved = retrieval_agent_node(fake_state)["retrieved_context"]

    llm = get_chat_model_with_fallback()
    prompt = KB_QA_PROMPT.format(
        retrieved_context="\n\n".join(retrieved),
        question=question,
    )
    response = llm.invoke(prompt)
    answer = response.content
    if any(marker in answer for marker in _KB_MISS_MARKERS):
        fallback = llm.invoke(GENERAL_WRITING_QA_PROMPT.format(question=question))
        answer = "以下为通用英语写作建议（非知识库原文）：\n\n" + fallback.content
    return answer
