"""从GitHub Release下载训练好的评分模型权重（模型权重本身不进git仓库，
太大，见README.md「模型权重下载」）。

**当前仓库是私有的**：GitHub不允许匿名访问私有仓库的Release资产，就算你知道
`browser_download_url`直接请求也会是404。这个脚本会自动检测：如果本地`.env`
里有`GITHUB_TOKEN`就走认证下载（当前阶段用这个）；等仓库转成public之后，
不设`GITHUB_TOKEN`也能直接匿名下载。

用法：
    python scripts/download_models.py
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

REPO = "BCXiaoxue/RAG_Writing"
TAG = "models-v1.0.0"

EXPECTED_SHA256 = {
    "essay-scorer-finetuned-v1-pytorch_model.bin": "036a56a7d205eca050dab5f7e4a38fbd70c6be0301f7600d70f174b315d14ba4",
    "essay-scorer-custom-v1-pytorch_model.bin": "b113b4a7dc315577758e10b6d8414419315614c02545f2f5f10bb08205e1076c",
}

LOCAL_PATHS = {
    "essay-scorer-finetuned-v1-pytorch_model.bin": "models/essay-scorer-finetuned/v1/pytorch_model.bin",
    "essay-scorer-finetuned-v1-tokenizer.json": "models/essay-scorer-finetuned/v1/tokenizer.json",
    "essay-scorer-finetuned-v1-tokenizer_config.json": "models/essay-scorer-finetuned/v1/tokenizer_config.json",
    "essay-scorer-custom-v1-pytorch_model.bin": "models/essay-scorer-custom/v1/pytorch_model.bin",
    "essay-scorer-custom-v1-vocab.json": "models/essay-scorer-custom/v1/vocab.json",
    "essay-scorer-custom-v1-model_config.json": "models/essay-scorer-custom/v1/model_config.json",
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def get_release_assets(token: str | None) -> list[dict]:
    url = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["assets"]


def download_asset(asset: dict, local_path: Path, token: str | None):
    local_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {"Accept": "application/octet-stream"}
    if token:
        # 私有仓库必须走API的asset端点+认证头，不能直接用browser_download_url
        url = f"https://api.github.com/repos/{REPO}/releases/assets/{asset['id']}"
        headers["Authorization"] = f"Bearer {token}"
    else:
        # 仓库公开后，browser_download_url可以匿名直接下载
        url = asset["browser_download_url"]
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp, open(local_path, "wb") as f:
        f.write(resp.read())


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("未检测到GITHUB_TOKEN，按公开仓库匿名下载方式尝试（如果仓库还是私有的，会在这里失败）。")

    assets = {a["name"]: a for a in get_release_assets(token)}

    for asset_name, local_path in LOCAL_PATHS.items():
        if asset_name not in assets:
            raise RuntimeError(f"Release里找不到资产{asset_name}，检查tag={TAG}是否还存在")
        local_path = Path(local_path)
        print(f"下载 {asset_name} -> {local_path} ...")
        download_asset(assets[asset_name], local_path, token)

        expected = EXPECTED_SHA256.get(asset_name)
        if expected:
            actual = sha256_of(local_path)
            if actual != expected:
                raise RuntimeError(
                    f"{local_path} 的SHA-256校验失败！期望{expected}，实际{actual}。"
                    f"文件可能下载不完整或Release资产已更新，不要直接使用这个文件。"
                )
            print(f"  SHA-256校验通过: {actual}")

    print("\n全部模型权重下载完成，训练日志(training_log.json)已经在git仓库里，不需要单独下载。")


if __name__ == "__main__":
    main()
