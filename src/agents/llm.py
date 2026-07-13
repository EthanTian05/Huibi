"""LLM封装：主力DeepSeek V4 Flash，免费/兜底GLM-4.7-Flash，走LangChain的
ChatOpenAI（两家都提供OpenAI兼容接口）。Key从项目根目录的.env读取，
见Docs/RUNNING.md「环境变量」。

**踩坑记录（Day1已验证，别再踩）**：DeepSeek的"flash"系列是推理模型，
会先输出`reasoning_content`再输出`content`。如果`max_tokens`给得太小
（比如64），推理阶段就把token预算耗尽，`content`会是空字符串、
`finish_reason`是"length"——表现上像是"LLM调用成功但什么都没返回"，
容易被误判成Key错了或者Prompt有问题。这里默认给了较大的max_tokens，
不要因为"想省token"就调小到两位数。用`python scripts/check_llm_key.py`
可以脱离langchain独立验证这一点。
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

DEFAULT_MAX_TOKENS = 2048
DEFAULT_TEMPERATURE = 0.3

_PROVIDER_DEFAULTS = {
    "deepseek": {
        "model_env": "DEEPSEEK_MODEL_NAME",
        "model_default": "deepseek-chat",
        "key_env": "DEEPSEEK_API_KEY",
        "base_url_env": "DEEPSEEK_BASE_URL",
        "base_url_default": "https://api.deepseek.com",
    },
    "glm": {
        "model_env": "GLM_MODEL_NAME",
        "model_default": "glm-4-flash",
        "key_env": "GLM_API_KEY",
        "base_url_env": "GLM_BASE_URL",
        "base_url_default": "https://open.bigmodel.cn/api/paas/v4",
    },
}


def _has_real_key(key_env: str) -> bool:
    value = os.environ.get(key_env, "")
    return bool(value) and not value.startswith("your_")


def _build_chat_model(provider: str) -> ChatOpenAI:
    provider = provider.lower()
    if provider not in _PROVIDER_DEFAULTS:
        raise ValueError(f"未知的LLM供应商: {provider}（目前只支持 deepseek / glm）")

    cfg = _PROVIDER_DEFAULTS[provider]
    if not _has_real_key(cfg["key_env"]):
        raise RuntimeError(
            f"{provider}对应的环境变量{cfg['key_env']}还没配置真实Key，"
            f"检查项目根目录的.env（模板见.env.example）。"
        )

    return ChatOpenAI(
        model=os.environ.get(cfg["model_env"], cfg["model_default"]),
        api_key=os.environ[cfg["key_env"]],
        base_url=os.environ.get(cfg["base_url_env"], cfg["base_url_default"]),
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
    )


@lru_cache(maxsize=None)
def get_chat_model_with_fallback() -> ChatOpenAI:
    """返回主力供应商的ChatModel；如果兜底供应商的Key也配置好了，
    就用LangChain的.with_fallbacks()挂上，主力调用失败/超限时自动切换。
    """
    primary = os.environ.get("LLM_PROVIDER", "deepseek")
    fallback = os.environ.get("LLM_FALLBACK_PROVIDER", "glm")

    primary_model = _build_chat_model(primary)

    fallback_cfg = _PROVIDER_DEFAULTS.get(fallback.lower())
    if fallback_cfg and _has_real_key(fallback_cfg["key_env"]):
        fallback_model = _build_chat_model(fallback)
        return primary_model.with_fallbacks([fallback_model])

    return primary_model
