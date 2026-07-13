# CLAUDE.md
> Use advisor and dynamic workflow globally
> 本文件是创新创业项目的工作说明，**每次在这个仓库里开始任务前必须先读一遍**。
> 项目进度、每轮改了什么、还有什么没做见 `Docs/Progress.md`；待办清单见 `Docs/TODO.md`；怎么把系统跑起来/怎么测试见 `Docs/RUNNING.md`；

## 工作方式（全局遵守）

- **多用 `advisor` 工具**：开始实质性改动前、以及自认为完成一轮工作后，都调用一次 advisor 做确认，不要闷头一次性写完再汇报。这个项目历次返工大多是"想当然实现了 → advisor 或用户指出理解偏了"，advisor 能在动手写代码前拦住大部分这类问题。
- **动态迭代，别一次锁死大计划**：需求经常是"做完一轮反馈 → 用户看了效果 → 下一轮再改几个点"这种滚动式协作，不是一次性给完整需求。收到一批反馈后用 `TodoWrite` 拆成可勾选的小项、做完一项勾一项、有歧义的地方按合理判断做但**必须**在汇报里明说是自己的理解，不要预先规划完"整个项目"再一次性执行。
- 每一轮反馈做完之后，**必须**把这轮做了什么写进 `Docs/Progress.md`（照现有条目的格式写：小标题 + 讲清楚"根因是什么、怎么改的、怎么验证的"，而不是"改好了"这种空话）。如果某条反馈是按自己的理解做的取舍（不是字面唯一解），除了在回复里说明，也要在 `Docs/TODO.md`"需要你决策"里留一条，别自己悄悄替用户拍板。


## 项目是什么

**慧笔（HuiBi）——基于LangChain+LangGraph的英语写作智能批改与个性化学习伴学系统**

面向中国英语学习者（四六级/考研英语/雅思写作场景）的多智能体写作辅导工具。学生提交一篇英语作文，系统在数分钟内给出：

1. 量化评分——由小组自行微调的评分模型给出（不是直接问大模型"打个分"）；
2. 结构化定性反馈——由多个LLM Agent协作生成（语法纠错、结构建议、用词建议，中英双语解释）；
3. 个性化学习闭环——结合该学生历史提交记录，给出弱项雷达图和针对性练习推荐。

这是"绍兴大学-大模型实训"小组项目（Langchain+LLM+LangGraph智能体方向），团队4人，工期4天。详细的立项理由、需求对照表、架构设计、数据/模型方案、4天分工、答辩材料全部在 `Docs/` 目录下，**开始写代码前请先完整读一遍 `Docs/00-项目总览.md` 和 `Docs/01-系统架构与Agent设计.md`**。

当前进度（Day1已完成脚手架）：`src/`、`app.py`已经是真代码，不再只是文档。已实现：`EssayReviewState`、DeepSeek/GLM双供应商LLM封装（含fallback）、7个LangGraph节点（`intake_validator`真实校验、`feedback_agent`/`coach_agent`真实调用DeepSeek、`retrieval_agent`/`scoring_tool`/`grammar_check`是Day2占位实现）、SQLite读写、数据清洗/EDA/预处理脚本、RAG建库脚本+KB种子内容、Streamlit四页面UI。**本仓库当前开发环境`pip install`被网络环境挡住**（详情见"环境信息"），所以LangGraph/Streamlit相关代码只做了语法检查，没能实际跑起来；不依赖这些包的部分（intake校验、评分占位逻辑、SQLite）已经用`scripts/smoke_test_nodes.py`跑通，DeepSeek Key已经用`scripts/check_llm_key.py`（纯标准库）验证调通。**下一个打开这个仓库的人，第一件事是在一个pip能正常工作的环境里`pip install -r requirements.txt`后跑一遍`streamlit run app.py`，确认langgraph/langchain-openai的实际API调用没问题**，见`Docs/TODO.md`"GitHub仓库与代码现状"一节。

代码已推送到`https://github.com/BCXiaoxue/RAG_Writing.git`（`main`分支），仓库当前私有，以后会转public。

## 目录结构

