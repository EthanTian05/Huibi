"""按公开官方量表生成可审计的“模拟评阅”配置。

这里刻意不把系统输出称为官方成绩：正式 IELTS/TOEFL 也由官方考官和官方评分
系统完成，GENERAL 更是没有对应的官方考试。本模块只约束 LLM 按公开评分描述
（或 GENERAL 的通用写作评估框架）给出结构化对照分。
"""
from __future__ import annotations

import json
import math
from typing import Any

from src.exam_types import GENERAL, IELTS, IELTS_TASK1, TOEFL

# 所有考试类型的定性反馈统一按这四个维度展示（内容主旨/结构与衔接/语言运用/
# 语法多样性与准确性），不再跟着每种考试自己的官方评分维度走（IELTS官方也是
# 四维度但键名不同、TOEFL官方只有一个单题分、GENERAL是自定义四维度）——官方
# 维度仍然用于`rubric_scores`的数值评分（IELTS Band/TOEFL单题分/GENERAL四维度
# 的计算不受影响），只有定性反馈这一层统一成这四块，方便学生跨考试类型对照、
# 前端卡片数量和顺序也保持一致。GENERAL/IELTS/TOEFL三种当前支持的考试类型
# 统一走LLM+对应公开评分量表这一条路径（不再区分"AB模型场景"），
# `src/agents/nodes.py`的`LLM_RUBRIC_PROMPT`要求LLM按这四个英文key
# （content/coherence/language/grammar）返回`dimension_feedback`，和
# `rubric_scores`自己的键名（IELTS是task_response等）是两套完全独立的key，
# 解析时不要混用。
DIMENSION_LABELS = {
    "内容主旨": "content",
    "结构与衔接": "coherence",
    "语言运用": "language",
    "语法多样性与准确性": "grammar",
}


RUBRIC_INSTRUCTIONS = {
    GENERAL: """本评测不对应任何单一官方考试，用于通用英语写作能力练习，按国际
通用的学术写作评估四维度框架分别给0-25整数分，不要互相拉平：内容与任务完成
（是否切题、观点是否清楚、论证/说明是否具体充分）；结构与衔接（段落安排是否
合理、逻辑推进是否清楚、过渡衔接是否自然）；语言运用与词汇（词汇范围与准确性、
表达是否地道、句式是否有变化）；语法准确性（语法错误的数量与严重程度、错误
对理解造成的干扰程度）。空白、完全离题、只有孤立词语等无有效作答的维度应
打0分。输出键必须为 content_score、organization_score、language_score、
grammar_score，均为0到25之间的整数，系统按四项求和得到0-100总分。""",
    TOEFL: """采用ETS 2026版TOEFL iBT Writing单题评分指南。先从题目判断任务是
Write an Email还是Write for an Academic Discussion；本系统不根据一篇作文推算完整
Writing section的1-6分，因为正式写作部分还包含Build a Sentence等任务。
单题按0-5整数评分：5=任务完全成功、展开有效、表达清晰、句法词汇运用成熟且几乎
无错误；4=总体成功、展开充分、易于理解、错误很少；3=部分成功，展开或语言能力
存在明显限制；2=大多不成功，内容展开和语言能力有限；1=内容极少、几乎不能形成
扩展文本；0=空白、拒答、非英语、完全抄题、完全无关或任意字符。Email还必须评估
交际目的、礼貌、语域和信息组织；Academic Discussion必须评估是否切题、是否回应
讨论、解释/例证是否充分及学术语气。只输出一个键 task_score，取0到5的整数。""",
    IELTS: """采用IELTS Writing Task 2公开Band Descriptors。分别给四个标准0-9整数
Band：Task Response（完整回应所有题目要求、立场清楚、观点相关且充分展开）；
Coherence and Cohesion（信息组织、逻辑推进、衔接、指代和分段）；Lexical Resource
（词汇范围、准确性、得体性、拼写及构词）；Grammatical Range and Accuracy
（句法范围、准确性、标点及错误对交流的影响）。评分必须满足对应Band的正面描述；
明显少于250词、答题不完整、背诵/抄题或错误影响理解时按描述限制相关维度。
输出键必须为 task_response、coherence_cohesion、lexical_resource、
grammar_accuracy。系统按四项等权平均并四舍五入到最近0.5得到本篇Task 2对照Band。""",
    IELTS_TASK1: """采用IELTS Writing Task 1（学术类，图表/表格/流程图/地图描述）
公开Band Descriptors。分别给四个标准0-9整数Band：Task Achievement（是否达到最低
150词、是否有清晰的总体趋势概述overview、是否准确选取并报告图表中的关键特征和
数据、数据引用是否与图片事实一致没有明显错误、Task 1不需要也不应该给出个人观点
或建议）；Coherence and Cohesion（信息组织、段落安排、逻辑顺序、衔接手段和指代
是否清楚）；Lexical Resource（描述数据/趋势相关词汇的范围与准确性，比如
increase/decrease/fluctuate/peak等词汇是否多样且用得准确）；Grammatical Range
and Accuracy（句法范围、准确性、标点及错误对交流的影响）。评分必须满足对应Band
的正面描述；明显少于150词、遗漏overview、大量誊抄题目文字、或作文对图片数据的
描述与下方"图片内容描述"明显不符时按描述限制Task Achievement维度。下方会给出
一段图片理解模型对图表内容的客观描述（"图片内容描述"），请依据这段描述核对作文
里引用的数据/趋势是否准确，不需要也不能真的看到原图。输出键必须为
task_achievement、coherence_cohesion、lexical_resource、grammar_accuracy。
系统按四项等权平均并四舍五入到最近0.5得到本篇Task 1对照Band。""",
}


