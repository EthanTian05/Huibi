"""不依赖`langgraph`运行时，直接用`ast`解析`src/agents/graph.py`里
`build_graph()`函数体的真实源码（`add_node`/`add_conditional_edges`/
`add_edge`/`set_entry_point`调用），从中抽取节点与边的结构后再绘图。

和`export_graph_diagram.py`的区别：那份脚本调用真·LangGraph
（`compiled_graph.get_graph()`），需要能`pip install langgraph`的完整环境；
这份脚本本地`.venv`/pip都装不上`langgraph`（见CLAUDE.md"环境信息"，
SSLEOFError），所以退而求其次——不跑运行时，只解析`graph.py`这份源码文件
本身的AST，图上的每条边都能对应到`graph.py`里的一行`add_edge(...)`/
`add_conditional_edges(...)`调用，不是凭空手绘或凭记忆画的示意框。

输出到 03-项目效果截图/system/09_LangGraph编排图(源码解析).png，
同时把解析出的节点/边列表打印到stdout，方便核对是否和`graph.py`一致。
"""
from __future__ import annotations

import ast
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
GRAPH_SRC = ROOT / "src" / "agents" / "graph.py"
OUT_DIR = next(
    (p for p in ROOT.parent.iterdir() if p.name == "03-项目效果截图"), ROOT / "reports"
) / "system"

FONT = "Microsoft YaHei"
INK, MUTED, LINE = "#172033", "#60708A", "#CBD5E1"
BLUE, PURPLE, ORANGE, GREEN, RED = "#5B7CFA", "#8B6CF6", "#F59E0B", "#14B8A6", "#EF4444"

END_LABEL = "END"


