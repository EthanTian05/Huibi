# RUNNING · 环境搭建 / 运行 / 测试

> Day1骨架代码已经写好（`src/`、`app.py`），本文档是实际的运行步骤。如果你改了代码的运行方式，回来同步更新本文档，保持"文档=实际能跑的步骤"。

## 0. 已知问题：某些环境下`pip install`会失败

Day1脚手架阶段的开发环境里，`pip install`会报`SSLEOFError`（连接被重置），但`curl`/`python -m urllib.request`访问同一个pypi地址完全正常（HTTP 200）。排查过的点：
- 换`--index-url`（清华镜像/官方pypi.org）都一样失败，不是镜像的问题；
- 升级pip到最新版（26.x）、加`--trusted-host`都没用；
- 不是Key/项目本身的问题，是那个特定网络环境对pip的HTTP连接模式不友好。

如果你也遇到这个报错：换一个网络（比如手机热点/不同的校园网出口）通常能解决；如果换网络还不行，可以尝试`pip install --proxy ...`指定一个可用代理，或者用conda环境试试`conda install`。**这不代表整个项目有问题**，只是这一层网络环境的问题。

## 1. 环境准备

```bash
# 建议使用虚拟环境（Day1已建好.venv，别的机器上需要重新建）
python -m venv .venv
.venv\Scripts\activate        # Windows

pip install -r requirements.txt
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

- **Day1已有的两个免安装验证脚本**（不需要`pip install`，Day1在受限网络环境里就是靠这两个验证的）：

```bash
python scripts/check_llm_key.py              # 验证.env里的DeepSeek/GLM Key能不能真的调通
PYTHONPATH=. python scripts/smoke_test_nodes.py   # 验证intake校验/评分占位逻辑/SQLite读写
```

- **完整链路测试**（需要`pip install -r requirements.txt`之后）：`streamlit run app.py`，手动跑一遍端到端提交流程；后续如果补充了`pytest`用例，再在这里记录跑法。至少要覆盖：
  - `EssayScorer.predict()`输入输出格式（Day2接入真实评分模型后）；
  - LangGraph路由逻辑（无效输入是否正确短路到`short_circuit_reject`）；
  - SQLite读写（提交记录能正确写入、历史查询能正确返回，已在`scripts/smoke_test_nodes.py`里覆盖）。
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
