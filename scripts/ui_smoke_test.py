"""不用控制浏览器的Streamlit页面执行冒烟测试。

通过Streamlit自带AppTest实际执行三个页面脚本；工作台预置登录会话，但不点击
提交按钮，因此不会加载A/B模型或调用LLM。
"""
from __future__ import annotations

from streamlit.testing.v1 import AppTest


def main() -> int:
    failed = False
    # 必须从入口应用切页；直接用from_file单独执行pages里的文件时，AppTest没有
    # 建立多页路由表，st.page_link会因测试框架缺少url_pathname而误报KeyError。
    app = AppTest.from_file("app.py")
    cases = [
        ("app.py", None, {}),
        ("pages/1_登录.py", "pages/1_登录.py", {}),
        ("pages/2_工作台.py", "pages/2_工作台.py", {"logged_in": True, "username": "mcr"}),
    ]
    for label, page_path, session in cases:
        if page_path:
            app.switch_page(page_path)
        for key, value in session.items():
            app.session_state[key] = value
        app.run(timeout=45)
        exceptions = list(app.exception)
        print(f"{label}: {'PASS' if not exceptions else 'FAIL'}")
        for exception in exceptions:
            print(exception)
        failed = failed or bool(exceptions)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
