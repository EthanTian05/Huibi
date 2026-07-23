"""工作台：提交批改 / 反馈详情 / 历史进步仪表盘 / 写作知识库问答，
对应Docs/01-系统架构与Agent设计.md「前端页面设计」。

这个页面需要先在`app.py`（产品介绍页）登录，登录状态存在
`st.session_state`里，Streamlit多页应用里session_state是跨页面共享的
（同一个浏览器会话），不需要重复登录。

运行：
    streamlit run app.py   # 入口仍是app.py，工作台通过页面顶部导航进入
"""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import altair as alt
import pandas as pd
import streamlit as st

from src.exam_types import EXAM_TYPE_OPTIONS, IELTS, IELTS_SUBTYPES, IELTS_TASK1, TOEFL, TOEFL_SUBTYPES
from src.storage import db
from src.ui_theme import (
    inject_theme,
    render_coach_plan,
    render_essay_with_highlights,
    render_feedback_dimensions,
    render_footer,
    render_grammar_error_cards,
    render_score_panel,
    render_top_nav,
    render_topic_card,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="工作台 · 慧笔 HuiBi", page_icon="✍️", layout="wide", initial_sidebar_state="collapsed"
)
inject_theme()
render_top_nav("workspace")

if not st.session_state.get("logged_in"):
    st.warning("请先登录后再使用工作台。")
    st.info("请前往登录页完成登录或注册。")
    st.page_link("pages/1_登录.py", label="前往登录页", icon="🔐")
    render_footer()
    st.stop()

user_id = st.session_state["username"]

if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "submission_executor" not in st.session_state:
    st.session_state.submission_executor = ThreadPoolExecutor(max_workers=1)
if "submission_future" not in st.session_state:
    st.session_state.submission_future = None
if "submission_task_id" not in st.session_state:
    st.session_state.submission_task_id = None
if "cancelled_submission_ids" not in st.session_state:
    st.session_state.cancelled_submission_ids = set()
if "pending_submission" not in st.session_state:
    st.session_state.pending_submission = None


def _number(value) -> float | None:
    if value is None:
        return None
    try:
        return None if pd.isna(value) else float(value)
    except (TypeError, ValueError):
        return None


def _normalized_score(record) -> float:
    primary, maximum = _number(record.get("primary_score")), _number(record.get("primary_max"))
    if primary is not None and maximum and maximum > 0:
        return max(0.0, min(1.0, primary / maximum))
    legacy, legacy_max = _number(record.get("official_rubric_score")), _number(record.get("official_rubric_max"))
    if legacy is not None and legacy_max and legacy_max > 0:
        return max(0.0, min(1.0, legacy / legacy_max))
    return 0.0


def _score_text(record) -> str:
    primary, maximum = _number(record.get("primary_score")), _number(record.get("primary_max"))
    if primary is not None and maximum:
        return f"{primary:g}/{maximum:g}"
    legacy, legacy_max = _number(record.get("official_rubric_score")), _number(record.get("official_rubric_max"))
    if legacy is not None and legacy_max:
        return f"{legacy:g}/{legacy_max:g}（旧记录）"
    return f"{_normalized_score(record) * 100:.0f}/100（旧记录）"


def _has_feedback_content(feedback_dimensions: dict) -> bool:
    """`feedback_dimensions`解析失败时`feedback_agent_node`会回退成`{}`，
    但也可能拿到一个非空字典、里面每个维度的字段却全是空的（比如LLM返回的
    JSON能解析、但内容本身是空字符串/空列表）——这种情况下`if feedback_dimensions`
    仍然是True，会走进卡片渲染分支却什么都渲不出来，页面只剩标题、内容空白。
    这个函数额外检查"是不是真的有内容"，不是只看字典是不是非空。"""
    return any(
        dim.get("strengths") or dim.get("improvements") or dim.get("tips")
        for dim in (feedback_dimensions or {}).values()
    )


