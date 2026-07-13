"""Day1 联通性自检：不依赖langchain/openai SDK，只用标准库urllib直接调用
DeepSeek/GLM的OpenAI兼容Chat Completions接口，确认.env里的Key能不能真的调通。

用法：
    python scripts/check_llm_key.py
"""
import json
import os
import urllib.request
import urllib.error
from pathlib import Path


def load_dotenv(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def call_chat_completions(base_url: str, api_key: str, model: str, prompt: str) -> dict:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    env = {**os.environ, **load_dotenv(env_path)}

    checks = [
        ("DeepSeek", env.get("DEEPSEEK_API_KEY"), env.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"), env.get("DEEPSEEK_MODEL_NAME", "deepseek-chat")),
        ("GLM", env.get("GLM_API_KEY"), env.get("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"), env.get("GLM_MODEL_NAME", "glm-4-flash")),
    ]

    for name, api_key, base_url, model in checks:
        print(f"--- {name} ({model}) ---")
        if not api_key or api_key.startswith("your_"):
            print(f"跳过：{name}的API Key未配置（.env里是占位值）\n")
            continue
        try:
            result = call_chat_completions(base_url, api_key, model, "用一句话介绍一下你自己")
            content = result["choices"][0]["message"]["content"]
            print("调通成功，返回内容：", content.strip())
            if not content.strip():
                print("完整响应（内容为空，供调试）：", json.dumps(result, ensure_ascii=False, indent=2))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"HTTP错误 {e.code}：{body[:500]}")
        except Exception as e:
            print(f"调用失败：{type(e).__name__}: {e}")
        print()


if __name__ == "__main__":
    main()
