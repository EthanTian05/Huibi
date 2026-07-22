@echo off
cd /d "%~dp0"

echo 正在启动慧笔（HuiBi），首次运行会检查PostgreSQL/RAG知识库，请稍等...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_app.ps1"

echo.
echo ==========================================
echo 程序已退出（Streamlit被关闭，或者启动过程中报错）。
echo 如果是报错，请往上翻看具体的错误信息；正常关闭可以直接关闭这个窗口。
echo ==========================================
pause