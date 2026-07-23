"""作文类型与RAG细则的单一配置源。"""
from __future__ import annotations

GENERAL = "通用英语作文评测"
IELTS = "雅思（IELTS）"
TOEFL = "托福（TOEFL）"

EXAM_TYPE_CONFIG: dict[str, dict] = {
    GENERAL: {"rubric_file": "exam_rubrics/general.md"},
    IELTS: {"rubric_file": "exam_rubrics/ielts.md"},
    TOEFL: {"rubric_file": "exam_rubrics/toefl.md"},
}

EXAM_TYPE_OPTIONS = [GENERAL, IELTS, TOEFL]
TOEFL_SUBTYPES = ["Write for an Academic Discussion", "Write an Email"]

# IELTS Task 1（学术类，图表/表格/流程图/地图描述）和Task 2（议论文）评分维度不同
# （Task Achievement vs Task Response），需要单独的量表和图片上传，见
# src/official_rubrics.py、pages/2_工作台.py。
IELTS_TASK2 = "IELTS Writing Task 2（议论文）"
IELTS_TASK1 = "IELTS Writing Task 1（图表/图片描述）"
IELTS_SUBTYPES = [IELTS_TASK2, IELTS_TASK1]


def exam_config(exam_type: str) -> dict:
    return EXAM_TYPE_CONFIG.get(exam_type, EXAM_TYPE_CONFIG[GENERAL])


def rubric_file_for_exam_type(exam_type: str) -> str | None:
    return exam_config(exam_type).get("rubric_file")
