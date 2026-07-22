<#
.SYNOPSIS
    本地启动慧笔（HuiBi）：确认本地PostgreSQL在跑、RAG知识库已构建，再用.venv-uv跑Streamlit。

.DESCRIPTION
    纯本地运行，不涉及服务器部署（服务器部署脚本见 deploy_start.ps1 / deploy_stop.ps1，
    当前项目不使用，见CLAUDE.md「服务器部署（备用，当前不用）」）。
    步骤：确认.venv-uv和.env存在 → 确认本地PostgreSQL在跑（没跑则pg_ctl start拉起来，
    scoop装的服务不会开机自启）→ 确认RAG向量库已构建（没有则先跑build_kb.py）→
    用.venv-uv/Scripts/python.exe跑streamlit run app.py（前台运行，Ctrl+C停止）。

.EXAMPLE
    powershell -File scripts/start_app.ps1
#>

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$VenvPython = Join-Path $RepoRoot ".venv-uv\Scripts\python.exe"
$EnvFile = Join-Path $RepoRoot ".env"
$ChromaDir = Join-Path $RepoRoot "data\processed\chroma_kb"

if (-not (Test-Path $VenvPython)) {
    Write-Host "找不到 .venv-uv，先按 Docs/03-RUNNING.md 建好能pip install的环境："
    Write-Host "  uv venv --python 3.11 .venv-uv"
    Write-Host "  uv pip install -r requirements.txt --python .venv-uv"
    exit 1
}

if (-not (Test-Path $EnvFile)) {
    Write-Host "找不到 .env，先执行： cp .env.example .env  然后填入真实的DEEPSEEK_API_KEY等Key"
    exit 1
}

Write-Host "检查本地PostgreSQL..."
if (-not (Get-Command pg_ctl -ErrorAction SilentlyContinue)) {
    Write-Host "找不到pg_ctl命令，确认本机是否已用 scoop install postgresql 装好并加进PATH（见CLAUDE.md「环境信息」）。"
    exit 1
}

& pg_ctl status
if ($LASTEXITCODE -eq 0) {
    Write-Host "PostgreSQL已经在跑。"
} else {
    Write-Host "PostgreSQL没在跑，启动中（pg_ctl start）..."
    & pg_ctl start -w -t 30
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PostgreSQL启动失败，检查scoop装的postgresql是否正常。"
        exit 1
    }
    Write-Host "PostgreSQL已启动。"
}

if (-not (Test-Path $ChromaDir)) {
    Write-Host "data/processed/chroma_kb 不存在，先构建RAG知识库（把data/kb/下的Markdown embedding进本地Chroma，几十秒）..."
    & $VenvPython -m src.rag.build_kb
    if ($LASTEXITCODE -ne 0) {
        Write-Host "build_kb.py执行失败，检查上面的报错（常见于embedding模型下载失败），见Docs/03-RUNNING.md。"
        exit 1
    }
} else {
    Write-Host "RAG知识库已存在（data/processed/chroma_kb），跳过重新构建。"
}

Write-Host "启动Streamlit，浏览器访问 http://localhost:8501（Ctrl+C停止）..."
& $VenvPython -m streamlit run app.py