def rubric_instruction(exam_type: str, exam_subtype: str | None = None) -> str:
    key = IELTS_TASK1 if (exam_type == IELTS and exam_subtype == IELTS_TASK1) else exam_type
    if key not in RUBRIC_INSTRUCTIONS:
        raise ValueError(f"没有为{exam_type}配置评分标准")
    return RUBRIC_INSTRUCTIONS[key]


def parse_llm_json(content: str) -> dict[str, Any]:
    """兼容JSON前后说明、Markdown围栏及字符串内未转义换行。

    ``strict=False``只放宽JSON字符串中的控制字符；缺字段、错误类型和完全无法
    解析的响应仍由后续校验明确失败，绝不会用0分替代。
    """
    content = content.strip()
    try:
        return json.loads(content, strict=False)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("模型未返回可解析的JSON对象")
        return json.loads(content[start : end + 1], strict=False)


def _clamp(value: Any, low: float, high: float, *, integer: bool = True) -> float:
    number = max(low, min(high, float(value)))
    return float(math.floor(number + 0.5)) if integer else number


def _required_score(raw: dict, key: str) -> Any:
    if key not in raw:
        raise ValueError(f"LLM评分结果缺少字段: {key}")
    return raw[key]


def dimension_entry(raw: dict[str, Any] | None) -> dict[str, Any]:
    """把LLM返回的单个维度反馈原始dict，防御性规整成统一形状
    ``{strengths, improvements, tips}``——字段缺失/类型不对都不报错，只是
    对应内容留空，避免一个维度格式异常拖垮整篇反馈。"""
    raw = raw or {}
    tips = []
    for tip in raw.get("tips") or []:
        if not isinstance(tip, dict):
            continue
        title = str(tip.get("title") or "").strip()
        comment = str(tip.get("comment") or "").strip()
        if not (title or comment):
            continue
        tips.append({
            "title": title,
            "comment": comment,
            "example": str(tip.get("example") or "").strip(),
        })
    return {
        "strengths": str(raw.get("strengths") or "").strip(),
        "improvements": str(raw.get("improvements") or "").strip(),
        "tips": tips,
    }


def build_dimension_feedback(
    raw_dimension_feedback: dict[str, Any] | None, label_by_key: dict[str, str]
) -> dict[str, dict]:
    """按``{显示名: 原始key}``的映射，把LLM返回的``dimension_feedback``整理成
    ``{显示名: {strengths, improvements, tips}}``，用于前端渲染反馈卡片
    （见`src/ui_theme.py`的`render_feedback_dimensions()`）。"""
    raw_dimension_feedback = raw_dimension_feedback or {}
    return {
        label: dimension_entry(raw_dimension_feedback.get(key))
        for label, key in label_by_key.items()
    }


