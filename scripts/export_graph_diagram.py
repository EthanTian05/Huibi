"""导出LangGraph真实编排出的Agent流程图（不是手绘示意图），输出到
03-项目效果截图/system/，供报告/PPT/答辩材料使用。

区别于`scripts/generate_system_diagrams.py`——那份脚本用matplotlib手绘了一个
简化版的"LangGraph 编排"示意框，这里导出的是`build_graph()`编译后LangGraph
自己看到的真实节点/边结构（`compiled_graph.get_graph()`），更适合答辩时回应
"能不能看一下真实的Agent编排图"这类问题。

需要能`pip install -r requirements.txt`的完整环境（langgraph/langchain-core），
本地开发机装不上，见CLAUDE.md"环境信息"，在训练服务器/部署服务器等能跑
`build_graph()`的机器上执行本脚本。

PNG渲染走LangChain封装的Mermaid Ink公开API（`draw_method`默认为API），需要
这台机器能访问外网；同时总是先保存一份`.mmd`纯文本源码作为不依赖网络渲染的
兜底——网络失败时至少还有可以贴进支持Mermaid的Markdown查看器（比如
Docs/01号文档已经在用的mermaid代码块）里渲染的文本。
"""
from __future__ import annotations

from pathlib import Path

def _default_out_dir() -> Path:
    """本地完整checkout（`01-源代码`和`03-项目效果截图`是同级目录）能找到
    报告用的输出目录；训练/部署服务器上只有`01-源代码`这一层内容（没有
    同级的素材目录），这种情况下退回仓库自己的`reports/`目录，不因为找不到
    素材目录就直接崩溃——这个脚本两种环境都要能跑，服务器上主要是用来验证
    真实渲染链路（网络能不能连到mermaid.ink），不是最终出图的地方。
    """
    root = Path(__file__).resolve().parents[2]
    sibling = next((path for path in root.iterdir() if path.name == "03-项目效果截图"), None)
    if sibling is not None:
        return sibling / "system"
    return Path(__file__).resolve().parents[1] / "reports"


OUT_DIR = _default_out_dir()

MMD_FILENAME = "08_LangGraph编排图.mmd"
PNG_FILENAME = "08_LangGraph编排图.png"


def export_langgraph_diagram(out_dir: Path = OUT_DIR) -> Path:
    """导出`build_graph()`编译后的真实节点/边结构，返回PNG成功时的路径，
    PNG渲染失败（比如这台机器访问不了mermaid.ink）时返回.mmd源码的路径。
    """
    from src.agents.graph import build_graph

    out_dir.mkdir(parents=True, exist_ok=True)
    drawable = build_graph().get_graph()

    mermaid_source = drawable.draw_mermaid()
    mmd_path = out_dir / MMD_FILENAME
    mmd_path.write_text(mermaid_source, encoding="utf-8")
    print(f"已保存Mermaid源码：{mmd_path}")

    try:
        png_bytes = drawable.draw_mermaid_png()
    except Exception as exc:  # noqa: BLE001 - 网络/依赖问题都归为渲染失败，不影响.mmd已经保存
        print(f"PNG渲染失败（{exc}），已保存的.mmd源码仍可以贴进支持Mermaid的Markdown查看器/在线编辑器查看。")
        return mmd_path

    png_path = out_dir / PNG_FILENAME
    png_path.write_bytes(png_bytes)
    print(f"已保存PNG图片：{png_path}（{len(png_bytes)}字节）")
    return png_path


if __name__ == "__main__":
    export_langgraph_diagram()
