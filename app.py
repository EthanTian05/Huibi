"""慧笔 HuiBi 产品页：介绍核心能力并引导用户登录或进入工作台。"""
from __future__ import annotations

import streamlit as st

from src.ui_theme import inject_theme, render_footer, render_top_nav

st.set_page_config(page_title="慧笔 HuiBi · 英语写作智能批改", page_icon="✦", layout="wide")
inject_theme()
render_top_nav("product")

st.markdown(
    """
    <div class="hb-hero">
      <h1><span class="hb-hero-accent">慧笔 HuiBi：</span>雅思/托福/通用英语写作批改专家</h1>
      <p>提交一篇作文，几分钟内拿到结构化评分、看得懂的修改意见，以及下一步该练什么。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

hero_left, hero_right = st.columns([0.95, 1.05], vertical_alignment="center")
with hero_left:
    checklist = [
        "结合官方评分量表打分，不是拍脑袋给分",
        "语法/用词/结构逐项指出，不只给一个总分",
        "免费使用，登录后就能提交批改",
    ]
    for item in checklist:
        st.markdown(
            f'<div class="hb-check-pill"><span class="hb-check-pill-icon">✓</span>{item}</div>',
            unsafe_allow_html=True,
        )
    st.write("")
    st.page_link("pages/1_登录.py", label="开始使用慧笔", icon="🚀", use_container_width=False)
with hero_right:
    with st.container(border=True):
        st.markdown("##### 📋 作文原文（示例）")
        st.caption("this technology have change the way we study...")
        st.markdown("---")
        score_col, dim_col = st.columns([0.8, 1.2])
        with score_col:
            st.markdown(
                '<div class="hb-score-number">88<span class="hb-score-max">/100</span></div>'
                '<div class="hb-score-label">通用英语写作对照分</div>',
                unsafe_allow_html=True,
            )
        with dim_col:
            st.caption("结构与衔接 · 23/25")
            st.caption("语法准确性 · 24/25")
            st.caption("内容与任务完成 · 21/25")
            st.caption("语言运用与词汇 · 20/25")

st.markdown('<h2 class="hb-section-title">核心优势</h2>', unsafe_allow_html=True)
st.markdown('<p class="hb-section-subtitle">少花时间猜错在哪里，把时间用在真正能提升写作的地方。</p>', unsafe_allow_html=True)

advantages = [
    ("🎯", "知道自己在哪个水平", "结合雅思Band Descriptors、托福ETS评分指南等公开量表打分，先帮你快速判断这篇作文的大致表现。"),
    ("🛠️", "知道具体哪里要改", "不只给总分，也会指出语法、表达和结构中值得优先修改的地方，中英双语说明。"),
    ("📈", "知道下一步练什么", "根据本次暴露的问题给出练习方向和针对性题目，让下一次写作更有的放矢。"),
    ("📊", "看得见自己的进步", "保存历次结果和常见问题，用趋势图帮助你发现正在变好的地方和仍需加强的部分。"),
]
row1 = st.columns(2)
row2 = st.columns(2)
for col, (icon, title, desc) in zip(row1 + row2, advantages):
    with col:
        st.markdown(
            f'<div class="hb-card"><span class="hb-badge">{icon}</span>'
            f'<h4>{title}</h4><p>{desc}</p></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="hb-closing-panel">
      <h2>准备好查看你的写作反馈了吗？</h2>
      <p>通过页面顶部导航登录或进入工作台，提交作文并查看评分、反馈与进步记录。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

render_footer()