def flatten_dimension_feedback(feedback_dimensions: dict[str, dict]) -> str:
    """把结构化的``feedback_dimensions``拍平成一段Markdown文本，供
    `coach_agent_node`的上下文、以及没有卡片渲染能力的旧历史记录兜底展示。"""
    lines = []
    for label, dim in feedback_dimensions.items():
        lines.append(f"### {label}")
        if dim.get("strengths"):
            lines.append(f"- 优势点：{dim['strengths']}")
        if dim.get("improvements"):
            lines.append(f"- 待改进：{dim['improvements']}")
        for tip in dim.get("tips") or []:
            line = f"- **{tip['title']}**：{tip['comment']}"
            if tip.get("example"):
                line += f"（示例：{tip['example']}）"
            lines.append(line)
    return "\n".join(lines)


def normalize_rubric_result(
    exam_type: str,
    payload: dict[str, Any],
    *,
    word_count: int | None = None,
    exam_subtype: str | None = None,
) -> dict[str, Any]:
    raw = payload.get("rubric_scores") or {}
    if exam_type == TOEFL:
        keys = {"单题表现": "task_score"}
        scores = {name: _clamp(_required_score(raw, key), 0, 5) for name, key in keys.items()}
        score, maximum = scores["单题表现"], 5.0
        label = "TOEFL 写作单题评分指南对照（0–5）"
    elif exam_type == IELTS and exam_subtype == IELTS_TASK1:
        keys = {
            "任务完成情况": "task_achievement",
            "连贯与衔接": "coherence_cohesion",
            "词汇资源": "lexical_resource",
            "语法多样性与准确性": "grammar_accuracy",
        }
        scores = {name: _clamp(_required_score(raw, key), 0, 9) for name, key in keys.items()}
        average = sum(scores.values()) / len(scores)
        score, maximum = math.floor(average * 2 + 0.5) / 2, 9.0
        label = "IELTS Writing Task 1 标准对照 Band（0–9）"
    elif exam_type == IELTS:
        keys = {
            "任务回应": "task_response",
            "连贯与衔接": "coherence_cohesion",
            "词汇资源": "lexical_resource",
            "语法多样性与准确性": "grammar_accuracy",
        }
        scores = {name: _clamp(_required_score(raw, key), 0, 9) for name, key in keys.items()}
        average = sum(scores.values()) / len(scores)
        score, maximum = math.floor(average * 2 + 0.5) / 2, 9.0
        label = "IELTS Writing Task 2 标准对照 Band（0–9）"
    elif exam_type == GENERAL:
        keys = {
            "内容与任务完成": "content_score",
            "结构与衔接": "organization_score",
            "语言运用与词汇": "language_score",
            "语法准确性": "grammar_score",
        }
        scores = {name: _clamp(_required_score(raw, key), 0, 25) for name, key in keys.items()}
        score, maximum = sum(scores.values()), 100.0
        label = "通用英语写作能力对照评分（0–100，四维度各占25分）"
    else:
        raise ValueError(f"{exam_type}不是LLM数值评分类型")

    # 数值评分（rubric_scores/scores）仍然按考试官方维度（IELTS四项/TOEFL单题）
    # 计算，只有定性反馈这一层统一简化成DIMENSION_LABELS的四个维度，两者不是
    # 同一套键名，不要混用。
    feedback_dimensions = build_dimension_feedback(payload.get("dimension_feedback"), DIMENSION_LABELS)
    qualitative_feedback = flatten_dimension_feedback(feedback_dimensions).strip()
    overall_summary = str(payload.get("overall_summary") or "").strip()

    result = {
        "score_source": "llm_rubric",
        "primary_score": score,
        "primary_max": maximum,
        "primary_label": label,
        "secondary_score": None,
        "secondary_max": None,
        "secondary_label": None,
        "score_details": scores,
        "official_rubric_score": score,
        "official_rubric_max": maximum,
        "official_rubric_label": label,
        "official_rubric_scores": scores,
        "feedback_dimensions": feedback_dimensions,
        "overall_summary": overall_summary,
        "qualitative_feedback": qualitative_feedback or "本次未能生成结构化反馈，请重新提交。",
        "score_error": None,
    }
    return result
