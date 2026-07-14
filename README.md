# 慧笔 HuiBi

基于LangChain + LangGraph的英语写作智能批改与个性化学习伴学系统。项目背景、需求对照、架构设计、训练结果等完整文档见 [`CLAUDE.md`](CLAUDE.md) 和 [`Docs/`](Docs/) 目录（先看 [`Docs/06-本轮成果与复现步骤.md`](Docs/06-本轮成果与复现步骤.md) 了解当前真实进度）。

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入真实的API Key，见下方"环境变量"
python scripts/download_models.py   # 下载训练好的模型权重（见下方"模型权重下载"）
streamlit run app.py
```

## 环境变量

复制 `.env.example` 为 `.env`，填入：

- `DEEPSEEK_API_KEY` / `GLM_API_KEY`：LLM推理用，见`Docs/RUNNING.md`「环境变量」
- `KAGGLE_API_TOKEN`（可选）：如果想用Kaggle官方渠道下载ASAP-AES数据集而不是默认的HuggingFace镜像

`.env`已在`.gitignore`里排除，不要提交，也不要把里面的真实值粘贴进任何文档。

## 模型权重下载

两条评分模型（路径A微调DistilBERT、路径B自建BiLSTM）已经在真实ASAP-AES数据上训练完成（测试集QWK分别是0.693和0.622，见`Docs/03-模型训练与微调方案.md`），**但模型权重文件本身没有提交进这个git仓库**——微调模型的`pytorch_model.bin`约265MB，超过GitHub单文件100MB的硬性限制，为了保持仓库轻量、干净，两个模型的权重都统一放在GitHub Release里分发，不进git历史。

### 下载方式一：脚本自动下载（推荐）

```bash
python scripts/download_models.py
```

会自动从[Release `models-v1.0.0`](https://github.com/BCXiaoxue/RAG_Writing/releases/tag/models-v1.0.0)下载全部文件到正确路径，并校验SHA-256。**注意：本仓库当前是私有仓库，运行这个脚本前需要在`.env`里配置好`GITHUB_TOKEN`（有权限读取这个私有仓库的token即可）；仓库转成public之后，不需要`GITHUB_TOKEN`也能匿名下载。**

### 下载方式二：手动下载

去[Release页面](https://github.com/BCXiaoxue/RAG_Writing/releases/tag/models-v1.0.0)手动下载以下文件，放到对应路径：

| Release资产 | 放到这个本地路径 | SHA-256 |
|---|---|---|
| `essay-scorer-finetuned-v1-pytorch_model.bin` | `models/essay-scorer-finetuned/v1/pytorch_model.bin` | `036a56a7d205eca050dab5f7e4a38fbd70c6be0301f7600d70f174b315d14ba4` |
| `essay-scorer-finetuned-v1-tokenizer.json` | `models/essay-scorer-finetuned/v1/tokenizer.json` | — |
| `essay-scorer-finetuned-v1-tokenizer_config.json` | `models/essay-scorer-finetuned/v1/tokenizer_config.json` | — |
| `essay-scorer-custom-v1-pytorch_model.bin` | `models/essay-scorer-custom/v1/pytorch_model.bin` | `b113b4a7dc315577758e10b6d8414419315614c02545f2f5f10bb08205e1076c` |
| `essay-scorer-custom-v1-vocab.json` | `models/essay-scorer-custom/v1/vocab.json` | — |
| `essay-scorer-custom-v1-model_config.json` | `models/essay-scorer-custom/v1/model_config.json` | — |

下载后用`sha256sum <文件路径>`（或PowerShell的`Get-FileHash`）核对一下两个`.bin`文件的SHA-256，确认没有下载不完整。`training_log.json`（训练过程/QWK指标）体积小，已经直接提交在git仓库里的`models/essay-scorer-*/v1/`下，不需要单独下载。

### 如果没有下载模型权重会怎样

`src/agents/nodes.py`里的`scoring_tool_node`（评分）和`retrieval_agent_node`（RAG检索）在检测到`models/`或`data/processed/chroma_kb/`不存在时，会自动降级为Day1的占位启发式逻辑，**不会报错崩溃**，但会打印明确的`warnings.warn(...)`提示告诉你现在用的是占位结果、该跑什么命令来补全。跑`streamlit run app.py`或`scripts/e2e_graph_test.py`时注意看控制台有没有这类警告。

RAG知识库本身（`data/processed/chroma_kb/`）不在Release里，体积小（约1MB）、构建也快，直接跑`python -m src.rag.build_rubric_docs && python -m src.rag.build_kb`重新生成即可，不需要下载。
