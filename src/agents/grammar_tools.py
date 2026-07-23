"""语法检查用的确定性工具（LangGraph节点固定调用，不是LLM自主决定要不要调用）。

单独成一个模块、不放进`src/agents/tools.py`：`tools.py`顶部`from
langchain_core.tools import tool`，`grammar_check_node`本身是本仓库"不需要
pip install就能跑"的`scripts/smoke_test_nodes.py`覆盖的节点之一（见CLAUDE.md
"怎么跑起来"），如果混在一起，`grammar_check_node`一导入就会连带触发
`langchain_core`导入，在没装langchain的环境里直接`ModuleNotFoundError`，
免pip验证这条路径就断了。这个模块只用标准库`urllib`，保持零依赖。
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

LANGUAGETOOL_API_URL = "https://api.languagetool.org/v2/check"
_REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuiBiEssayCoach/1.0)"}
_LANGUAGETOOL_TIMEOUT_SECONDS = 10
_LANGUAGETOOL_MAX_MATCHES = 40


def languagetool_check(text: str) -> list[dict]:
    """调用LanguageTool公共HTTP API（免费，不需要本地装Java版引擎，见
    `CLAUDE.md`"不要重新踩的坑"里放弃`language_tool_python`本地方案的原因）
    做语法检查，返回结构和`grammar_check_node`本地正则规则库产出的
    `grammar_errors`一致：``{type, position, context, message, suggestion}``，
    方便直接合并进同一个列表，前端渲染/内联高亮不需要区分来源。

    公共API有限流（免费匿名约20次/分钟）且需要联网，调用失败/超时/限流时
    直接返回空列表，不抛异常——语法检查这个环节本来就有本地正则规则库兜底，
    LanguageTool查不到不应该让整条批改链路失败。
    """
    text = text or ""
    if not text.strip():
        return []

    data = urllib.parse.urlencode({"text": text, "language": "en-US"}).encode("utf-8")
    request = urllib.request.Request(
        LANGUAGETOOL_API_URL,
        data=data,
        headers={**_REQUEST_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=_LANGUAGETOOL_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return []

    errors = []
    for match in (payload.get("matches") or [])[:_LANGUAGETOOL_MAX_MATCHES]:
        offset = match.get("offset")
        length = match.get("length")
        if not isinstance(offset, int) or not isinstance(length, int):
            continue
        replacements = [r.get("value") for r in (match.get("replacements") or [])[:3] if r.get("value")]
        category = ((match.get("rule") or {}).get("category") or {}).get("name", "")
        message = match.get("shortMessage") or match.get("message") or "语法/用词问题"
        errors.append({
            "type": "languagetool",
            "position": [offset, offset + length],
            "context": text[max(0, offset - 15):offset + length + 15],
            "message": f"{message}" + (f"（{category}）" if category else ""),
            "suggestion": "、".join(replacements) if replacements else None,
        })
    return errors