```
01-源代码/
├── CLAUDE.md                  本文件
├── .env                       真实密钥（已gitignore，DeepSeek/GLM Key、部署服务器信息）
├── .env.example               占位模板，给团队其他成员复制用
├── .gitignore                 排除.env、.venv、大文件、__pycache__等
├── .venv/                     本地Python虚拟环境（已gitignore）
├── Docs/                      规划与答辩支持文档，见下方列表
├── data/
│   ├── raw/                   原始ASAP-AES数据（需手动从Kaggle下载，尚为空）
│   ├── processed/             清洗/预处理后的训练数据（Day2产出，尚为空）
│   └── kb/                    RAG知识库源文件，目前只有各1篇rubric/语法卡片占位示例
├── models/                    Day2训练产出的模型权重存放处，尚为空
│   ├── essay-scorer-finetuned/  路径A：微调BERT系模型权重与分词器
│   └── essay-scorer-custom/     路径B：自建BiLSTM模型权重（不依赖预训练）
├── src/
│   ├── data_pipeline/         clean.py/eda.py/preprocess.py，已写好，需要A先手动下载数据集才能跑
│   ├── training/               Day2任务，目前只有空的__init__.py
│   ├── agents/                 state.py/llm.py/nodes.py/graph.py，已写好，见下方"怎么跑起来"
│   ├── rag/                    build_kb.py已写好（Day2任务，依赖chromadb等还没验证过）
│   └── storage/                db.py，SQLite读写，已写好并验证通过
├── scripts/
│   ├── check_llm_key.py       不依赖任何pip包，验证.env里的LLM Key能不能调通
│   └── smoke_test_nodes.py    验证不依赖langchain的节点逻辑+SQLite读写
├── app.py                      Streamlit入口，已写好，未在本环境验证运行
├── requirements.txt
└── .env.example
```

`Docs/` 目录内容：

| 文件 | 内容 |
|---|---|
| `00-项目总览.md` | 题目、立项理由、需求与加分项对照表、参考资料 |
| `01-系统架构与Agent设计.md` | LangGraph状态图、各Agent职责、RAG知识库设计、工具清单 |
| `02-数据集与数据处理方案.md` | 数据来源、清洗规则、EDA计划、预处理步骤 |
| `03-模型训练与微调方案.md` | 模型选型（微调+自建两条路径）、训练配置、评估指标、"225原则"含义说明 |
| `04-四天开发计划与分工.md` | 4人4天任务拆解与里程碑 |
| `05-答辩材料与演示话术.md` | PPT大纲、演示脚本、预设问答 |
| `RUNNING.md` | 环境搭建、运行、测试步骤 |
| `Progress.md` | 每轮工作记录 |
| `TODO.md` | 待办清单 + 需要你决策的事项 |

## 怎么跑起来 / 怎么测试

严格按 `Docs/RUNNING.md` 执行（环境准备 → 数据准备 → 微调模型 → 建知识库 → 跑Streamlit → 测试）。任何运行方式的变更都要同步改 `RUNNING.md`，不要让文档和实际脚本脱节。

不需要`pip install`任何东西就能跑的两个验证脚本（本仓库当前环境已验证通过）：

```bash
python scripts/check_llm_key.py       # 验证.env里的DeepSeek/GLM Key能不能调通
PYTHONPATH=. python scripts/smoke_test_nodes.py   # 验证intake校验/评分占位逻辑/SQLite读写
```

需要先`pip install -r requirements.txt`才能跑、本仓库当前环境还没能验证的：

```bash
streamlit run app.py    # 完整的LangGraph多智能体链路 + 四页面UI
```

## 不要重新踩的坑

- 不要把"调用大模型API直接打分"当成加分项里的"自定义构建模型"——评分必须来自小组自己训练的模型（微调BERT系 + 自建BiLSTM两条路径，见`Docs/03-模型训练与微调方案.md`），大模型API只负责生成定性反馈/推理/RAG问答，两者分工不能混淆，否则加分项和"微调模型必须自己完成"的规定都可能不成立。
- 不要为了"看起来花哨"而在LangGraph里堆砌过多Agent节点/循环——4天工期下，核心链路（校验→检索→评分→反馈→辅导→进步追踪）够用且可控；反思/自我批评循环等属于Day4有余力才做的加分项，见`Docs/04-四天开发计划与分工.md`里的"有余力再做"标注，不要把stretch goal当成必须交付项而挤占主线时间。
- 参考的开源仓库（见`Docs/00-项目总览.md`参考资料）只用于理解架构思路，不要直接搬运代码当作自己的实现提交——尤其是两条评分模型的训练部分，题目要求"微调模型的构建和训练，必须自己完成"，答辩时要能讲清楚每一行关键逻辑。
- **真实密钥/服务器凭证一律只进`.env`，不进`Docs/*.md`**：上一轮DeepSeek的真实API Key被直接粘贴进了`Docs/TODO.md`这种会当作交付材料提交的文档里，已经清理并补了`.gitignore`。以后任何Key/密码/私钥内容，团队协作时通过口头或私聊分发，不要再写进Markdown文档，也不要`git add`任何`.env`文件。
- **DeepSeek V4 Flash是推理模型，`max_tokens`给小了会拿到空字符串**：会先输出`reasoning_content`再输出`content`，`max_tokens`太小（比如个位数/几十）的话推理阶段就把预算耗尽，`content`是空字符串、`finish_reason`是`"length"`，表现上像是"调用成功但什么都没返回"，容易被误判成Key错了或Prompt有问题。`src/agents/llm.py`里默认给了`DEFAULT_MAX_TOKENS = 2048`，改这个值之前先用`scripts/check_llm_key.py`验证过再改，别为了省token改小。
- **这个开发环境`pip install`会失败（SSLEOFError），但curl/urllib能正常访问同一个host**：报错是`pip`自己的HTTP客户端连接被重置，不是真的没网络，也不是Key/网站的问题。如果换一台机器还遇到同样情况，参考`Docs/RUNNING.md`的排查记录，不要一上来就怀疑是防火墙挡了pypi。