def _has_coach_content(coach_plan: dict) -> bool:
    """道理同`_has_feedback_content`：`build_coach_plan()`解析失败时会返回
    `{"action_items": [], "exercises": [], "model_essay": {}}`这种"字典本身
    非空、但三个字段全是空"的结构，不额外检查内容会导致"个性化修改建议与
    练习推荐"标题下面直接空白，而不是回退显示`revision_plan`纯文本。"""
    coach_plan = coach_plan or {}
    model_essay = coach_plan.get("model_essay") or {}
    return bool(coach_plan.get("action_items") or coach_plan.get("exercises") or model_essay.get("text"))


def _render_essay_image(essay_image_b64: str) -> None:
    """雅思Task 1提交时展示用户上传的图表/图片，让作文原文和图片放在一起对照看。"""
    st.image(base64.b64decode(essay_image_b64), caption="题目图表", width=320)


def _finish_submission_if_ready() -> str | None:
    """收取后台结果；被用户取消的任务即使后台自然结束也不展示结果。"""
    future = st.session_state.submission_future
    task_id = st.session_state.submission_task_id
    if future is None or not future.done():
        return None

    st.session_state.submission_future = None
    st.session_state.submission_task_id = None
    st.session_state.pending_submission = None
    if task_id in st.session_state.cancelled_submission_ids:
        st.session_state.cancelled_submission_ids.discard(task_id)
        return "已忽略已结束任务的后台结果。"
    try:
        result = future.result()
    except Exception as exc:
        return f"批改任务执行失败：{exc}"
    st.session_state.last_result = result
    # 新一轮结果到了，无论是不是用户点了"写一篇新作文"触发的重新提交，
    # 都应该自动切回结果展示，不需要用户再手动做什么。
    st.session_state.show_new_essay_form = False
    if result.get("is_valid") is False:
        return f"提交未通过校验：{result.get('reject_reason')}"
    return "处理完成，结果已经在下方展示。"


@st.fragment(run_every=2)
def _render_task_banner() -> None:
    """整个工作台页顶部的任务状态条：每2秒自己刷新一次，不需要用户手动点
    "刷新任务状态"。一旦发现后台任务跑完了，调用`st.rerun()`把当前fragment
    的刷新"升级"成整页rerun，这样`_finish_submission_if_ready()`才能真正
    收走结果、把`last_result`/`show_new_essay_form`这些状态切过去。
    """
    future = st.session_state.submission_future
    if future is None:
        return
    if future.done():
        st.rerun()
        return
    st.info("批改任务正在后台处理；切换页面不会中断，这里会自动刷新状态。")
    if st.button("强制结束任务", type="secondary", key="stop_submission_top"):
        task_id = st.session_state.submission_task_id
        future.cancel()
        if task_id:
            st.session_state.cancelled_submission_ids.add(task_id)
        st.session_state.submission_future = None
        st.session_state.submission_task_id = None
        st.session_state.pending_submission = None
        st.warning("已结束本次任务。若请求已发送，后台会自然结束，但结果不会被保存或展示。")
        st.rerun()


@st.fragment(run_every=1)
def _render_correction_progress() -> None:
    """"写作批改"页在批改进行中时的右栏：只显示"正在批阅中"，每秒自己
    刷新一次。任务跑完时用`st.rerun()`升级成整页rerun，切回展示结果卡片。
    """
    future = st.session_state.submission_future
    if future is None:
        return
    if future.done():
        st.rerun()
        return
    st.info("⏳ 正在批阅中，请稍候……")


