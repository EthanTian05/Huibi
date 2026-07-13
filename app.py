"""慧笔 HuiBi —— Streamlit入口。四个页面：提交批改 / 反馈详情 /
历史进步仪表盘 / 写作知识库问答，对应Docs/01-系统架构与Agent设计.md
「前端页面设计」。

Day1现状：评分模型（scoring_tool_node）和RAG知识库（retrieval_agent_node）
还是Day2占位实现，见src/agents/nodes.py顶部注释。定性反馈/辅导建议是
真实调用DeepSeek/GLM的结果，SQLite读写是真实实现。

运行：
    streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.agents.graph import build_graph
from src.storage import db

st.set_page_config(page_title="慧笔 HuiBi", layout="wide")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.title("慧笔 HuiBi —— 英语写作智能批改与个性化学习伴学系统")
st.caption("Day1骨架：评分模型/RAG知识库是占位实现，定性反馈/辅导建议已接通真实LLM，见README/CLAUDE.md")

page = st.sidebar.radio("页面", ["提交批改", "反馈详情", "历史进步仪表盘", "写作知识库问答"])
user_id = st.sidebar.text_input("用户ID（演示用，同一ID可以看到历史进步曲线）", value="demo_user")

if page == "提交批改":
    st.header("提交批改")
    essay_prompt_id = st.number_input(
        "题目集ID（对应ASAP-AES的essay_set，Day1先随便填）", min_value=1, max_value=8, value=1
    )
    essay_text = st.text_area("粘贴你的英语作文", height=300)
    if st.button("提交批改", type="primary"):
        if not essay_text.strip():
            st.warning("请先粘贴作文内容")
        else:
            with st.spinner("多智能体正在处理：校验 → 检索 → 评分 → 语法检查 → 定性反馈 → 个性化辅导..."):
                history = db.get_user_history(user_id)
                result = st.session_state.graph.invoke(
                    {
                        "user_id": user_id,
                        "essay_text": essay_text,
                        "essay_prompt_id": int(essay_prompt_id),
                        "history_summary": {"submission_count": len(history)} if history else None,
                    }
                )
            st.session_state.last_result = result
            if result.get("is_valid") is False:
                st.error(f"提交未通过校验：{result.get('reject_reason')}")
            else:
                st.success("处理完成，请切换到「反馈详情」页查看结果")

elif page == "反馈详情":
    st.header("反馈详情")
    result = st.session_state.last_result
    if not result or result.get("is_valid") is False:
        st.info("还没有可展示的反馈，请先在「提交批改」页提交一篇作文")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("量化评分（Day2占位，接入真实评分模型后更新）", f"{result.get('quant_score', 0):.2f}")
        with col2:
            traits = result.get("trait_scores", {})
            if traits:
                st.write("分项评分：", traits)
        st.subheader("定性反馈")
        st.write(result.get("qualitative_feedback", ""))
        st.subheader("个性化修改建议与练习推荐")
        st.write(result.get("revision_plan", ""))

elif page == "历史进步仪表盘":
    st.header("历史进步仪表盘")
    history = db.get_user_history(user_id)
    if not history:
        st.info("该用户暂无历史提交记录")
    else:
        history_df = pd.DataFrame(history)
        st.line_chart(history_df.set_index("created_at")["quant_score"])
        st.dataframe(history_df)

elif page == "写作知识库问答":
    st.header("写作知识库问答")
    st.info(
        "Day2接入：RAG知识库（评分细则/语法卡片/范文）尚未构建，"
        "见Docs/01-系统架构与Agent设计.md和src/rag/build_kb.py"
    )
    st.text_input("问题（占位，暂不可用）", disabled=True)
