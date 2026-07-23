"""LLM封装：主力DeepSeek V4 Pro，免费/兜底GLM-4.7-Flash，走LangChain的
ChatOpenAI（都提供OpenAI兼容接口）。量化打分固定用DeepSeek V4 Pro，
和定性反馈/辅导建议共用同一个主模型，见`get_scoring_chat_model()`。
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

DEFAULT_MAX_TOKENS = 8192
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
    # 图片理解（IELTS Task 1图表分析）专用，复用GLM账号的Key/Base URL，
    # 只是模型名不同——GLM-4.7-Flash是纯文本模型，不认image_url这种多模态
    # content，必须用GLM-4V-Flash这条独立的视觉模型线。
    "glm_vision": {
        "model_env": "GLM_VISION_MODEL_NAME",
        "model_default": "glm-4v-flash",
        "key_env": "GLM_API_KEY",
        "base_url_env": "GLM_BASE_URL",
        "base_url_default": "https://open.bigmodel.cn/api/paas/v4",
    },
}


def _has_real_key(key_env: str) -> bool:
    value = os.environ.get(key_env, "")
    return bool(value) and not value.startswith("your_")


# 按供应商配置构造 OpenAI 兼容的聊天模型实例。
def _build_chat_model(provider: str) -> ChatOpenAI:
    provider = provider.lower()
    if provider not in _PROVIDER_DEFAULTS:
        raise ValueError(f"未知的LLM供应商: {provider}（目前只支持 deepseek / glm / glm_vision）")

    cfg = _PROVIDER_DEFAULTS[provider]
    key_env = cfg["key_env"]
    if not _has_real_key(key_env):
        raise RuntimeError(
            f"{provider}对应的环境变量{key_env}还没配置真实Key，"
            f"检查项目根目录的.env（模板见.env.example）。"
        )
    api_key = os.environ[key_env]

    return ChatOpenAI(
        model=os.environ.get(cfg["model_env"], cfg["model_default"]),
        api_key=api_key,
        base_url=os.environ.get(cfg["base_url_env"], cfg["base_url_default"]),
        max_tokens=DEFAULT_MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
    )


@lru_cache(maxsize=None)
# 优先返回可用的 DeepSeek；不可用时自动切换到 GLM。
def get_chat_model_with_fallback() -> ChatOpenAI:
    primary = os.environ.get("LLM_PROVIDER", "deepseek")
    fallback = os.environ.get("LLM_FALLBACK_PROVIDER", "glm")

    primary_model = _build_chat_model(primary)

    fallback_cfg = _PROVIDER_DEFAULTS.get(fallback.lower())
    if fallback_cfg and _has_real_key(fallback_cfg["key_env"]):
        fallback_model = _build_chat_model(fallback)
        return primary_model.with_fallbacks([fallback_model])

    return primary_model


@lru_cache(maxsize=None)
# 获取主模型供 Coach Agent 绑定工具；该场景不使用备用模型。
def get_primary_chat_model() -> ChatOpenAI:

    primary = os.environ.get("LLM_PROVIDER", "deepseek")
    return _build_chat_model(primary)


@lru_cache(maxsize=None)
# 打分专用模型：固定用主力DeepSeek V4 Pro，和定性反馈/辅导建议共用同一个模型实例。
def get_scoring_chat_model() -> ChatOpenAI:
    """量化打分这一步用的模型。曾经默认走本地Ollama（`qwen2.5:7b`），用户
    确认改回固定用DeepSeek V4 Pro，不再需要本地模型依赖和按调用方切换。
    """
    return get_primary_chat_model()


@lru_cache(maxsize=None)
# 图片理解专用（IELTS Task 1图表/图片分析），固定用GLM-4V-Flash，不做fallback——
# 图片分析失败时应该让调用方明确感知、提示用户重试，而不是静默换一个不认识
# 图片的文本模型进去，那样会拿到胡编的图片描述而不是报错。
def get_vision_chat_model() -> ChatOpenAI:
    return _build_chat_model("glm_vision")
