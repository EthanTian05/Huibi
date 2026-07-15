"""慧笔 HuiBi —— Streamlit入口。四个页面：提交批改 / 反馈详情 /
历史进步仪表盘 / 写作知识库问答，对应Docs/01-系统架构与Agent设计.md
「前端页面设计」。

现状：评分模型（scoring_tool_node）、RAG知识库（retrieval_agent_node）、
语法检查（grammar_check_node）均已是真实实现（见src/agents/nodes.py顶部
注释）；trait_scores三项都已经从整体分占位复制改成启发式信号（词汇丰富度/
段落结构/语法错误密度），但仍不是训练出来的多头预测，见CLAUDE.md说明。

运行：
    streamlit run app.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from src.agents.graph import build_graph
from src.storage import db

st.set_page_config(page_title="慧笔 HuiBi", layout="wide")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.title("慧笔 HuiBi —— 英语写作智能批改与个性化学习伴学智能体")
st.caption("评分模型（微调DistilBERT+自建BiLSTM）/ RAG知识库 / 规则库语法检查均为真实实现，见README/CLAUDE.md")

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
            st.metric("量化评分（A:0.95微调DistilBERT + B:0.05自建BiLSTM）", f"{result.get('quant_score', 0):.2f}")
        with col2:
            traits = result.get("trait_scores", {})
            if traits:
                st.write("分项评分（均为启发式信号驱动，非训练出的多头预测，见CLAUDE.md）：", traits)
        st.subheader("定性反馈")
        st.write(result.get("qualitative_feedback", ""))
        st.subheader("个性化修改建议与练习推荐")
        st.write(result.get("revision_plan", ""))
        grammar_errors = result.get("grammar_errors", [])
        st.subheader(f"检测到的语法/用词问题（规则库，共{len(grammar_errors)}处）")
        if grammar_errors:
            st.dataframe(pd.DataFrame(grammar_errors)[["type", "message", "context", "suggestion"]])
        else:
            st.caption("未检测到规则库覆盖范围内的问题")

elif page == "历史进步仪表盘":
    st.header("历史进步仪表盘")
    history = db.get_user_history(user_id)
    if not history:
        st.info("该用户暂无历史提交记录")
    else:
        history_df = pd.DataFrame(history)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("评分趋势")
            st.line_chart(history_df.set_index("created_at")["quant_score"])
        with col2:
            st.subheader("最近一次分项雷达图")
            latest_traits = history_df.iloc[-1]["trait_scores"]
            if latest_traits:
                import matplotlib.pyplot as plt

                labels = list(latest_traits.keys())
                values = list(latest_traits.values())
                angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
                values_closed = values + values[:1]
                angles_closed = angles + angles[:1]
                fig, ax = plt.subplots(figsize=(3.5, 3.5), subplot_kw={"polar": True})
                ax.plot(angles_closed, values_closed, linewidth=2)
                ax.fill(angles_closed, values_closed, alpha=0.25)
                ax.set_xticks(angles)
                ax.set_xticklabels(labels)
                ax.set_ylim(0, 1)
                st.pyplot(fig)
                st.caption(
                    "三轴都是启发式信号驱动（词汇丰富度/段落结构/语法错误密度），"
                    "不是训练出来的多头预测，见CLAUDE.md"
                )
        st.dataframe(history_df)

elif page == "写作知识库问答":
    st.header("写作知识库问答")
    st.info(
        "Day2接入：RAG知识库（评分细则/语法卡片/范文）尚未构建，"
        "见Docs/01-系统架构与Agent设计.md和src/rag/build_kb.py"
    )
    st.text_input("问题（占位，暂不可用）", disabled=True)
