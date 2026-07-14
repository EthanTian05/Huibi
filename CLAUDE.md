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

当前进度（本轮已经在真实GPU训练服务器上把主链路全部跑通，不再是"骨架"）：

- **全部真实跑通、不是占位**：数据（真实ASAP-AES 12879条清洗后样本，8个essay_set全覆盖）→ EDA → 两条评分模型训练（路径A微调DistilBERT测试集QWK=0.693，路径B自建BiLSTM从零训练QWK=0.622）→ RAG知识库（120个chunk，来自真实rubric+prompt数据）→ LangGraph全链路（intake→retrieval→scoring→grammar→feedback→coach→progress）→ SQLite持久化，全部用`scripts/e2e_graph_test.py`在训练服务器上验证过，`qualitative_feedback`/`revision_plan`是DeepSeek的真实生成内容，不是mock。Streamlit（`app.py`）也在服务器上以headless模式实测过能正常serve（HTTP 200）。
- **诚实的缺口**：分项`trait_scores`目前是整体分的占位复制，不是单独训练的多头输出（见`Docs/03-模型训练与微调方案.md`顶部说明，之前文档把这个写成"已确认主线方案"是不准确的，本轮已经改正）；`grammar_check_node`仍是Day3占位（没接`language_tool_python`）；`CriticAgentNode`反思循环没做（本来就是stretch goal）；正式的SSH部署（`Docs/RUNNING.md`第8节，部署到`121.41.238.92`）还没做。
- **本地开发环境限制**：本仓库所在的这个开发环境`pip install`用不了（网络层SSLEOFError，详情见"环境信息"），所以上述所有"真实跑通"都是在另一台训练服务器（`ssh retinascope-server`）上做的，不是在这台机器上。
- **模型权重通过GitHub Release分发，不进git历史**：微调模型的`pytorch_model.bin`约265MB，超过GitHub单文件100MB的硬限制。两条模型的权重+tokenizer/vocab/config已经从训练服务器拉回本地并上传到 [`models-v1.0.0`](https://github.com/BCXiaoxue/RAG_Writing/releases/tag/models-v1.0.0) 这个Release，`.gitignore`排除了所有模型产出物（权重/tokenizer/vocab/config），只保留体积小的`training_log.json`。**下载方式见根目录`README.md`「模型权重下载」和`scripts/download_models.py`**——仓库当前私有，下载需要在`.env`配好`GITHUB_TOKEN`，转public后就不需要了。`scoring_tool_node`/`retrieval_agent_node`在模型/知识库文件不存在时会自动降级回占位逻辑并打印`warnings.warn(...)`明确提示，不会报错崩溃、也不会静默装作是真实结果。
- 详细过程、踩过的坑（HF的Xet存储卡死、这台服务器根分区写满、pkill误杀生产容器的教训等）见`Docs/RUNNING.md`「0.5 本轮已经在训练服务器上把全部流程实际跑通了一遍」和`Docs/Progress.md`最新一轮记录。

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
│   ├── raw/                   原始ASAP-AES数据，gitignore（训练服务器上有真实数据，本地跑download.py可重新生成）
│   ├── processed/             score_ranges.json（真实，已提交）、eda/*.png（真实图表，已提交）；train/val/test.csv是gitignore的（跑preprocess.py重新生成）
│   └── kb/                    真实RAG知识库源文件：grammar_cards.md（手写）+ rubric_essay_set_1~8.md（从真实数据集提取的prompt/rubrics，已提交）
├── models/                    模型产出物(权重/tokenizer/vocab/config)全部gitignore，只保留训练日志；权重通过GitHub Release分发（见README.md）
│   ├── essay-scorer-finetuned/v1/training_log.json  路径A真实训练记录，测试集QWK=0.693
│   └── essay-scorer-custom/v1/training_log.json     路径B真实训练记录，测试集QWK=0.622
├── src/
│   ├── data_pipeline/         clean.py/eda.py/preprocess.py/download.py，已写好并在真实数据上跑通
│   ├── training/               common.py(QWK计算)/train_finetuned.py(路径A)/train_custom.py(路径B)/essay_scorer.py(推理封装)，已写好并训练出真实模型
│   ├── agents/                 state.py/llm.py/nodes.py/graph.py，已写好并端到端验证通过（含真实DeepSeek调用）
│   ├── rag/                    build_kb.py + build_rubric_docs.py，已写好并构建出真实120-chunk向量库
│   └── storage/                db.py，SQLite读写，已写好并验证通过
├── scripts/
│   ├── check_llm_key.py       不依赖任何pip包，验证.env里的LLM Key能不能调通
│   ├── smoke_test_nodes.py    验证不依赖langchain的节点逻辑+SQLite读写
│   └── e2e_graph_test.py      完整端到端验证（真实DeepSeek+真实评分模型+真实RAG检索），已在训练服务器上跑通
├── app.py                      Streamlit入口，已在训练服务器上headless模式验证能正常serve(HTTP 200)
├── README.md                   GitHub仓库首页说明，重点是"模型权重下载"一节
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
| `06-本轮成果与复现步骤.md` | **本轮真实训练结果汇总+复现步骤，第一次接手/想快速了解当前真实进度先看这个** |
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

需要先`pip install -r requirements.txt`的（在训练服务器`retinascope-server`上已验证通过，这台本地开发环境pip用不了）：

```bash
PYTHONPATH=. python scripts/e2e_graph_test.py    # 完整端到端：真实DeepSeek+真实评分模型+真实RAG检索
streamlit run app.py                              # 四页面UI，headless模式已验证能正常serve
```

## 不要重新踩的坑

- 不要把"调用大模型API直接打分"当成加分项里的"自定义构建模型"——评分必须来自小组自己训练的模型（微调BERT系 + 自建BiLSTM两条路径，见`Docs/03-模型训练与微调方案.md`），大模型API只负责生成定性反馈/推理/RAG问答，两者分工不能混淆，否则加分项和"微调模型必须自己完成"的规定都可能不成立。
- 不要为了"看起来花哨"而在LangGraph里堆砌过多Agent节点/循环——4天工期下，核心链路（校验→检索→评分→反馈→辅导→进步追踪）够用且可控；反思/自我批评循环等属于Day4有余力才做的加分项，见`Docs/04-四天开发计划与分工.md`里的"有余力再做"标注，不要把stretch goal当成必须交付项而挤占主线时间。
- 参考的开源仓库（见`Docs/00-项目总览.md`参考资料）只用于理解架构思路，不要直接搬运代码当作自己的实现提交——尤其是两条评分模型的训练部分，题目要求"微调模型的构建和训练，必须自己完成"，答辩时要能讲清楚每一行关键逻辑。
- **真实密钥/服务器凭证一律只进`.env`，不进`Docs/*.md`**：上一轮DeepSeek的真实API Key被直接粘贴进了`Docs/TODO.md`这种会当作交付材料提交的文档里，已经清理并补了`.gitignore`。以后任何Key/密码/私钥内容，团队协作时通过口头或私聊分发，不要再写进Markdown文档，也不要`git add`任何`.env`文件。
- **DeepSeek V4 Flash是推理模型，`max_tokens`给小了会拿到空字符串**：会先输出`reasoning_content`再输出`content`，`max_tokens`太小（比如个位数/几十）的话推理阶段就把预算耗尽，`content`是空字符串、`finish_reason`是`"length"`，表现上像是"调用成功但什么都没返回"，容易被误判成Key错了或Prompt有问题。`src/agents/llm.py`里默认给了`DEFAULT_MAX_TOKENS = 2048`，改这个值之前先用`scripts/check_llm_key.py`验证过再改，别为了省token改小。
- **这个开发环境`pip install`会失败（SSLEOFError），但curl/urllib能正常访问同一个host**：报错是`pip`自己的HTTP客户端连接被重置，不是真的没网络，也不是Key/网站的问题。如果换一台机器还遇到同样情况，参考`Docs/RUNNING.md`的排查记录，不要一上来就怀疑是防火墙挡了pypi。
- **在共用服务器上，停止自己的进程只能用精确PID，绝不能`pkill -f`模式匹配**：本轮有一次事故——`pkill -f 'streamlit run app.py'`同时杀掉了同一台机器上田溯开的RetinaScope生产Docker容器（命令行里同样包含这几个字），导致约1分钟的服务中断（Docker的`restart: unless-stopped`自动拉起来了，没造成数据损失，但这是真实发生过的事故，不是假设）。以后一律`ps aux | grep <关键词>`先看清楚PID，只`kill <精确PID>`，见`Docs/RUNNING.md`「0.5」第2条。
- **训练服务器(`retinascope-server`)的根分区(`/`)是满的，只能在`/data/wangchen/tiansukai/RAG/`下操作**；HuggingFace的大文件下载要加`HF_HUB_DISABLE_XET=1`否则会卡死在0字节；Python裸`urllib`/`ssl`调用在这台机器上会因为自定义OpenSSL证书目录是空的而报`certificate verify failed`（`langchain_openai`/`requests`等库因为默认走`certifi`不受影响）。完整细节见`Docs/RUNNING.md`「0.5 本轮已经在训练服务器上把全部流程实际跑通了一遍」。
- **GitHub单文件超100MB会被硬性拒绝push，Git LFS和"发布Release"是两种不同的应对方案**：微调模型的265MB权重文件选了后者（GitHub Release资产），不是Git LFS，两者操作方式和后续下载方式完全不同，别搞混——Release资产用`scripts/download_models.py`或`Docs`里记录的REST API方式下载，不是`git lfs pull`。
- **仓库私有时，GitHub Release资产不能匿名下载**：`browser_download_url`直接请求私有仓库的Release资产会返回404，必须用`Authorization: Bearer <token>`走`https://api.github.com/repos/{owner}/{repo}/releases/assets/{id}`这个API端点（`Accept: application/octet-stream`）才能拿到文件内容，`scripts/download_models.py`已经处理了这个区别（有`GITHUB_TOKEN`就走API下载，没有就走匿名`browser_download_url`，仓库转public后两种都行）。

## 已确认、不要再改的设计决策

- 项目题目：慧笔（HuiBi）——基于LangChain+LangGraph的英语写作智能批改与个性化学习伴学系统。领域选定为"教育"（用户明确要求：若有好获取的开源数据集则优先教育领域），数据集为Kaggle ASAP-AES。
- LLM推理后端：主力DeepSeek V4 Flash，免费/兜底GLM-4.7-Flash，**两个Key都已验证真实可用**（`scripts/check_llm_key.py`两个都返回"调通成功"），双供应商fallback真的有两条腿了。真实API Key存在本地`01-源代码/.env`（已被`.gitignore`排除），**不要把真实Key写进任何`Docs/*.md`或其他会被提交的文件**——这个问题已经连续两轮发生（DeepSeek Key、后来又是Kaggle Token+GLM Key），每次都清理了但别再重犯，见`Docs/TODO.md`"安全提醒"。
- 模型构建：三条路径都做——① DeepSeek/GLM负责生成类任务；② 微调BERT系模型（路径A，实际用`distilbert-base-uncased`，测试集QWK=0.693）；③ 从零构建、不依赖预训练权重的BiLSTM+Attention模型（路径B，测试集QWK=0.622）。两个自训练评分模型分别覆盖"预训练模型-微调"和"自定义构建模型"两个加分选项，已经训练完成、有真实QWK对比数据，见`Docs/03-模型训练与微调方案.md`。
- 评分模型的分项输出（内容/结构/语言）**目前是整体分的占位复制，不是真正的多头训练**——之前文档写成"已确认主线方案"是不准确的，本轮训练时发现各essay_set的trait标注字段不统一、需要额外的掩码多任务设计，已把这个改成Day3/4待办，不要再当成"已完成"来汇报，见`Docs/03-模型训练与微调方案.md`顶部说明。
- "225原则"：指训练循环"2层循环(epoch/batch)+2个遍历对象+5个核心步骤(梯度清零→正向传播→损失计算→反向传播→参数更新)"，是训练脚本的底线结构，可在此基础上叠加更好的方案，不要再当成未解之谜去问，直接照`Docs/03-模型训练与微调方案.md`写代码。
- 前端部署框架：Streamlit（与田溯开已有的RetinaScope项目技术栈一致，团队上手最快，且是题目允许的加分部署选项之一），部署目标是自有服务器`121.41.238.92`（root，端口22，私钥登录），通过SSH部署，见`Docs/RUNNING.md`第8节。
- Embedding模型：走开源本地模型（不用大模型API的embedding接口），具体型号Day1定。
- 创意加分模块：学习进步仪表盘 + 个性化弱项雷达图 + 自适应练习推荐的"持续学习闭环"，区别于一次性打分工具，用于申请10~15分创意加分。
- 文档语言：`Docs/`下所有文档一律使用中文撰写，服务于中文答辩场景。
- 模型权重分发：不进git（超GitHub 100MB单文件限制），发布到GitHub Release（`models-v1.0.0`），用`scripts/download_models.py`下载，见`README.md`。
- 数据集渠道：默认HuggingFace非gated镜像；Kaggle官方渠道的Token已就绪但下载被"需手动接受比赛规则"卡住，见`Docs/TODO.md`。

## 环境信息

- 操作系统：Windows 11；Shell以PowerShell为主；本地Python是Miniconda自带的3.9.1。
- git仓库已建好并关联远程：`https://github.com/BCXiaoxue/RAG_Writing.git`，分支`main`，当前私有，以后转public。**`git init`时`.gitignore`先于其他文件`git add`，已确认`.env`/`.venv/`没有被追踪**；远程原本有个`LICENSE`文件，已用`git merge --allow-unrelated-histories`合并进来，没有强推/覆盖过历史。
- `01-源代码/.venv/`是本地虚拟环境（已gitignore）。**这个开发环境的`pip install`目前用不了**：能`curl`/`python -m urllib.request`正常访问pypi.org和清华镜像（HTTP 200），但`pip install`本身会报`SSLEOFError`连接被重置，换了默认源、`--index-url`、加了`dangerouslyDisableSandbox`都没用，怀疑是这个sandbox网络环境对pip的连接模式（长连接/HTTP流式）有特殊限制。**这不代表其他机器/团队成员的环境也会有这个问题**，只是本轮没能在这个环境里`pip install -r requirements.txt`跑通LangGraph/Streamlit的实际调用，遇到同样报错时可以参考这个记录，不用重新排查一遍。
- 已存在`01-源代码/.env`（真实密钥，已被`.gitignore`排除）、`.env.example`（占位模板）、`.gitignore`。目前`.env`里有：`DEEPSEEK_API_KEY`/`GLM_API_KEY`（均已验证）、`KAGGLE_API_TOKEN`（已验证能访问API，下载被"需手动接受比赛规则"卡住）、`GITHUB_TOKEN`（**有仓库写权限，用于发布Release，比其他Key更敏感**）、`DEPLOY_HOST`等部署服务器信息。
- **训练用GPU资源已确定**：`ssh retinascope-server`（配置在`~/.ssh/config`，IdentityFile`id_ed25519_retinascope`），8×A100 40GB，Python 3.10.12。项目代码/环境放在`/data/wangchen/tiansukai/RAG/`（**不是**`/root/`下，根分区已满，见"不要重新踩的坑"）。这台机器同时也部署着田溯开的RetinaScope项目（Docker容器`retinascope_app`，端口8501），操作时要注意不要影响到它（尤其是进程管理，只能精确PID）。
- 部署目标服务器`121.41.238.92`和训练服务器`retinascope-server`是**两台不同的机器**，不要混淆：前者用于Day4最终部署跑Streamlit对外服务，后者用于Day2/3训练模型、开发调试。
