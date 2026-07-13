# RUNNING · 环境搭建 / 运行 / 测试

> 代码尚未搭建，本文档写的是Day1开始搭建骨架时**应该遵循的目标流程**。搭建过程中如果实际做法和这里不一致，请回来更新本文档，保持"文档=实际能跑的步骤"，不要让它变成写完就过期的空文档。

## 1. 环境准备

```bash
# 建议使用虚拟环境
python -m venv .venv
.venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

`requirements.txt`（Day1按实际选型确定版本号）预计包含：

```
langchain
langgraph
langchain-community
transformers
torch
sentence-transformers
chromadb
streamlit
pandas
scikit-learn
matplotlib
seaborn
python-dotenv
language-tool-python   # 语法检查，如最终采用
```

## 2. 环境变量

`01-源代码/.env`已经建好（内含真实DeepSeek Key），`.env.example`是给团队其他成员复制用的模板。**`.env`已加入`.gitignore`，不要提交进版本库，也不要把里面的真实Key再粘贴回任何`Docs/*.md`文档**：

```
DEEPSEEK_API_KEY=...        # 主力LLM
DEEPSEEK_MODEL_NAME=deepseek-v4-flash
GLM_API_KEY=...             # 免费兜底LLM
GLM_MODEL_NAME=glm-4.7-flash
LLM_PROVIDER=deepseek
LLM_FALLBACK_PROVIDER=glm
```

代码里对接LLM时建议做一层provider抽象：优先调用`LLM_PROVIDER`指定的模型，调用失败/超限时自动切换到`LLM_FALLBACK_PROVIDER`，这样答辩现场如果DeepSeek临时不可用，还能用GLM兜底演示。

## 3. 数据准备

```bash
# 1. 下载Kaggle ASAP-AES数据集至 data/raw/
# 2. 清洗
python -m src.data_pipeline.clean
# 3. EDA（产出图表到 data/processed/eda/）
python -m src.data_pipeline.eda
# 4. 预处理（分词、归一化、划分数据集）
python -m src.data_pipeline.preprocess
```

## 4. 训练两条评分模型

```bash
# 路径A：微调（基于预训练权重）
python -m src.training.train_finetuned \
    --model_name distilbert-base-uncased \
    --epochs 5 \
    --output_dir models/essay-scorer-finetuned/v1

# 路径B：自定义构建（从零训练，不加载任何预训练权重）
python -m src.training.train_custom \
    --arch bilstm-attention \
    --epochs 10 \
    --output_dir models/essay-scorer-custom/v1

python -m src.training.evaluate --model_dir models/essay-scorer-finetuned/v1
python -m src.training.evaluate --model_dir models/essay-scorer-custom/v1
# 各自输出测试集QWK指标，同时产出loss/QWK曲线图，便于横向对比
```

## 5. 构建RAG知识库

```bash
# 将 data/kb/ 下的rubric/语法卡片/范文文本切分并写入Chroma向量库
python -m src.rag.build_kb
```

## 6. 启动应用

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501`，四个页面：提交批改 / 反馈详情 / 历史进步仪表盘 / 写作知识库问答。

## 7. 测试

- **单元测试**：`pytest tests/`，至少覆盖：
  - `EssayScorer.predict()`输入输出格式；
  - LangGraph路由逻辑（无效输入是否正确短路到`ShortCircuitReject`）；
  - SQLite读写（提交记录能正确写入、历史查询能正确返回）。
- **端到端手动测试清单**（Day3~4联调时逐项过）：
  - [ ] 提交一篇明显高分作文，检查评分、反馈、雷达图是否合理。
  - [ ] 提交一篇有明显语法问题的作文，检查`GrammarCheckNode`是否能识别出对应错误并在反馈中体现。
  - [ ] 提交一篇过短/无意义文本，检查是否被`IntakeValidatorNode`正确拒绝并给出提示。
  - [ ] 同一账号连续提交2~3篇作文，检查"历史进步仪表盘"趋势图是否正确更新。
  - [ ] 断网/API Key失效场景下，检查前端是否有合理报错提示而不是直接崩溃（决定是否需要为答辩现场加一层fallback）。

## 8. 部署（已确认：SSH部署至自有服务器）

- 目标服务器：`121.41.238.92`，用户`root`，端口22，私钥登录（私钥文件留在各自本机的`~/.ssh/`下，不要拷贝进仓库）。
- 部署方式：

```bash
# 1. 把代码同步到服务器（排除.env等敏感/大文件，用.gitignore同名规则参考）
rsync -avz --exclude-from=.gitignore ./ root@121.41.238.92:/opt/huibi/

# 2. 登录服务器，安装依赖
ssh root@121.41.238.92
cd /opt/huibi && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. 服务器上单独准备.env（不要通过rsync同步含真实Key的.env，改为登录后手动创建或用scp单独传输一次）
# 4. 后台常驻运行（二选一）
#   a) tmux/nohup（最简单，适合4天工期）
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
#   b) systemd服务（更规范，如时间允许可做）

# 5. 确认服务器防火墙/安全组放通8501端口（或用nginx反代到80）
```

- 答辩前必须实测：从答辩现场网络能否访问`http://121.41.238.92:8501`（校园网/外网限制、防火墙规则都可能导致连不上），并准备好`RUNNING.md`第7节提到的离线演示预案兜底。
- 安全提醒：服务器用`root`直接部署仅为4天工期图快，如果这个项目之后要长期运行/给更多人用，建议改成非root部署用户；私钥文件本身任何时候都不要提交进仓库或粘贴进文档。
