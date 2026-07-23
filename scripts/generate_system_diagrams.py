"""生成可用于报告/PPT的系统工程图，输出到 03-项目效果截图/system。"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
OUT = next(path for path in ROOT.iterdir() if path.name == "03-项目效果截图") / "system"
FONT = "Microsoft YaHei"
INK, MUTED, LINE = "#172033", "#60708A", "#CBD5E1"
BLUE, PURPLE, ORANGE, GREEN = "#5B7CFA", "#8B6CF6", "#F59E0B", "#14B8A6"


def setup(fig, title, subtitle):
    fig.patch.set_facecolor("#F8FAFC")
    fig.text(.05, .93, title, fontsize=21, fontweight="bold", color=INK, fontname=FONT)
    fig.text(.05, .885, subtitle, fontsize=10.5, color=MUTED, fontname=FONT)


def box(ax, x, y, w, h, label, color=BLUE, detail=None):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.025",
                           facecolor="white", edgecolor=color, linewidth=1.8)
    ax.add_patch(patch)
    ax.text(x+w/2, y+h*.61, label, ha="center", va="center", fontsize=12, fontweight="bold", color=INK, fontname=FONT)
    if detail:
        ax.text(x+w/2, y+h*.30, detail, ha="center", va="center", fontsize=8.7, color=MUTED, fontname=FONT, wrap=True)


def arrow(ax, start, end, text=None):
    ax.annotate("", end, start, arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.6, shrinkA=6, shrinkB=6))
    if text:
        ax.text((start[0]+end[0])/2, (start[1]+end[1])/2+.025, text, ha="center", fontsize=8.5, color=MUTED, fontname=FONT)


def architecture():
    fig, ax = plt.subplots(figsize=(14, 8)); ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    setup(fig, "慧笔 · 系统架构图", "Streamlit 交互层 + LangGraph 编排层 + 模型/RAG/数据持久化服务")
    box(ax,.06,.58,.20,.16,"Streamlit 工作台",BLUE,"提交批改 · 反馈详情\n进步仪表盘 · 知识库问答")
    box(ax,.39,.58,.22,.16,"LangGraph 编排",PURPLE,"校验 · 检索\n反馈 · 辅导 · 入库")
    box(ax,.75,.74,.18,.13,"公开评分量表",ORANGE,"雅思Band/托福单题\nGENERAL四维度")
    box(ax,.75,.53,.18,.13,"RAG 知识库",GREEN,"评分细则/语法卡\nChroma 向量检索")
    box(ax,.75,.32,.18,.13,"LLM 服务",PURPLE,"反馈生成 · 教练计划\nDeepSeek / GLM 兜底")
    box(ax,.39,.25,.22,.14,"SQLite 持久化",GREEN,"用户、批改记录\n趋势与学习画像")
    arrow(ax,(.26,.66),(.39,.66),"提交 / 查看")
    arrow(ax,(.61,.69),(.75,.80),"数值评分")
    arrow(ax,(.61,.65),(.75,.59),"检索细则")
    arrow(ax,(.61,.61),(.75,.38),"生成反馈")
    arrow(ax,(.50,.58),(.50,.39),"保存结果")
    arrow(ax,(.39,.32),(.26,.58),"历史数据")
    fig.savefig(OUT / "05_系统架构图.png", dpi=220, bbox_inches="tight"); plt.close(fig)


def sequence():
    fig, ax = plt.subplots(figsize=(14, 8.4)); ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    setup(fig, "慧笔 · 作文批改时序图", "一次有效提交从界面输入到历史仪表盘更新的关键交互")
    actors = [("学习者", .11), ("Streamlit", .29), ("LangGraph", .48), ("模型 / RAG / LLM", .70), ("SQLite", .89)]
    for name, x in actors:
        ax.text(x,.82,name,ha="center",fontsize=12,fontweight="bold",color=INK,fontname=FONT)
        ax.plot([x,x],[.15,.78],color=LINE,lw=1.25,ls="--")
    events = [
        (.75,.11,.29,"提交作文"), (.68,.29,.48,"创建状态并校验词数"),
        (.61,.48,.70,"检索题型细则"), (.54,.48,.70,"语法检查 / 量表数值评分"),
        (.47,.48,.70,"生成反馈与练习计划"), (.40,.48,.89,"保存批改记录"),
        (.33,.89,.29,"返回评分与反馈"), (.25,.11,.29,"查看趋势与学习画像"),
        (.18,.29,.89,"读取历史记录"),
    ]
    for y, x1, x2, label in events:
        ax.annotate("",(x2,y),(x1,y),arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.7))
        ax.text((x1+x2)/2,y+.018,label,ha="center",va="bottom",fontsize=9.2,color=INK,fontname=FONT,
                bbox=dict(boxstyle="round,pad=.2",fc="#FFFFFF",ec="none",alpha=.96))
    ax.text(.48,.12,"若词数不合规，LangGraph 直接短路返回，不调用模型或 LLM。",ha="center",fontsize=9.5,color=MUTED,fontname=FONT)
    fig.savefig(OUT / "06_作文批改时序图.png", dpi=220, bbox_inches="tight"); plt.close(fig)


def scoring_flow():
    fig, ax = plt.subplots(figsize=(14, 6)); ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    setup(fig, "慧笔 · 量化评分流程", "GENERAL/IELTS/TOEFL统一走LLM+对应公开评分量表")
    box(ax,.08,.42,.20,.18,"作文 + 考试类型",BLUE,"essay_text · exam_type")
    box(ax,.38,.42,.24,.18,"公开评分量表说明",ORANGE,"雅思Band/托福单题指南\nGENERAL四维度标准")
    box(ax,.72,.42,.20,.18,"结构化对照分",GREEN,"official_rubric_scores\n+ 定性反馈")
    arrow(ax,(.28,.51),(.38,.51),"注入Prompt")
    arrow(ax,(.62,.51),(.72,.51),"LLM生成+解析")
    ax.text(.50,.12,"两条自训练评分模型（微调DistilBERT+自建BiLSTM）已删除，不再是当前的量化评分路径。",
            ha="center", fontsize=9.5, color=MUTED, fontname=FONT)
    fig.savefig(OUT / "07_量化评分流程图.png", dpi=220, bbox_inches="tight"); plt.close(fig)


def entity(ax, x, y, w, title, fields, color):
    """绘制带字段清单的实体；PK/逻辑关联字段在图内明确标识。"""
    h = .075 + len(fields) * .043
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor="white", edgecolor=color, linewidth=1.8))
    ax.add_patch(FancyBboxPatch((x, y+h-.07), w, .07, boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=color, edgecolor=color, linewidth=1.0))
    ax.text(x+w/2, y+h-.035, title, ha="center", va="center", fontsize=13, fontweight="bold", color="white", fontname=FONT)
    for index, field in enumerate(fields):
        ax.text(x+.025, y+h-.105-index*.043, field, ha="left", va="center", fontsize=9.4, color=INK, fontname=FONT)
    return h


def er_diagram():
    """从 db.py 的实际 SQLite schema 提炼 ER 图，不虚构数据库外键。"""
    fig, ax = plt.subplots(figsize=(14, 8)); ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    setup(fig, "慧笔 · SQLite 数据库 ER 图", "用户与批改记录的逻辑一对多关系；当前由应用层维护，不设 SQLite 外键约束")
    user_h = entity(ax, .10, .35, .29, "users（用户）", [
        "PK  id : INTEGER", "UK  username : TEXT", "password_hash : TEXT", "salt : TEXT", "created_at : TEXT",
    ], BLUE)
    submission_h = entity(ax, .60, .13, .31, "submissions（批改记录）", [
        "PK  id : INTEGER", "LK  user_id : TEXT → users.username", "exam_type / exam_subtype / essay_topic",
        "primary_score / secondary_score / score_source", "official_rubric_scores / score_details (JSON)", "qualitative_feedback / revision_plan", "created_at : TEXT",
    ], GREEN)
    # 虚线表示这是查询/写入逻辑维系的关联，而不是数据库声明的 FOREIGN KEY。
    ax.annotate("", (.60, .45), (.39, .48), arrowprops=dict(arrowstyle="->", color=PURPLE, lw=2, linestyle="--"))
    ax.text(.495, .515, "1 位用户", ha="center", fontsize=11, color=INK, fontname=FONT)
    ax.text(.495, .425, "0..N 条批改记录", ha="center", fontsize=11, color=INK, fontname=FONT)
    ax.text(.50, .08, "说明：official_rubric_scores、score_details 以 JSON 文本保存，供反馈详情与历史进步仪表盘读取。",
            ha="center", fontsize=9.5, color=MUTED, fontname=FONT)
    fig.savefig(OUT / "08_SQLite_ER图.png", dpi=220, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    architecture(); sequence(); scoring_flow(); er_diagram()
    print(f"Generated diagrams in {OUT}")
