"""LLM可自主调用的第三方工具（不是LangGraph固定路由调用的工具）。

确定性工具（语法检查`languagetool_check`，每次都要跑、不需要LLM自己决定要不要
调）在`src/agents/grammar_tools.py`，不放在这里——这个模块顶部要import
`langchain_core`，混在一起会让不需要langchain的调用方（比如
`grammar_check_node`）被迫连带触发`langchain_core`导入。
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from langchain_core.tools import tool

DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
_TIMEOUT_SECONDS = 6
_MAX_MEANINGS = 2
_MAX_DEFINITIONS_PER_MEANING = 2
_MAX_SYNONYMS = 5
_REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuiBiEssayCoach/1.0)"}


@tool
def dictionary_lookup(word: str) -> str:
    """查询一个英语单词的释义、词性、例句和同义词，用于核实某个具体单词的
    含义或用法是否准确、有没有更地道的替代表达。传入单词的原形（不要传短语
    或整句话），只有真的不确定某个词的意思或用法时才调用，常见词不用查。
    """
    word = word.strip()
    if not word:
        return "没有提供有效的单词，跳过查词。"

    url = DICTIONARY_API_URL.format(word=urllib.parse.quote(word))
    request = urllib.request.Request(url, headers=_REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return f'词典未收录"{word}"，请换一个词或直接使用作文原文里的表达。'
        return f"词典查询失败（HTTP {exc.code}），本次不使用查词结果，按已有知识作答。"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return f"词典查询失败（{exc}），本次不使用查词结果，按已有知识作答。"

    entry = data[0] if isinstance(data, list) and data else {}
    lines = [f"单词：{entry.get('word', word)}"]
    for meaning in entry.get("meanings", [])[:_MAX_MEANINGS]:
        part_of_speech = meaning.get("partOfSpeech", "")
        for definition in meaning.get("definitions", [])[:_MAX_DEFINITIONS_PER_MEANING]:
            lines.append(f"- ({part_of_speech}) {definition.get('definition', '')}")
            if definition.get("example"):
                lines.append(f"  例句：{definition['example']}")
        synonyms = meaning.get("synonyms", [])[:_MAX_SYNONYMS]
        if synonyms:
            lines.append(f"- 同义词：{', '.join(synonyms)}")

    if len(lines) == 1:
        return f'"{word}"没有查到有效释义，按已有知识作答。'
    return "\n".join(lines)