## 已确认、不要再改的设计决策

- 项目题目：慧笔（HuiBi）——基于LangChain+LangGraph的英语写作智能批改与个性化学习伴学系统。领域选定为"教育"（用户明确要求：若有好获取的开源数据集则优先教育领域），数据集为Kaggle ASAP-AES。
- LLM推理后端：主力DeepSeek V4 Flash，免费/兜底GLM-4.7-Flash，双供应商、代码里做fallback切换。真实API Key存在本地`01-源代码/.env`（已被`.gitignore`排除），**不要把真实Key写进任何`Docs/*.md`或其他会被提交的文件**——上一轮曾经把Key直接粘贴进`Docs/TODO.md`，已经清理并补了`.gitignore`，不要重犯。
- 模型构建：三条路径都做——① DeepSeek/GLM负责生成类任务；② 微调BERT系模型（路径A）；③ 从零构建、不依赖预训练权重的BiLSTM+Attention模型（路径B）。两个自训练评分模型分别覆盖"预训练模型-微调"和"自定义构建模型"两个加分选项，且要做横向对比，见`Docs/03-模型训练与微调方案.md`。
- 评分模型采用多头输出（内容/结构/语言分项评分），是主线方案，不是"时间不够就降级"的条件项。
- "225原则"：指训练循环"2层循环(epoch/batch)+2个遍历对象+5个核心步骤(梯度清零→正向传播→损失计算→反向传播→参数更新)"，是训练脚本的底线结构，可在此基础上叠加更好的方案，不要再当成未解之谜去问，直接照`Docs/03-模型训练与微调方案.md`写代码。
- 前端部署框架：Streamlit（与田溯开已有的RetinaScope项目技术栈一致，团队上手最快，且是题目允许的加分部署选项之一），部署目标是自有服务器`121.41.238.92`（root，端口22，私钥登录），通过SSH部署，见`Docs/RUNNING.md`第8节。
- Embedding模型：走开源本地模型（不用大模型API的embedding接口），具体型号Day1定。
- 创意加分模块：学习进步仪表盘 + 个性化弱项雷达图 + 自适应练习推荐的"持续学习闭环"，区别于一次性打分工具，用于申请10~15分创意加分。
- 文档语言：`Docs/`下所有文档一律使用中文撰写，服务于中文答辩场景。

## 环境信息

- 操作系统：Windows 11；Shell以PowerShell为主；本地Python是Miniconda自带的3.9.1。
- git仓库已建好并关联远程：`https://github.com/BCXiaoxue/RAG_Writing.git`，分支`main`，当前私有，以后转public。**`git init`时`.gitignore`先于其他文件`git add`，已确认`.env`/`.venv/`没有被追踪**；远程原本有个`LICENSE`文件，已用`git merge --allow-unrelated-histories`合并进来，没有强推/覆盖过历史。
- `01-源代码/.venv/`是本地虚拟环境（已gitignore）。**这个开发环境的`pip install`目前用不了**：能`curl`/`python -m urllib.request`正常访问pypi.org和清华镜像（HTTP 200），但`pip install`本身会报`SSLEOFError`连接被重置，换了默认源、`--index-url`、加了`dangerouslyDisableSandbox`都没用，怀疑是这个sandbox网络环境对pip的连接模式（长连接/HTTP流式）有特殊限制。**这不代表其他机器/团队成员的环境也会有这个问题**，只是本轮没能在这个环境里`pip install -r requirements.txt`跑通LangGraph/Streamlit的实际调用，遇到同样报错时可以参考这个记录，不用重新排查一遍。
- 已存在`01-源代码/.env`（真实密钥，已被`.gitignore`排除）、`.env.example`（占位模板）、`.gitignore`。这三个文件是Day1新增的，不用重新决策供应商。
- 仍未确定：训练用GPU资源来源（本地/Colab，注意部署服务器`121.41.238.92`不建议用来跑训练，只用来跑Streamlit服务）。