col_title, col_user = st.columns([4.4, 1.25], vertical_alignment="center")
with col_title:
    st.markdown(
        f"""
        <div class="hb-workbench-hero">
          <h1>你好，{user_id} 👋</h1>
          <p>从一篇练习开始，发现优点、解决问题，并看见自己的持续进步。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_user:
    st.markdown(f"<div class='hb-account-card'>👤 <b>{user_id}</b><br/><span style='font-size:.86rem'>我的学习空间</span></div>", unsafe_allow_html=True)
    if st.button("退出登录", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

page = st.radio("工作台功能", ["写作批改", "历史进步仪表盘", "写作知识库问答"], horizontal=True, label_visibility="collapsed")

# 任务状态在整个工作台页展示；用户切去产品页、再回来时仍可看到并收取同一任务。
completed_message = _finish_submission_if_ready()
active_future = st.session_state.submission_future
is_processing = active_future is not None and not active_future.done()
if completed_message:
    if completed_message.startswith("处理完成"):
        st.success(completed_message)
    elif completed_message.startswith("提交未通过"):
        st.warning(completed_message)
    else:
        st.error(completed_message)
_render_task_banner()

if page == "写作批改":
    result = st.session_state.last_result
    has_result = bool(result) and result.get("is_valid") is not False
    show_form = not has_result or st.session_state.get("show_new_essay_form", False)

    if is_processing:
        # bug修复：批改进行中时，之前这里的分支条件只看`has_result`/
        # `show_new_essay_form`，如果用户之前有历史结果，处理中会误把
        # 上一轮的旧结果卡片渲染出来，而不是这次新提交的内容。现在
        # `is_processing`优先级最高：处理中只展示这次刚提交的题目和作文
        # 原文（存在`pending_submission`里），配合下面的5步进度条，完成前
        # 完全不出现分数/反馈卡片，等后台任务结束后才切回结果视图。
        pending = st.session_state.pending_submission or {}
        render_topic_card(pending.get("exam_type"), pending.get("essay_topic"), pending.get("exam_subtype"))
        col_essay, col_status = st.columns([1.7, 1])
        with col_essay:
            if pending.get("essay_image_b64"):
                _render_essay_image(pending["essay_image_b64"])
            render_essay_with_highlights(pending.get("essay_text", ""), [])
        with col_status:
            _render_correction_progress()

    elif show_form:
        st.header("开始一次写作练习")
        st.markdown('<div class="hb-learning-note">写完不用急着自己找问题。提交后，慧笔会帮你梳理评分、可修改的句子与下一步练习方向。</div>', unsafe_allow_html=True)

        # 提交表单本轮改成和下方结果视图同样的"题目卡+左右两栏"外壳
        # （`st.container(border=True)`是Streamlit的原生带边框容器，自带圆角
        # 边框，不需要额外CSS就有卡片的观感），保证提交前/提交后是同一套
        # 版式，不是两种完全不同风格的页面。
        with st.container(border=True):
            st.markdown("##### 📋 题目")
            exam_type = st.selectbox("作文类型", EXAM_TYPE_OPTIONS)
            exam_subtype = None
            if exam_type == TOEFL:
                exam_subtype = st.selectbox("托福写作任务", TOEFL_SUBTYPES)
            elif exam_type == IELTS:
                exam_subtype = st.selectbox("雅思写作任务", IELTS_SUBTYPES)
            essay_topic = st.text_area("作文题目（请填写题目要求）", height=100)

            essay_image_b64 = None
            if exam_type == IELTS and exam_subtype == IELTS_TASK1:
                uploaded_image = st.file_uploader(
                    "上传题目附带的图表/表格/流程图/地图（Task 1必须有图片才能评分）",
                    type=["png", "jpg", "jpeg"],
                )
                if uploaded_image is not None:
                    image_bytes = uploaded_image.getvalue()
                    essay_image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    st.image(image_bytes, caption="已上传，提交后会先做图片理解再评分", width=320)
                st.caption(
                    "图片会先交给GLM-4V-Flash（云端、免费）做客观描述，再用这份描述"
                    "核对作文里的数据/趋势是否准确——打分模型全程看不到原图。"
                )

        col_essay, col_submit = st.columns([1.7, 1])
        with col_essay:
            with st.container(border=True):
                st.markdown("##### 作文原文")
                essay_text = st.text_area(
                    "粘贴你的英语作文",
                    height=320,
                    label_visibility="collapsed",
                    placeholder="在这里粘贴你的英语作文……",
                )
        with col_submit:
            with st.container(border=True):
                st.markdown("##### 准备好了吗？")
                st.caption(
                    "通用英语作文评测、雅思、托福写作统一由大模型结合对应的公开评分量表"
                    "给出结构化对照分，均为模拟评阅，不代表任何官方考试机构的正式成绩。"
                )
                submit_clicked = st.button(
                    "📤 提交作文", type="primary", disabled=is_processing, use_container_width=True
                )

        if submit_clicked:
            if not essay_text.strip():
                st.warning("请先粘贴作文内容")
            elif not essay_topic.strip():
                st.warning("请先填写作文题目")
            elif exam_type == IELTS and exam_subtype == IELTS_TASK1 and not essay_image_b64:
                st.warning("雅思Task 1需要先上传题目附带的图表/图片才能提交")
            else:
                # `build_graph`懒加载：会一路引入langgraph/langchain-openai等重依赖，
                # 本地开发环境没装这些包（见CLAUDE.md"环境信息"）。放到真正点击提交
                # 才import，这样登录后只是切换看三个功能tab（历史仪表盘/知识库问答）
                # 不会因为没装重依赖而崩溃，只有真正要跑推理时才需要。
                if "graph" not in st.session_state:
                    from src.agents.graph import build_graph

                    st.session_state.graph = build_graph()
                history = db.get_user_history(user_id)
                payload = {
                    "user_id": user_id,
                    "essay_text": essay_text,
                    "exam_type": exam_type,
                    "exam_subtype": exam_subtype,
                    "essay_topic": essay_topic,
                    "essay_image_b64": essay_image_b64,
                    "history_summary": {"submission_count": len(history)} if history else None,
                }
                st.session_state.submission_task_id = uuid4().hex
                # bug修复关键点：把这次提交的题目/作文原文单独存一份快照，
                # 处理中的展示只读这份快照，不读`last_result`（那是上一轮的
                # 旧结果），两者不会互相串。
                st.session_state.pending_submission = {
                    "exam_type": exam_type,
                    "exam_subtype": exam_subtype,
                    "essay_topic": essay_topic,
                    "essay_text": essay_text,
                    "essay_image_b64": essay_image_b64,
                }
                st.session_state.submission_future = st.session_state.submission_executor.submit(
                    st.session_state.graph.invoke,
                    payload,
                )
                st.session_state.show_new_essay_form = False
                st.rerun()

    else:
        # 提交+反馈本轮合并成一个页面：题目卡在上，作文原文（左，带语法高亮）
        # 和分数卡（右）左右分栏，布局思路参考essay.art，不是抓取/复制对方代码，
        # 颜色沿用本项目已有的PRIMARY蓝+卡片语言。
        render_topic_card(result.get("exam_type"), result.get("essay_topic"), result.get("exam_subtype"))
        if result.get("score_error"):
            st.error(f"本次数值评分失败：{result['score_error']}")
        if result.get("image_analysis_error"):
            st.warning(f"图片理解失败：{result['image_analysis_error']}，本次评分未参考图片内容。")

        col_essay, col_score = st.columns([1.7, 1])
        with col_essay:
            if result.get("essay_image_b64"):
                _render_essay_image(result["essay_image_b64"])
            render_essay_with_highlights(result.get("essay_text", ""), result.get("grammar_errors", []))
        with col_score:
            # 分数卡不再附带A/B权重、校正说明这类面向内部/答辩的技术细节
            # 文案——对学生来说是看不懂也不需要看懂的信息，按要求去掉，
            # 只保留分数本身和总体评价。
            render_score_panel(result)
            if st.button("✏️ 写一篇新作文", use_container_width=True):
                st.session_state.show_new_essay_form = True
                st.rerun()

        st.subheader("定性反馈")
        feedback_dimensions = result.get("feedback_dimensions") or {}
        if _has_feedback_content(feedback_dimensions):
            render_feedback_dimensions(feedback_dimensions)
        else:
            st.write(result.get("qualitative_feedback", "") or "暂无反馈。")
        st.subheader("个性化修改建议与练习推荐")
        coach_plan = result.get("coach_plan") or {}
        if _has_coach_content(coach_plan):
            render_coach_plan(coach_plan)
        else:
            st.write(result.get("revision_plan", "") or "暂无建议。")
        grammar_errors = result.get("grammar_errors", [])
        st.subheader(f"检测到的语法/用词问题（规则库，共{len(grammar_errors)}处）")
        render_grammar_error_cards(grammar_errors)

elif page == "历史进步仪表盘":
    st.header("我的学习成长")
    st.caption("每一次提交都会留下足迹。回看记录，找到已经进步的地方和下一步的重点。")
    history = db.get_user_history(user_id)
    if not history:
        st.info("还没有历史记录。完成第一篇作文批改后，这里会生成你的成长轨迹。")
    else:
        history_df = pd.DataFrame(history)
        history_df["display_time"] = (
            pd.to_datetime(history_df["created_at"], errors="coerce", utc=True)
            .dt.tz_convert("Asia/Shanghai")
            .dt.strftime("%Y-%m-%d %H:%M")
        )
        latest = history_df.iloc[-1]
        latest_score = _number(latest.get("primary_score"))
        latest_label = latest.get("primary_label") or latest.get("official_rubric_label") or "最近一次评分"
        latest_norm = _normalized_score(latest)
        first_row = history_df.iloc[0]
        first_norm = _normalized_score(first_row)
        change = latest_norm - first_norm
        metric1, metric2, metric3 = st.columns(3)
        with metric1:
            st.metric("累计练习", f"{len(history_df)} 篇")
        with metric2:
            st.metric("最近一次评分", _score_text(latest))
            st.caption(latest_label)
        with metric3:
            st.metric("相较首次变化", f"{change * 100:+.0f} 分")
            st.caption("按统一的 0-100 参考刻度计算")

        st.subheader("学习趋势")
        trend_df = history_df.copy()
        trend_df["写作表现参考"] = trend_df.apply(lambda row: _normalized_score(row) * 100, axis=1)
        trend_df["练习"] = [f"第{i}次" for i in range(1, len(trend_df) + 1)]
        trend_df["提交时间"] = trend_df["display_time"]
        trend_chart = (
            alt.Chart(trend_df)
            .mark_line(
                color="#5B7CFA",
                strokeWidth=3,
                point=alt.OverlayMarkDef(color="#FFFFFF", fill="#5B7CFA", size=90),
                interpolate="monotone",
            )
            .encode(
                x=alt.X(
                    "练习:N",
                    sort=None,
                    title=None,
                    axis=alt.Axis(labelAngle=0, labelColor="#6C7890", tickSize=0),
                ),
                y=alt.Y(
                    "写作表现参考:Q",
                    title="表现参考（0-100）",
                    scale=alt.Scale(domain=[0, 100]),
                    axis=alt.Axis(gridColor="#E8EDF6", labelColor="#6C7890"),
                ),
                tooltip=[
                    alt.Tooltip("练习:N", title="练习次数"),
                    alt.Tooltip("提交时间:N", title="提交时间"),
                    alt.Tooltip("exam_type:N", title="作文类型"),
                    alt.Tooltip("写作表现参考:Q", title="表现参考", format=".0f"),
                ],
            )
            .properties(height=300)
        )
        st.altair_chart(trend_chart, use_container_width=True)
        st.caption("趋势使用统一的 0-100 参考刻度，便于观察自己的变化；不同考试类型的展示分请在详情中查看。")

        st.subheader("历史记录")
        records_for_table = history_df.copy()
        records_for_table["评分"] = records_for_table.apply(_score_text, axis=1)
        st.dataframe(
            records_for_table[["display_time", "exam_type", "score_source", "essay_topic", "评分"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "display_time": "提交时间",
                "exam_type": "作文类型",
                "score_source": "评分来源",
                "essay_topic": "作文题目",
            },
        )

        record_options = {
            f"{row['display_time']} · {row['exam_type'] or '未指定类型'} · {str(row['essay_topic'] or '未填写题目')[:26]}": int(row["id"])
            for _, row in history_df.iloc[::-1].iterrows()
        }
        selected_label = st.selectbox("选择一条记录查看详情", list(record_options))
        selected = history_df.loc[history_df["id"] == record_options[selected_label]].iloc[0]
        with st.expander("查看本次详细反馈", expanded=True):
            selected_primary, selected_max = _number(selected.get("primary_score")), _number(selected.get("primary_max"))
            if selected_primary is not None and selected_max:
                st.metric(
                    selected.get("primary_label") or "本次评分",
                    f"{selected_primary:g}/{selected_max:g}",
                )
                selected_secondary, selected_secondary_max = _number(selected.get("secondary_score")), _number(selected.get("secondary_max"))
                if selected_secondary is not None and selected_secondary_max:
                    st.metric(selected.get("secondary_label") or "辅助分", f"{selected_secondary:g}/{selected_secondary_max:g}")
            else:
                st.metric("历史评分", _score_text(selected))
            st.caption(f"题目：{selected['essay_topic'] or '未填写'}")
            if selected.get("essay_image_path"):
                saved_image_path = _PROJECT_ROOT / selected["essay_image_path"]
                if saved_image_path.exists():
                    st.image(str(saved_image_path), caption="当时上传的题目图表", width=320)
                if selected.get("image_analysis"):
                    with st.expander("查看当时的图片理解描述"):
                        st.write(selected["image_analysis"])
            st.markdown("#### 老师反馈")
            selected_dimensions = selected.get("feedback_dimensions") or {}
            if _has_feedback_content(selected_dimensions):
                render_feedback_dimensions(selected_dimensions)
            else:
                st.write(selected["qualitative_feedback"] or "该历史记录未保存详细反馈。")
            st.markdown("#### 下一步练习建议")
            selected_coach_plan = selected.get("coach_plan") or {}
            if _has_coach_content(selected_coach_plan):
                render_coach_plan(selected_coach_plan)
            else:
                st.write(selected["revision_plan"] or "该历史记录未保存练习建议。")

        confirm_delete = st.checkbox("我确认删除选中的历史记录，此操作不可撤销。", key=f"delete_confirm_{int(selected['id'])}")
        if st.button("删除这条记录", type="secondary", disabled=not confirm_delete):
            if db.delete_submission(int(selected["id"]), user_id):
                st.success("已删除该历史记录。")
                st.rerun()
            else:
                st.error("删除失败，请刷新后重试。")

elif page == "写作知识库问答":
    st.header("写作知识库问答")
    st.caption(
        "知识库（评分细则/语法卡片/考试类型专属细则）已真实构建，直接问问题即可，"
        "比如「雅思写作的评分标准有哪些」「四级作文常见扣分点是什么」。"
    )
    kb_exam_type = st.selectbox(
        "限定检索范围（可选，选一个考试类型可以让检索更精准）",
        ["不限定"] + EXAM_TYPE_OPTIONS,
    )
    if "kb_answering" not in st.session_state:
        st.session_state.kb_answering = False
    with st.form("kb_question_form", enter_to_submit=True):
        kb_question = st.text_input("请输入你的问题")
        ask_submitted = st.form_submit_button(
            "提问",
            type="primary",
            disabled=st.session_state.kb_answering,
            use_container_width=True,
        )
    if ask_submitted:
        if not kb_question.strip():
            st.warning("请先输入问题")
        else:
            # 懒加载：这个tab不需要完整的build_graph()，直接调用
            # answer_kb_question()（复用同一个Chroma检索+LLM），但同样要在
            # 真正点击提问时才import，登录后单纯切换看这个tab不应该报错。
            from src.agents.nodes import answer_kb_question

            st.session_state.kb_answering = True
            try:
                with st.spinner("正在检索知识库并生成回答..."):
                    answer = answer_kb_question(
                        kb_question,
                        exam_type=None if kb_exam_type == "不限定" else kb_exam_type,
                    )
                st.session_state.kb_last_answer = answer
            finally:
                st.session_state.kb_answering = False
    if st.session_state.get("kb_last_answer"):
        st.markdown(st.session_state.kb_last_answer)

render_footer()
