"""慧笔 HuiBi 登录与注册页。"""
from __future__ import annotations

import streamlit as st

from src.storage import db
from src.ui_theme import inject_theme, render_footer, render_top_nav

st.set_page_config(page_title="登录 · 慧笔 HuiBi", page_icon="🔐", layout="wide")
inject_theme()
render_top_nav("login")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

st.markdown(
    """
    <div class="hb-hero">
      <h1>登录或创建账号</h1>
      <p>登录后保存你的评分趋势、常见错误与个性化练习计划。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 单栏居中卡片，仿essay.art"纯背景+居中内容"的极简版式，不再用左侧大幅
# 渐变Hero+右侧表单的两栏布局——essay.art全站没有这种色块Hero。
_, center, _ = st.columns([1, 1.3, 1])
with center:
    if st.session_state.logged_in:
        st.success(f"已登录：{st.session_state.username}")
        st.page_link("pages/2_工作台.py", label="进入工作台", icon="📝", use_container_width=False)
        if st.button("退出登录"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    else:
        login_tab, register_tab = st.tabs(["登录", "注册"])
        with login_tab:
            with st.form("login_form"):
                login_username = st.text_input("用户名", key="login_username")
                login_password = st.text_input("密码", type="password", key="login_password")
                submitted = st.form_submit_button("登录", type="primary", use_container_width=True)
            if submitted:
                if db.verify_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.switch_page("pages/2_工作台.py")
                else:
                    st.error("用户名或密码错误")
        with register_tab:
            with st.form("register_form"):
                reg_username = st.text_input("用户名", key="register_username")
                reg_password = st.text_input(
                    "密码（至少6位）",
                    type="password",
                    key="register_password",
                )
                reg_password2 = st.text_input(
                    "确认密码",
                    type="password",
                    key="register_password2",
                )
                reg_submitted = st.form_submit_button("注册", type="primary", use_container_width=True)
            if reg_submitted:
                if reg_password != reg_password2:
                    st.error("两次输入的密码不一致")
                else:
                    ok, msg = db.create_user(reg_username, reg_password)
                    if ok:
                        st.success(msg + "，请切换到“登录”标签页继续。")
                    else:
                        st.error(msg)

render_footer()