def _str_const(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def parse_build_graph(source_path: Path) -> dict:
    """解析`build_graph()`函数体，返回节点顺序、入口节点、普通边、条件边。

    只认`graph.<method>(...)`这种调用形式，字符串字面量直接取值；
    `add_edge(..., END)`里的`END`是个Name（不是字符串），单独识别成终止节点。
    解析不出来的调用形式会被跳过并打印警告，不会静默假装成功。
    """
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    build_fn = next(
        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "build_graph"
    )

    nodes: list[str] = []
    entry: str | None = None
    edges: list[tuple[str, str, str | None]] = []  # (src, dst, condition_fn_name or None)

    for stmt in ast.walk(build_fn):
        if not isinstance(stmt, ast.Call):
            continue
        if not isinstance(stmt.func, ast.Attribute) or not isinstance(stmt.func.value, ast.Name):
            continue
        if stmt.func.value.id != "graph":
            continue
        method = stmt.func.attr
        args = stmt.args

        if method == "add_node" and args:
            name = _str_const(args[0])
            if name:
                nodes.append(name)

        elif method == "set_entry_point" and args:
            entry = _str_const(args[0])

        elif method == "add_edge" and len(args) >= 2:
            src = _str_const(args[0])
            dst_node = args[1]
            dst = _str_const(dst_node)
            if dst is None and isinstance(dst_node, ast.Name) and dst_node.id == "END":
                dst = END_LABEL
            if src and dst:
                edges.append((src, dst, None))

        elif method == "add_conditional_edges" and len(args) >= 3:
            src = _str_const(args[0])
            cond_fn = args[1].id if isinstance(args[1], ast.Name) else None
            mapping = args[2]
            if src and isinstance(mapping, ast.Dict):
                for value_node in mapping.values:
                    dst = _str_const(value_node)
                    if dst:
                        edges.append((src, dst, cond_fn))

    return {"nodes": nodes, "entry": entry, "edges": edges}


LAYER_GAP = 2.4
ROW_GAP = 1.5
BOX_W, BOX_H = 1.75, 0.85


def layered_positions(nodes: list[str], entry: str, edges: list[tuple[str, str, str | None]]):
    """按从entry出发的最长路径层数摆放节点（同层内按加入顺序纵向排开），
    坐标单位是"层号 x LAYER_GAP / 行号 x ROW_GAP"，由图结构算出来，
    不是照着渲染结果手工调的像素坐标。
    """
    import networkx as nx

    g = nx.DiGraph()
    g.add_nodes_from(nodes + [END_LABEL])
    g.add_edges_from((s, d) for s, d, _ in edges)

    depth = {entry: 0}
    frontier = [entry]
    while frontier:
        nxt = []
        for u in frontier:
            for v in g.successors(u):
                if v not in depth or depth[v] < depth[u] + 1:
                    depth[v] = depth[u] + 1
                    nxt.append(v)
        frontier = nxt

    by_layer: dict[int, list[str]] = {}
    for n in nodes + [END_LABEL]:
        by_layer.setdefault(depth.get(n, 0), []).append(n)

    max_layer = max(by_layer)
    pos = {}
    for layer, members in by_layer.items():
        x = layer * LAYER_GAP
        for i, name in enumerate(members):
            y = 0.0 if len(members) == 1 else (len(members) - 1) / 2 * ROW_GAP - i * ROW_GAP
            pos[name] = (x, y)
    return pos, depth, max_layer


def render(parsed: dict, out_path: Path) -> None:
    nodes, entry, edges = parsed["nodes"], parsed["entry"], parsed["edges"]
    pos, depth, max_layer = layered_positions(nodes, entry, edges)

    all_y = [y for _, y in pos.values()]
    top_lane = max(all_y) + 1.3
    bottom_lane = min(all_y) - 1.3

    fig, ax = plt.subplots(figsize=(2.2 * (max_layer + 1), 6.4))
    ax.set(xlim=(-1.1, max_layer * LAYER_GAP + 1.1), ylim=(bottom_lane - 0.6, top_lane + 0.6))
    ax.axis("off")
    fig.patch.set_facecolor("#F8FAFC")
    fig.text(.02, .96, "慧笔 · LangGraph 编排节点图（从 src/agents/graph.py 源码AST解析）",
              fontsize=15, fontweight="bold", color=INK, fontname=FONT)
    fig.text(.02, .915, "节点/边直接抽取自 build_graph() 里的 add_node / add_conditional_edges / add_edge 调用，非手绘示意",
              fontsize=9, color=MUTED, fontname=FONT)

    for name in nodes + [END_LABEL]:
        x, y = pos[name]
        if name == END_LABEL:
            color = MUTED
        elif name == entry:
            color = BLUE
        elif name == "short_circuit_reject":
            color = RED
        else:
            color = PURPLE
        patch = FancyBboxPatch(
            (x - BOX_W / 2, y - BOX_H / 2), BOX_W, BOX_H,
            boxstyle="round,pad=0.01,rounding_size=0.05",
            facecolor="white", edgecolor=color, linewidth=1.8, zorder=3,
        )
        ax.add_patch(patch)
        ax.text(x, y, name, ha="center", va="center", fontsize=9.6, fontweight="bold",
                 color=INK, fontname=FONT, zorder=4)

    # 同一(源节点, 条件函数)只标一次文字，避免多条分支边的label互相重叠
    labeled_conditions: set[tuple[str, str]] = set()

    for src, dst, cond_fn in edges:
        x1, y1 = pos[src]
        x2, y2 = pos[dst]
        color = ORANGE if cond_fn else "#64748B"
        skip = depth[dst] - depth[src]

        if skip > 1:
            # 跨层edge不走直线（会穿过中间层节点），绕到最上/最下的旁路车道
            lane = top_lane if y1 >= 0 else bottom_lane
            xs = [x1, x1, x2, x2]
            ys = [y1, lane, lane, y2 + (BOX_H / 2 + 0.15 if lane > y2 else -(BOX_H / 2 + 0.15))]
            ax.plot(xs, ys, color=color, lw=1.6, zorder=2)
            ax.annotate("", (x2, ys[-1] * 0 + (y2 + (0.05 if lane > y2 else -0.05))), (x2, ys[-1]),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.6), zorder=2)
            label_xy = (x1, lane + (0.18 if lane > y1 else -0.28))
        else:
            ax.annotate(
                "", (x2 - BOX_W / 2, y2), (x1 + BOX_W / 2, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.6, shrinkA=2, shrinkB=2), zorder=2,
            )
            label_xy = ((x1 + x2) / 2, (y1 + y2) / 2 + 0.22)

        if cond_fn and (src, cond_fn) not in labeled_conditions:
            ax.text(*label_xy, cond_fn, ha="center", fontsize=8, color=ORANGE, fontname=FONT, zorder=4,
                    bbox=dict(boxstyle="round,pad=.15", fc="#F8FAFC", ec="none", alpha=.9))
            labeled_conditions.add((src, cond_fn))

    ax.text(-1.1, bottom_lane - 0.5,
            f"入口节点：{entry}　｜　共 {len(nodes)} 个节点、{len(edges)} 条边（橙色=条件路由分支，弧线=跨层跳转边）",
            fontsize=9, color=MUTED, fontname=FONT)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    parsed = parse_build_graph(GRAPH_SRC)
    print(f"从 {GRAPH_SRC} 解析出：")
    print(f"  入口节点: {parsed['entry']}")
    print(f"  节点（{len(parsed['nodes'])}个）: {parsed['nodes']}")
    print(f"  边（{len(parsed['edges'])}条）:")
    for src, dst, cond in parsed["edges"]:
        tag = f"  [条件路由: {cond}]" if cond else ""
        print(f"    {src} -> {dst}{tag}")

    out_path = OUT_DIR / "09_LangGraph编排图(源码解析).png"
    render(parsed, out_path)
    print(f"已保存: {out_path}")
