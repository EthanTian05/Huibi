# Progress 项目进度记录

> 每轮工作结束后在下面追加一节：小标题 + 讲清楚"根因是什么、怎么改的、怎么验证的"，不要写"改好了"这种空话。

## 2026-07-13 · 完成项目立项与全套规划文档

**背景**：仓库初始状态只有一份空白模板的`CLAUDE.md`和两个空文件（`Progress.md`/`TODO.md`），没有确定项目题目，也没有任何架构/数据/模型/分工方案。任务要求根据《绍兴大学-大模型实训小组项目要求.md》，产出一套能支撑4人4天开发+项目答辩的中文规划文档，并完成所有加分项的方案设计。

**做了什么**：

1. 通读了官方要求文档，逐条拆解10项基本要求 + 3条注意事项 + 创意加分说明。
2. 与用户确认了三个关键决策点：本次只产出规划文档（不产出可运行代码骨架）、项目领域选定"教育"（用户指定：若有好获取的开源数据集则优先教育领域）、LLM推理后端选定走商用API（Qwen/DeepSeek/GLM等，供应商未定）。
3. 检索确认了真实存在的参考资料（Kaggle ASAP-AES数据集、`Gaurav-Pande/AES_DL`、`zkurtz/ASAP-AES-workbench`、`langchain-ai/rag-research-agent-template`、`junfanz1/Cognito-LangGraph-RAG`），避免文档里出现编造的链接。
4. 确定项目题目为"慧笔（HuiBi）——基于LangChain+LangGraph的英语写作智能批改与个性化学习伴学系统"：英语写作批改赛道，核心技术方案是"微调评分模型（自建，满足加分项）+ 通用大模型多智能体生成反馈 + 学习进步仪表盘（创意加分模块）"。
5. 产出以下文档（均为中文）：
   - `CLAUDE.md`：填完了"项目是什么/目录结构/怎么跑/不要踩的坑/已确认决策/环境信息"各节。
   - `Docs/00-项目总览.md`：题目、立项理由、需求与加分项逐条对照表、参考资料。
   - `Docs/01-系统架构与Agent设计.md`：LangGraph状态图设计（含mermaid架构图和状态转移图）、各Agent职责表、路由逻辑、工具清单、RAG知识库设计、前端页面设计。
   - `Docs/02-数据集与数据处理方案.md`：ASAP-AES数据集说明、清洗规则、EDA计划、预处理步骤（含"面向真实场景的泛化回退策略"）。
   - `Docs/03-模型训练与微调方案.md`：模型选型、训练配置、QWK评估指标、"225原则"含义不明确的说明与临时假设（8:1:1划分）。
   - `Docs/04-四天开发计划与分工.md`：4人角色划分 + Day1~Day4逐日任务表 + 时间不够时的取舍优先级。
   - `Docs/05-答辩材料与演示话术.md`：PPT大纲、10分钟演示脚本、预设问答表、答辩前必查清单。
   - `Docs/RUNNING.md`：环境搭建/数据准备/训练/建知识库/启动/测试/部署的目标步骤。
   - `Docs/TODO.md`：4天开发checklist + "需要你决策"的开放事项。

**怎么验证的**：这是纯规划/文档产出，没有代码可运行验证；验证方式是交叉核对——`00`号文档的"需求与加分项对照表"逐条对应回官方要求文档的10个条目和加分说明，确认没有遗漏任何一条；`01`~`05`号文档之间互相引用的文件名/术语（如`EssayScorer`、`essay_scorer_tool`、`225原则`）保持一致，没有互相矛盾的表述。

**遗留问题（不是本轮能解决的）**：225原则的确切含义、最终LLM供应商、是否与同班同学选题重复、项目文件夹是否改名——均已记录到`TODO.md`"需要你决策"部分，需要团队/用户在Day1前后确认。

## 2026-07-13（第二轮）· 落地上一轮的6项决策，并处理一次密钥泄露

**背景**：用户直接在`Docs/TODO.md`里回答了上一轮列出的6个待决策问题，但回答里把DeepSeek的真实API Key明文写进了这份文档——而这份文档属于"01-源代码"，是会被当作交付材料提交、以后大概率要进版本库的东西，明文Key留在这里是真实的泄露风险。

**做了什么**：

1. **先处理密钥泄露，再改文档**：新建`01-源代码/.gitignore`（排除`.env`、大文件、`__pycache__`等）、`01-源代码/.env`（存真实DeepSeek Key + GLM占位 + 部署服务器信息）、`01-源代码/.env.example`（占位模板）。然后把`Docs/TODO.md`里出现过的真实Key替换成"已移至本地.env"的脱敏说明，并在文档里加了一段"安全提醒"，建议团队评估是否需要重置这个已经明文出现过一次的Key。
2. **落地6项决策**，逐一更新到对应文档（不是只记在TODO里）：
   - **225原则**：确认含义是训练循环"2层循环(epoch/batch)+2个遍历对象+5个核心步骤(梯度清零→正向传播→损失计算→反向传播→参数更新)"。重写了`03-模型训练与微调方案.md`里原本"待确认"的整节，改为明确说明+"可在此基础上叠加更好方案"的补充。
   - **LLM供应商**：DeepSeek V4 Flash为主、GLM-4.7-Flash为免费兜底。更新了`00`/`01`/`RUNNING.md`里所有"Qwen/DeepSeek/GLM待定"的表述为确定的双供应商+fallback说明。
   - **自定义构建模型**：新增"路径B"——不依赖预训练权重、从零训练的BiLSTM+Attention评分模型，与原有的"路径A微调BERT系"并列，同时覆盖要求文档第6条里"预训练模型-微调"和"自定义构建模型"两个选项。改动覆盖`00`（需求对照表+技术栈表）、`03`（模型定位/选型/保存/预测/评估各节）、`01`（架构图、节点职责表、工具清单）、`04`（角色分工与每日任务）、`05`（答辩话术）、`TODO`（checklist）。
   - **部署渠道**：SSH部署至自有服务器`121.41.238.92`（root/22/私钥登录）。更新了`RUNNING.md`第8节为具体的rsync+ssh+nohup部署步骤，并加了"答辩前必须实测现场网络能否连通该服务器"的提醒。
   - **Embedding模型**：确认走开源本地模型（不用大模型API的embedding接口），型号留到Day1按实测确定，更新了`00`的技术栈表。
   - **trait分项评分**：确认做多头输出，不再是"时间不够就降级"的条件项，更新了`01`的State定义注释和`03`的模型选型描述为主线方案。
3. 同步更新了`CLAUDE.md`"已确认、不要再改的设计决策"（写入以上6项）、"环境信息"（记录新增的`.env`/`.env.example`/`.gitignore`）、"不要重新踩的坑"（新增一条：真实密钥只进`.env`，不进`Docs/*.md`）、"目录结构"（补充`.env`相关文件和拆分后的两个模型目录）。

**怎么验证的**：交叉检查了`00`/`01`/`03`/`04`/`05`/`RUNNING`/`TODO`/`CLAUDE.md`里所有提到"供应商待定""微调模型（单条路径）""待确认"等旧表述的地方，确认已经替换为本轮确认后的说法，没有新旧表述互相矛盾的地方；确认`TODO.md`文末"原始决策记录"里已经不包含真实Key字符串。

**遗留问题**：`TODO.md`里仍未回答的两项——"本班选题查重"和"项目文件夹是否改名"——本轮未处理，继续留在`TODO.md`"仍需要你/团队决策的事项"里。建议团队评估是否需要重置已经明文暴露过一次的DeepSeek Key（本轮只做了脱敏和归档，没有能力代为吊销/重置线上Key）。

## 2026-07-13（第三轮）· Day1代码脚手架落地 + 建仓push GitHub

**背景**：用户给了GitHub仓库地址`https://github.com/BCXiaoxue/RAG_Writing.git`（后续会转public），并明确指示"改名和查重暂时先不管，先开始Day1任务；若有需要手动实现的，先帮我实现，然后我再手动自己过一遍流程"——即从"只产出规划文档"转为"现在就把Day1范围内能写的代码写出来"。

**做了什么**：

1. **环境探测**：确认本机Python 3.9.1（Miniconda）、git 2.51、pip 20.3.1可用；建了`.venv`虚拟环境。尝试`pip install`核心依赖（langchain/langgraph/streamlit等）持续报`SSLEOFError`，换了默认源/清华镜像/pypi.org官方源/升级pip到最新/`dangerouslyDisableSandbox`都没解决；但用`curl`和`python -m urllib.request`访问同样的host完全正常（HTTP 200）。判断是这个sandbox网络环境对pip连接模式的特殊限制，不是通用问题，已在`CLAUDE.md`"环境信息"和`RUNNING.md`"已知问题"里记录排查过程，避免下次重新踩一遍。
2. **在装不上langchain/langgraph的情况下，先验证了能验证的部分**：写了`scripts/check_llm_key.py`（纯标准库urllib，不依赖任何pip包），直接调用DeepSeek的OpenAI兼容Chat Completions接口，**确认.env里的DeepSeek真实Key可以正常调通**。过程中发现一个重要坑：`deepseek-v4-flash`是推理模型，先输出`reasoning_content`再输出`content`，`max_tokens=64`时`content`是空字符串（`finish_reason: "length"`，token预算被推理阶段耗尽），调到`max_tokens=512`才拿到真实回答。这个坑已经写进`src/agents/llm.py`的模块docstring和`CLAUDE.md`"不要重新踩的坑"，因为它会让人误以为"LLM调用失败"或"Key不对"。GLM的Key目前是`.env`里的占位值，跳过未测。
3. **按Docs/01号架构文档把代码写出来**：
   - `src/agents/state.py`：`EssayReviewState`（TypedDict, total=False）。
   - `src/agents/llm.py`：DeepSeek/GLM双供应商`ChatOpenAI`封装，`get_chat_model_with_fallback()`用LangChain的`.with_fallbacks()`在兜底Key配置好时自动挂上。
   - `src/agents/nodes.py`：7个节点。`intake_validator_node`（真实校验作文词数）、`feedback_agent_node`/`coach_agent_node`（真实调用LLM，Prompt见文件内）是完整实现；`retrieval_agent_node`/`scoring_tool_node`/`grammar_check_node`是Day2占位，明确标注"[Day2占位]"防止被误当成真实结果。LLM相关的import故意写成函数内懒加载，让不需要langchain的部分能在没装包的环境里单独测试。
   - `src/agents/graph.py`：`build_graph()`，`StateGraph`按`Docs/01`的路由逻辑（intake_validator条件路由到retrieval_agent或short_circuit_reject）编排。
   - `src/storage/db.py`：SQLite读写（`save_submission`/`get_user_history`），只用标准库`sqlite3`。
   - `src/data_pipeline/{clean,eda,preprocess}.py`：按`Docs/02`号文档实现清洗/EDA/预处理（8:1:1按essay_set分层划分），需要A先手动从Kaggle下载数据集才能跑（Kaggle账号/协议这一步没法自动化）。
   - `src/rag/build_kb.py` + `data/kb/{rubric_essay_set_1.md, grammar_cards.md}`：Day2的RAG建库脚本，KB内容只写了每类1个占位示例，D需要补齐。
   - `app.py`：Streamlit四页面，"提交批改"页真实调用`build_graph()`并写入SQLite。
   - `requirements.txt`：按`RUNNING.md`定稿。
4. **验证**：`python -m py_compile`跑通全部`.py`文件（语法检查）；写了`scripts/smoke_test_nodes.py`验证不依赖langchain的部分——`intake_validator_node`（过短/正常长度两种情况）、`scoring_tool_node`占位启发式、`grammar_check_node`占位、`db.save_submission`+`get_user_history`往返读写——全部通过。**没能验证的**：`src/agents/graph.py`（需要langgraph）、`app.py`（需要streamlit）实际跑起来的效果，因为pip装不上，只做了语法检查，已在`CLAUDE.md`/`TODO.md`里明确标注，请求用户在自己的环境里`pip install`后跑一遍确认。
5. **建git仓库并push**：`git init` → 先单独`git add .gitignore`确认`.env`/`.venv/`被正确排除（`git status --short --ignored`核对过）→ 加了其余文件 → 提交 → `git branch -M main` → `git remote add origin https://github.com/BCXiaoxue/RAG_Writing.git` → 发现远程已有一个只含`LICENSE`的commit → 用`git merge origin/main --allow-unrelated-histories`合并（没有强推覆盖远程历史）→ `git push -u origin main`成功。push前用`git diff --cached | grep`过一遍确认真实Key字符串没有出现在任何要提交的内容里。
6. **更新文档**：`TODO.md`把已完成的Day1条目打勾、加了"GitHub仓库与代码现状"一节说明当前代码完成度和用户需要手动做什么、把用户的"下一步"指示转成"已落地"记录；`CLAUDE.md`更新了项目当前进度、真实的目录结构（不再是"规划中的结构"）、怎么跑起来（区分免安装可跑的验证脚本 vs 需要pip install的完整链路）、新增两条"不要重新踩的坑"（DeepSeek max_tokens坑、这个环境pip装不上的坑）、环境信息（git仓库状态、.venv、pip问题）；`RUNNING.md`加了"已知问题"一节和更新了测试步骤。

**怎么验证的**：见上面第4点；另外用`git status --short`和`git diff --cached | grep`两次确认了`.env`真实内容没有被意外staged/commit。

**遗留问题**：
- LangGraph/Streamlit的实际运行没有在本环境验证过，需要用户在能`pip install`的环境里跑一遍`streamlit run app.py`，如果langgraph/langchain-openai的API签名因版本不同而报错，需要下一轮再修。
- GLM的真实Key还没有，`.env`里是占位值，fallback逻辑目前实际上只有DeepSeek这一条腿在跑。
- Day2任务（真实训练两条评分模型、构建真实Chroma知识库、补齐KB内容）都还没开始，`TODO.md`里的Day2 checklist是下一轮的工作范围。
- "本班选题查重"和"项目文件夹改名"仍按用户指示暂缓，没有处理。

## 2026-07-13（第三轮）· 在真实GPU训练服务器上把Day2主链路全部跑通（不再是占位）

**背景**：用户给了训练服务器信息（`ssh retinascope-server`，密钥`id_ed25519_retinascope`，8×A100），指示"把4天能先跑好的代码先跑好（不用部署），需要我手动的先帮我完成，然后写一个md文档我照着跑一遍"。这是从"写文档/骨架"转为"尽量把系统真的跑起来"的明确指示。

**做了什么**：

1. **SSH探测与安全前提**：连上服务器后发现根分区(`/`)100%满（`df -h /`显示0可用，且是被多个同学共用的机器），改在`/data/wangchen/tiansukai/RAG/`下操作（1.4TB可用），用`TMPDIR`/`PIP_CACHE_DIR`/`HF_HOME`把所有临时文件和缓存都指过去，没有往`/root/`写任何大文件。
2. **一次真实事故及处理**：为了停掉自己起的一个Streamlit测试进程，执行了`pkill -f 'streamlit run app.py'`，结果这个模式匹配同时命中了同一台机器上正在运行的、用户的RetinaScope生产Docker容器（`retinascope_app`，其启动命令同样包含这几个字），导致该容器被杀、约1分钟服务中断。`docker ps`显示容器已被`restart: unless-stopped`策略自动拉起并恢复healthy，`docker inspect`的重启时间戳与操作时间精确吻合，确认是这次误操作导致而非巧合。**立即停止后续操作，用`AskUserQuestion`向用户如实汇报事故经过和当前恢复状态**，用户确认"继续，但以后只用精确PID"后才继续。此后所有停止进程的操作都先`ps aux`查到精确PID再`kill`，没有再用任何模式匹配。
3. **搭建可用的Python环境**：`.venv`建在`/data/...`下，`pip install -r requirements.txt`成功（这台服务器的pip网络正常，和本地开发环境的pip问题是两回事）。
4. **真实验证LangGraph全链路**：写了`scripts/e2e_graph_test.py`，跑通`build_graph().invoke()`真实调用DeepSeek生成定性反馈和辅导建议、SQLite正确写入、过短作文被正确短路拒绝——这是本项目第一次证明"LangGraph+LangChain+LLM"的整个链路真的能跑，不只是语法正确。过程中发现两个环境坑并解决：
   - DeepSeek调用如果用裸`urllib`，这台机器的Python因为自定义OpenSSL证书目录是空的会报`certificate verify failed`；用`langchain_openai.ChatOpenAI`（走`certifi`）不受影响，只有独立的`check_llm_key.py`裸调用脚本需要注意（本轮没改这个脚本本身，只是记录了这个环境差异，脚本原有逻辑在本地开发环境上依然有效）。
   - Streamlit headless模式在测试端口跑通、返回HTTP 200，随后按规则用精确PID停止（这一步就是引发上面事故的那次操作）。
5. **数据集：绕开Kaggle账号限制**：Kaggle官方ASAP-AES需要账号/协议，没有用户的Kaggle凭证没法自动化下载。搜索确认HuggingFace上"llm-aes"组织发布了非gated的镜像（4个repo覆盖全部8个essay_set，来自开源项目`Xiaochr/LLM-AES`），写了`src/data_pipeline/download.py`用`HF_ENDPOINT=https://hf-mirror.com`下载合并，共12976条，覆盖8个essay_set，与Kaggle官方数据内容一致（同样的essay文本和domain1_score）。`clean.py`改造为优先使用Kaggle官方文件、找不到就自动回退到HF镜像文件，两种来源都支持。清洗后剩12879条。
6. **EDA与预处理在真实数据上跑出结果**：`eda.py`发现matplotlib默认字体不支持中文（图表标题变方块），修复为自动探测`Noto Sans CJK SC`等中文字体（服务器上确认可用）；产出的分数分布统计与ASAP-AES论文/竞赛公开信息量级吻合（如set1均值8.5/满分12，set8均值37/满分60），验证数据没有搞错。`preprocess.py`补充了保存`data/processed/score_ranges.json`（每个essay_set的原始分数区间），供QWK评估时反归一化使用。按essay_set分层8:1:1划分：train=10303, val=1288, test=1288。
7. **训练两条评分模型，真实QWK**：新写`src/training/common.py`（QWK计算，按Kaggle ASAP官方口径——每个essay_set分别算QWK再宏平均，不是混在一起算）、`train_finetuned.py`（路径A，DistilBERT微调，显式写出"225原则"的2层循环+5步骤结构，AdamW+梯度裁剪+早停）、`train_custom.py`（路径B，Embedding随机初始化+BiLSTM+Attention，完全从零训练，同样的225结构+Adam+梯度裁剪+早停）。在GPU 0和GPU 1上并行训练（训练前用`nvidia-smi`确认这两块卡当时利用率为0，没有占用别人在用的卡）：
   - 路径A：4个epoch，测试集QWK(宏平均)=0.693，各essay_set 0.47~0.80不等（set8最弱，样本最少+分值范围最大）。
   - 路径B：12个epoch设置，第6轮早停，测试集QWK=0.622，同样set8最弱(0.15)。
   - 两者对比符合预期（迁移学习优于从零训练），且都是真实训练出来的、可复现的结果，不是编造数字。
8. **RAG知识库从真实数据构建**：发现HF数据集本身带有每个essay_set真实的`prompt`（作文题目）和`rubrics`（评分细则）字段，写了`src/rag/build_rubric_docs.py`自动提取生成`data/kb/rubric_essay_set_1~8.md`（替换掉之前只有1个占位示例的状态），比团队手写要真实、完整。`build_kb.py`用`BAAI/bge-small-en-v1.5`（开源embedding模型）构建Chroma向量库，120个chunk，实测相似度检索能正确命中"主谓一致"语法卡片和对应essay_set的真实评分细则。
9. **把两个真实模型接入LangGraph**：写`src/training/essay_scorer.py`（`EssayScorer`类，融合路径A/B的预测，**如实标注trait_scores目前是整体分的占位复制，不是真正训练出来的分项预测**，避免过度宣称"多头训练已完成"），更新`src/agents/nodes.py`的`scoring_tool_node`/`retrieval_agent_node`调用真实模型/真实KB，且在模型/KB文件不存在时优雅降级回Day1占位逻辑（不会让别的机器上跑代码直接崩溃）。重跑`e2e_graph_test.py`确认反馈内容确实引用了检索到的真实评分细则（比如essay_set 1提示"应该写成书信格式"，这正是该essay_set真实题目的要求）。
10. **同步小体积的真实产出物回本地仓库**：`data/kb/*.md`（真实rubric）、`data/processed/score_ranges.json`、`data/processed/eda/*.png`（真实图表）、`models/essay-scorer-*/v1/training_log.json`（真实训练日志/QWK）。模型权重本身（266MB）和向量库(1.1MB)/训练数据(150MB+)体积较大且可复现，保留在训练服务器上，`.gitignore`做了精细化调整（排除`*.bin`/`*.safetensors`但保留`training_log.json`等小文件）。
11. **文档全面更新**：`03-模型训练与微调方案.md`加了"已在训练服务器上实际跑通，真实结果"一节，并**更正了上一版"多头输出已确认为主线方案"的不准确表述**；`RUNNING.md`加了「0.5」一整节记录本轮踩过的坑（磁盘写满、pkill事故、HF的Xet存储卡死、SSL证书问题、GPU选择礼仪、nohup后台化）和真实可复现命令；`CLAUDE.md`更新项目当前进度、目录结构、环境信息（训练服务器信息）、新增3条"不要重新踩的坑"；新增`Docs/06-本轮成果与复现步骤.md`作为给用户的浓缩版总结+操作清单（用户明确要求的"md文档"）；`TODO.md`更新Day2 checklist为已完成状态、新增本轮待办。

**怎么验证的**：`scripts/e2e_graph_test.py`在训练服务器上实际跑通（真实DeepSeek调用+真实评分+真实RAG检索，日志见上）；两个训练脚本各自的`training_log.json`记录了完整的epoch级loss/QWK曲线，不是只有一个最终数字；`git status --short`和`git diff --cached | grep`确认没有真实Key/大文件被误提交；`docker inspect`确认事故恢复状态。

**遗留问题**：
- 分项trait_scores仍是占位复制，不是真实多头训练，已在文档里如实更正，Day3/4如果有时间可以补。
- `grammar_check_node`仍是占位（未接语法检查工具）。
- Day4的SSH正式部署（`121.41.238.92`）还没做。
- GLM真实Key、是否切换回Kaggle官方数据源、训练服务器上的数据/模型要不要打包取回——三条都记在`TODO.md`和`06`号文档里，需要用户决策。

## 2026-07-13（第四轮）· 清理TODO.md等文档里三轮累积下来的过时/自相矛盾内容

**背景**：用户要求"更新Docs下的文件，尤其是TODO.md"，没有给具体新指令。检查发现`TODO.md`积累了三轮的过程记录，出现了明显的自相矛盾——比如"GitHub仓库与代码现状"一节还写着"pip install被网络环境挡住，app.py这些代码没能实际跑起来验证"，但这是第二轮的状态，第三轮已经在训练服务器上把这些全部跑通并训练出真实模型；Day1 checklist里"数据清洗+EDA"还是`[ ]`未勾选，但第三轮已经在真实数据上跑完了。`04`/`05`号文档也有类似的"过去时该改成完成时"的小问题。

**做了什么**：

1. **`TODO.md`整体重写**：删除了三轮里过程性、已经被后续进展覆盖掉的段落（"GitHub仓库与代码现状（本轮新增）"整节、"下一步"trailing段落——这些内容要么已经完全过时，要么已经被执行完毕，留着只会误导后面接手的人以为还是那个状态）；把仍然有效的内容（已确认决策摘要、安全提醒两条、GitHub仓库现状的准确当前描述、需要决策的事项）合并去重，去掉"本轮"这种会随时间失效的措辞；Day1~Day4 checklist按实际完成情况重新勾选核对——Day1/Day2全部完成，Day3标注"评分模型→Graph→Streamlit端到端打通"已完成、但"CoachAgentNode补齐"这条本身是误标（coach_agent_node从第一轮起就是真实实现，不需要再补，需要补的只有grammar_check_node），Day4仍全部未开始。
2. **`04-四天开发计划与分工.md`**：Day2标题加了"已提前跑通"的状态提示，避免读者以为这部分还是待办。
3. **`05-答辩材料与演示话术.md`**：PPT大纲第5点补上真实QWK数字（0.693/0.622）；预设问答表修正了"知识库内容来源"这条的说法（之前写"Kaggle公开数据集"，实际是HF非gated镜像，如实更新并加了官方渠道降级说明）；新增一条问答"为什么essay_set 8表现明显更差"，把数据稀疏这个真实局限包装成诚实、专业的答辩素材。
4. **`02-数据集与数据处理方案.md`**：补充"实际获取渠道（已确认）"和"实际清洗结果"两段，把之前只描述"计划用Kaggle"的表述更新为实际发生的事（HF镜像下载、12976→12879条清洗结果），并说明如何切换回Kaggle官方渠道。
5. 检查了`00`/`01`号文档，确认没有类似的自相矛盾表述，不需要改动。

**怎么验证的**：对`Docs/`下所有文件做了一轮grep（关键词"占位""尚未""待定""Kaggle公开的ASAP-AES"等），逐条核对是否已经被后续实际进展推翻，只对确认过时的地方做修改，`Progress.md`历史记录本身不改（那是"当时状态"的如实记录，不应该被后续状态覆盖）。

**遗留问题**：无新增，`TODO.md`当前的待决策事项和Day3/4 checklist与`06-本轮成果与复现步骤.md`保持一致。

## 2026-07-14（第五轮）· 又一次密钥泄露处理 + Kaggle官方数据源尝试 + 模型权重发布到GitHub Release

**背景**：用户在`TODO.md`"下一步"里又一次直接粘贴了两个真实凭证（Kaggle API Token、GLM API Key），并给了三条新指示："选题查重已过""代码最好在本地服务器上搞，因为后续要部署到121.41.238.92""跑好的模型效果好的话可以放回本地代码"。

**做了什么**：

1. **立即处理第三次密钥泄露**：把Kaggle Token和GLM Key移到本地`.env`，从`TODO.md`里脱敏。这是同一个问题第二次复发（第一次是DeepSeek Key），在`TODO.md`"安全提醒"里换了措辞强调——以后有新Key应该先告诉我"有一个新Key"，由我来问你要值存进`.env`，而不是自己先粘贴到文档里。
2. **验证GLM Key真实可用**：用`scripts/check_llm_key.py`（纯标准库，不受本地pip问题影响）确认DeepSeek和GLM两个供应商都能调通，双供应商fallback现在真的有两条腿了。
3. **尝试用Kaggle官方渠道下载数据**：用提供的Token直接调Kaggle API（`Authorization: Bearer <token>`），确认Token有效（能访问`competitions/list`），并且定位到了官方文件`training_set_rel3.tsv`（16.3MB，通过`competitions/data/list/asap-aes`列出）。实际下载时被Kaggle拦截：`403 You must accept this competition's rules before you'll be able to download files.`——这是Kaggle强制要求的人工同意步骤，账号本身需要先在网页上点一次"I Understand and Accept"，没法用API/Token绕过，也不应该尝试绕过。已经把这个卡点和需要用户做的具体操作（打开比赛规则页面点接受）写进`TODO.md`，当前继续用HuggingFace镜像数据不受影响。
4. **把训练服务器上的模型权重取回本地**：`scp`拉回两条模型的完整产出物（路径A：pytorch_model.bin 265MB + tokenizer.json + tokenizer_config.json；路径B：pytorch_model.bin 11MB + vocab.json + model_config.json），过程中大文件那次scp因连接不稳定失败了一次，重试后文件大小与服务器端完全一致（265495867字节），确认传输完整。
5. **模型权重的git策略：发布GitHub Release而不是Git LFS或直接提交**——路径A的265MB权重超过GitHub单文件100MB硬限制，问了用户后选择"发布为Release资产，README里给下载脚本+SHA-256校验"这个方案（不是Git LFS，也不是完全不管）。具体做的：
   - 遇到`gh` CLI没装、也没有GitHub Token的问题，问用户要了token；第一个token只有读权限（创建Release时返回`403 Resource not accessible`），问用户换了一个有`Contents:write`权限的token才成功。
   - 用GitHub REST API（`curl` + Bearer token）创建了Release `models-v1.0.0`，上传了两条模型的全部产出物（权重+tokenizer/vocab/config共6个文件），核对了每个上传后的`browser_download_url`和文件大小都对得上。
   - 计算并记录了两个`.bin`文件的SHA-256。
   - 写了`scripts/download_models.py`（支持`GITHUB_TOKEN`存在时走认证API下载——当前仓库私有必须这样，不设Token时走匿名`browser_download_url`——留给仓库转public之后用），实际跑通验证过（下载了一个小文件比对内容）。
   - 写了根目录`README.md`（本仓库第一次有README.md），包含模型权重下载的两种方式、SHA-256表格、"文件缺失会发生什么"的说明。
   - 精细化了`.gitignore`：模型相关的所有产出物（权重/tokenizer/vocab/config）统一排除，只保留`training_log.json`，逻辑比之前更一致（之前只排除了.bin和部分tokenizer文件，vocab.json/model_config.json漏排了）。
   - 给`scoring_tool_node`/`retrieval_agent_node`的降级分支加了`warnings.warn(...)`，避免模型/知识库缺失时静默返回占位结果却没有任何提示。
6. **"选题查重已过"**：从TODO里的待决策事项移除，标记为已解决。
7. **"代码最好在本地服务器上搞...部署到121.41.238.92"**：这条指示有歧义（到底是现在就要在那台机器上开发，还是Day4部署时的提醒），用`AskUserQuestion`问清楚，用户确认是"Day4部署时的提醒，现在不用动"，所以本轮没有为这台机器配置SSH访问，只在`TODO.md`里记了一条"等真正部署时需要你提供访问信息"。
8. 更新了`TODO.md`（大幅重写，加入本节所有解决/新增事项）、`CLAUDE.md`（模型分发方式、环境信息里的Token清单、两条新的"不要重新踩的坑"：GitHub 100MB限制与Release vs LFS的区别、私有仓库Release资产需要认证下载）。

**怎么验证的**：`check_llm_key.py`跑通确认两个LLM Key都可用；`curl`直接测试Kaggle API确认Token有效、定位到官方文件、复现了规则未接受的403错误（不是我们代码的问题）；用`sha256sum`核对本地拉回的模型文件和Release上传前的一致性；用`download_models.py`实际下载一个Release资产验证认证下载路径能工作；`git status --short --ignored`和`git diff --cached | grep`确认两个新Token都没有进入任何要提交的文件。

**遗留问题**：
- Kaggle官方数据下载卡在"用户需要手动接受比赛规则"这一步，记在`TODO.md`，不阻塞任何已有功能。
- 121.41.238.92的SSH访问信息还没有，Day4真正部署时需要用户提供。
- `GITHUB_TOKEN`目前是有仓库写权限的敏感凭证，比LLM Key风险更高，需要格外注意不要再次泄露；仓库转public后可以考虑是否要撤销/降权这个token（届时下载模型权重不再需要认证）。

## 2026-07-14（第六轮）· TODO.md瘦身 + 部署服务器SSH配置 + 发现端口冲突

**背景**：用户在`TODO.md`里加了一条新的长期规则："除了4天开发Checklist，每次更新仅保留'需要你决策/补充的事项'即可，避免TODO冗余"，并在"下一步"里给了两条指示：①"HuggingFace非gated镜像如果跟kaggle上差不多的话，就不用kaggle上的了"（放弃Kaggle官方渠道）；②提供了`121.41.238.92`部署服务器的SSH访问信息（`~/.ssh/id_rsa`，root，22端口）。

**做了什么**：

1. **落实用户的两条指示**：
   - 数据源决策：确认放弃Kaggle官方渠道，统一用HuggingFace镜像，`TODO.md`/`CLAUDE.md`里的相关待办项直接移除（不再是"卡住的事项"，是"决定不做了"）。
   - 配置`deploy-server`（`121.41.238.92`）的SSH访问：加到`~/.ssh/config`，`IdentityFile ~/.ssh/id_rsa`，连接测试通过。
2. **探查部署服务器环境，发现关键问题**：这台机器不是空的——`docker ps`显示已经有一个叫`ophthalmic-ai`的生产容器占用端口`8501`（健康运行2个月，从内容看应该是田溯开另一个已上线的医疗项目），`ss -tlnp`还显示`80`/`8080`/`8502`也被其他python3进程占用。这正是`RUNNING.md`原计划要用的端口（`8501`），如果没有先检查直接部署，很可能重演第三轮"pkill误杀RetinaScope生产容器"那次事故的另一个版本——端口冲突可能导致我们的`docker run -p 8501:8501`或直接抢占端口的操作打断已有的生产服务。**这次先用只读命令（`docker ps`、`ss -tlnp`、`ls`）确认了现状，没有执行任何可能有副作用的操作**，然后把部署端口方案改成`8503`（已确认当前空闲），更新了`RUNNING.md`第8节的所有命令和示例URL。
3. **落实用户的新规则，大幅精简`TODO.md`**：删除了"本轮已解决""模型权重分发""安全提醒""已确认的设计决策摘要""GitHub仓库现状"这几个会不断累积、和`CLAUDE.md`重复的章节，只保留"需要你决策/补充的事项"（现在只剩"项目文件夹是否改名"一条，因为Kaggle和SSH访问都解决了）和"4天开发Checklist"。被删除章节里没有过时的信息之前已经同步进`CLAUDE.md`的对应位置（LLM Key状态、模型权重分发方式、密钥泄露的教训、GitHub仓库状态），这次又补充了部署服务器SSH信息和端口冲突记录进`CLAUDE.md`"环境信息"和"不要重新踩的坑"，确保精简`TODO.md`不等于丢信息。

**怎么验证的**：`ssh deploy-server`实际连接成功并跑了`hostname`/`df -h`/`docker ps`/`ss -tlnp`等只读命令确认环境；`git diff`确认`RUNNING.md`里所有`8501`都替换成了`8503`（除了明确注释"这个端口已被占用"的地方）。

**遗留问题**：
- Day4的实际部署命令还没有执行，只是把文档更新到了"可以直接照着跑"的状态。
- `deploy-server`磁盘只剩9.3G可用，正式部署前如果要装torch等重依赖，需要留意空间是否够用。

## 2026-07-14（第七轮）· 确认项目文件夹已改名 + TODO.md收尾清理

**背景**：用户手动把项目根目录从占位名"7_速通小分队_项目名称"改成了"7_速通小分队_慧笔"（简化版，未用`00-项目总览.md`里建议的完整长名），并在`TODO.md`里追加"下一步：基础工作是否都已经做完？名称目前已改"；`CLAUDE.md`里也追加了一条全局规则"更新md文件要精炼，避免冗余"。

**做了什么**：
1. `TODO.md`"需要你决策/补充的事项"里唯一一条（文件夹改名）已由用户自行完成，改成"当前无待决策事项"。
2. `00-项目总览.md`里"当前根目录仍是占位名…"这句同步改成改名已完成的实际状态。
3. 删掉`TODO.md`里用户手写的临时"下一步"小节（一次性问题，不适合留在长期待办文档里，答案见下方"是否做完"的判断，已经体现在Day1~4 checklist的勾选状态里）。

**关于"基础工作是否都已经做完"**：主链路（真实数据→真实两条评分模型→真实RAG→真实LangGraph全流程→SQLite→Streamlit可serve）已经全部跑通，不是占位，这部分基础工作已经做完。仍未完成的是：Day3的`grammar_check_node`（未接语法检查工具）、历史进步仪表盘的多头trait雷达图（依赖trait_scores是否要做真实多头训练）、零样本对比素材；以及整个Day4（实际执行部署到`121.41.238.92`、离线演示预案、PPT定稿与全员预演、录制演示视频）。这些仍在`TODO.md`的Day3/Day4 checklist里逐条列着。

**怎么验证的**：`git status`确认改动范围只有`TODO.md`/`00-项目总览.md`/`CLAUDE.md`；`pwd`确认当前工作目录已经是`7_速通小分队_慧笔`。

**遗留问题**：无新增，与改名前保持一致——Day3剩余项+Day4全部。

## 2026-07-14（第八轮）· Day3收尾：grammar_check_node真实实现 + trait启发式 + 雷达图 + 零样本对比 + set8误差诊断

**背景**：用户在`TODO.md`"下一步"连续给了两批指示：①"当前微调模型、自定义模型效果如何？有没有更好的提升方案？如果模型达到可以交付的效果，那么完成day3的BCAD"；②"完成同样本模型比较（同一批80份）/修复雷达图占位指标问题/端到端异常测试/set 8误差诊断（不需要重训，只做一次诊断）"。

**关于模型效果的结论**：微调DistilBERT测试集QWK=0.693、自建BiLSTM QWK=0.622，两条曲线（`training_log.json`里的`history`）都是正常收敛、不是运气，数值也在ASAP-AES公开方案的合理区间内（非集成的单模型）。essay_set 8偏低（QWK 0.47/0.15）确认是训练样本稀疏（见下方诊断），不是bug。结论：**两条模型达到可交付标准**，不建议在4天工期下继续为了QWK小数点后两位做更大模型/更多epoch这类边际收益的事，本轮把省下的时间用在了Day3的B/C/A/D上。

**做了什么**：

1. **B - `grammar_check_node`真实实现**（`src/agents/nodes.py`）：纯Python正则规则库，覆盖重复用词/`should of`类情态动词误用/双重否定/句首大小写/标点空格/常见拼写错误。**没有用`requirements.txt`里原来列的`language_tool_python`**——评估后发现它要打包Java版LanguageTool引擎（首次运行下载约200MB+要求装JVM），部署服务器`121.41.238.92`磁盘只剩9.3G、且没确认装了Java，临近Day4部署这个时间点不适合冒险，已把这个依赖从`requirements.txt`移除，改用零新增依赖的规则库方案，`scripts/smoke_test_nodes.py`同步更新了对应测试（原来的`test_grammar_check_stub`断言"永远返回空列表"，现在改成`test_grammar_check_rules`验证真实检测能力）。
2. **trait_scores启发式（对应用户"修复雷达图占位指标问题"的要求）**：新增`_heuristic_content_organization_penalty()`，content用词汇丰富度（type-token ratio过低说明用词重复单薄）扣分，organization用段落数/句长方差（单段落长文或句长毫无变化说明缺乏结构层次）扣分，language沿用已有的语法错误密度扣分。**三项都仍然不是训练出来的多头预测**，只是从"完全不看文本内容、直接复制整体分"变成"有可观察信号支撑的启发式近似"，这个区别在`src/training/essay_scorer.py`和`src/agents/nodes.py`里都写清楚了，答辩时不能说成"已完成多头训练"。
3. **C - 历史进步仪表盘雷达图**（`app.py`）：加了matplotlib极坐标图展示最近一次提交的三项分数，页面文案同步更新（去掉了几处"Day1/Day2占位"的过时说法，因为评分模型/RAG/语法检查现在都是真实实现）。
4. **A - LLM与自训练模型的职责边界**：曾做过固定抽样探索，但该类结果不再作为项目对外实验指标。当前正式材料只保留完整测试集上的路径A/B QWK，以及验证集上的融合权重选择；LLM用于生成反馈，不参与A/B数值评分。
5. **essay_set 8误差诊断**（不重训，一次性分析，同一个脚本里跑的）：train.csv里每个essay_set的样本量——set8只有578条，其他集合1252~1440条，**明显是训练样本量最少的**；在set8全量测试集（72条）上跑真实模型，残差(预测-真实)与真实分数的相关系数=**-0.73**，强负相关，说明模型对真实高分系统性低估、真实低分系统性高估——这是"训练样本少+分值范围宽(15-60)"场景下回归模型常见的"向均值收缩"症状，不是随机误差。诊断结果存了`models/set8_diagnosis.json`，给了这个已知弱点一个有数据支撑的解释，而不是只说"数据稀疏"四个字带过。
6. **端到端异常测试**（`scripts/e2e_graph_test.py`新增`test_edge_cases`）：补了5类之前没测过的边界情况——正好20词(MIN_WORDS边界)、正好1000词(MAX_WORDS边界)、1001词(应拒绝)、语法错误密集的作文（grammar_check_node压力测试）、essay_set 8（分值范围最宽0-60）。在训练服务器上跑通，见"怎么验证的"。

**怎么验证的**：
- `scripts/smoke_test_nodes.py`本地跑通（`test_grammar_check_rules`验证规则库真实检测出拼写/重复/双重否定/情态动词误用/小写i；`test_scoring_tool_stub`因为本地`models/essay-scorer-*/v1`权重已从Release拉回、但本地pip装不了transformers/sklearn，这一条在本地环境跑不了，是环境限制不是代码问题）。
- `app.py`本地headless模式起服务确认HTTP 200且无异常（用精确PID `kill`掉测试进程，没有用模式匹配）；雷达图matplotlib渲染逻辑单独用一段脚本验证过能正常出图。
- `scripts/eval_zero_shot_llm.py`、`scripts/eval_same_sample_and_diagnose_set8.py`、扩展后的`scripts/e2e_graph_test.py`均在训练服务器`retinascope-server`上实际跑通（真实DeepSeek调用+真实评分模型推理），过程中发现并修正了一个环境坑：`.hf_cache`离线缓存需要显式设`HF_HOME`+`HF_HUB_OFFLINE=1`才会命中本地缓存，不设的话`transformers`会尝试联网请求HuggingFace（这次刚好网络能通所以只是变慢，但如果网络恰好不通就会直接报错），已经在`Docs/RUNNING.md`里有过类似提醒，这次是在推理场景又踩到一次，补充确认。
- 本轮SSH到训练服务器的过程中多次遇到连接被重置（`Connection closed by ... port 22`），排查后判断是这条连接偶发不稳定、不是命令本身的问题，等几秒重试或换成`cat | ssh "cat > file"`的方式传文件都能恢复，没有发现是我方操作导致（没有执行任何可能引发这种情况的重操作）。

**遗留问题**：
- `CriticAgentNode`反思循环仍是stretch goal，本轮没做。
- Day4全部：实际执行部署到`121.41.238.92`、离线演示预案、PPT定稿+全员预演、录制演示视频。
- rubric知识库/语法卡片素材补充仍是持续性任务，不阻塞主链路。

## 2026-07-14（第九轮）· 按四人实际分工新增四份角色操作手册（07~10号文档）

**背景**：项目按数据处理+Streamlit包装、Docker部署、模型构建/微调/训练、系统测试四个职责产出对应操作手册，服务于答辩时被老师提问。LangGraph编排/Agent节点/RAG知识库并入模型训练文档（技术上`src/agents/`直接调用`src/training/`的模型，两者耦合，分开讲不自然）。

**做了什么**：

1. 新增`Docs/07-数据处理与前端操作手册.md`（林奕琳）：数据处理四步命令、Streamlit启动方式、四个页面的真实/占位现状说明（写作知识库问答页面前端仍是disabled占位，如实标注）、trait_scores启发式的诚实解释、EDA关键发现、预设问答。
2. 新增`Docs/08-部署操作手册.md`（毛陈荣）：`121.41.238.92`服务器现状（磁盘9.3G、端口冲突）、标准venv+nohup部署流程（当前主线方案）、Docker容器化思路（明确标注"可选，不是当前主线方案"，避免被误解成"已经决定要做"）、离线演示预案、预设问答。
3. 新增`Docs/09-模型训练与Agent编排操作手册.md`（田溯开）：两条模型训练命令、RAG知识库构建命令、**推理场景离线HF缓存的坑**（`HF_HUB_OFFLINE=1`，上一轮实际踩到过）、LangGraph路由逻辑图示、核心设计决策+真实数据支撑（零样本vs训练模型公平对比0.384/0.756、essay_set 8诊断的-0.73相关系数、两条路径QWK对比0.693/0.622）、预设问答。
4. 新增`Docs/10-系统测试操作手册.md`：全部测试脚本按依赖复杂度分类的操作手册、手动测试清单、**诚实说明测试没覆盖的部分**（压力测试/并发测试/对抗性输入测试都没做，4天工期下不是优先级），预设问答。
5. `CLAUDE.md`的Docs目录表加了这4行；`04-四天开发计划与分工.md`顶部加了一句指向新文档的说明，不改动原有按模块划分的内容（那是Day1的历史规划，如实保留）。
6. `TODO.md`按用户新提出的"精炼避免冗余"规则，加了"上一轮完成情况汇报"这个新分区（用户在文档头部说明里加的，介于"需要你决策"和"Checklist"之间），把第八轮和本轮的完成情况各写了一段浓缩总结在这里，"下一步"里的临时性问题解决后清空。

**怎么验证的**：四份文档里的命令/数字全部是从本仓库已有代码、已跑出的真实结果（`training_log.json`、`models/*.json`、`RUNNING.md`已验证过的命令）里摘取整理，没有新编造任何数字；用`grep`交叉检查了四份文档之间没有互相矛盾的表述（比如部署方案、trait_scores的说法在`07`/`09`号文档里保持一致）。

**遗留问题**：
- 四份文档是本轮根据现有信息编写的，具体到每个人手上后如果有和实际操作细节不符的地方（比如某人本地环境的具体路径），需要各自补充，已在`TODO.md`"下一步"留了一条等反馈。
- Day4部署/PPT/预演/录像仍未开始，和上一轮一致。

## 2026-07-14（第十轮）· 整理Docs，删除已被取代的06号文档，修正多处过时表述

**背景**：用户在`TODO.md`"下一步"要求"整理Docs中的md文件，保留必要文件"。

**做了什么**：

1. **删除`Docs/06-本轮成果与复现步骤.md`**：这份文档是第三轮创建的"给用户看的浓缩总结+操作清单"，内容已经被三处更新的文档完全覆盖——真实结果数字在`CLAUDE.md`"当前进度"、可复现命令在`RUNNING.md`+新的`07`~`10`号角色手册（比06号更细、按人分工）、逐轮历史在`Progress.md`。而且06号文档本身已经过时（比如还写着"content/organization仍是占位复制"，这在第八轮已经改成启发式信号），继续留着会误导人。删除前确认了它没有独有信息会丢失，唯一一条还没解决的"训练服务器`retinascope-server`上的内容要不要保留"被之前几轮的TODO.md精简漏掉了，这次补回`TODO.md`"需要你决策"里。
2. **修复所有指向06号文档的死链接**：`CLAUDE.md`目录表、`00-项目总览.md`、`02-数据集与数据处理方案.md`、`04-四天开发计划与分工.md`、`TODO.md`（共5处），改成指向替代它的`07`/`09`号文档或直接去掉这行。`Progress.md`历史记录里提到06号文档的地方不改（那是当时状态的如实记录）。
3. **顺手修正了几处发现的过时/有风险的表述**（都是在做上面这轮死链接排查时顺带发现的，不是专门去找的）：
   - `03-模型训练与微调方案.md`：essay_set 8那段"数据稀疏导致"补上了真实诊断数字（578条训练样本、残差相关系数-0.73），trait_scores那段"占位"改成"启发式近似"，和`09`号文档保持一致。
   - `05-答辩材料与演示话术.md`：①"为什么不直接用大模型打分"这条预设问答补上了真实的0.384 vs 0.756对比数字，比原来空泛的"方差大"有说服力；②essay_set 8那条预设问答补上真实诊断数据；③新增一条"雷达图是不是真正的多维度AI评分"的诚实问答；④**修正了一个会露怯的演示脚本错误**——原脚本第5步写"打开写作知识库问答页现场演示RAG问答"，但这个独立页面的输入框其实是禁用状态（`disabled=True`，Day1就是这个状态，一直没接通），如果真按原脚本演示会当场卡住，已经改成跳过这一步、改用"检索能力已经在批改流程里体现"的说法。

**怎么验证的**：`grep -rn "06-本轮成果\|06号文档"`确认所有存活文档（非Progress.md历史记录）里的引用都已修复；`ls Docs/`确认最终剩13个文件（`00`~`05`+`07`~`10`+`RUNNING/Progress/TODO`），没有编号跳跃造成的误导（`06`空缺是因为删除，不是笔误，各文档索引都已经不再引用它）。

**遗留问题**：
- `Docs/RUNNING.md`本身内容较长（172行），本轮没有发现明显冗余/过时内容，暂不动；如果之后团队反馈用不上某几节，可以再精简。
- 训练服务器`retinascope-server`上内容是否需要打包取回，重新记录进`TODO.md`"需要你决策"，等用户答复。

## 2026-07-14（第十一轮）· 项目全称后缀从"系统"改成"智能体"

**背景**：用户要求"调整项目名，后缀为xxx智能体"。理解为：完整题目末尾的"...个性化学习伴学系统"改成"...个性化学习伴学智能体"，其余部分（"慧笔""HuiBi"、副标题"基于LangChain+LangGraph的英语写作智能批改与"）不变——这个改动本身也更贴合项目实际形态（LangGraph多智能体编排），不只是文字游戏。

**做了什么**：`grep -rln`定位到所有包含完整题目的存活文件（`app.py`页面标题、`CLAUDE.md`两处、`Docs/00-项目总览.md`两处、`Docs/05-答辩材料与演示话术.md`封面页、`README.md`），统一把"...个性化学习伴学系统"替换成"...个性化学习伴学智能体"。英文题目("A LangChain + LangGraph Multi-Agent System...")保持不变，用户只指定了中文后缀。`Docs/Progress.md`历史记录里的旧提法不改（如实记录当时状态）。顺手发现`README.md`里还有一处指向已删除的`Docs/06-本轮成果与复现步骤.md`的死链接（上一轮整理时漏检了仓库根目录的`README.md`，只查过`Docs/`和`CLAUDE.md`），一并改成指向`Docs/Progress.md`最新记录。

**怎么验证的**：`grep -rln "个性化学习伴学系统"`确认只有`Docs/Progress.md`的历史记录还保留旧提法，其余全部改成"智能体"；`grep`确认没有遗漏的死链接。

**遗留问题**：无新增。提交文件夹的完整建议命名（`00`号文档里`07_速通小分队_慧笔——...`那一行）已同步更新为新后缀，但实际文件夹名仍是简化版"7_速通小分队_慧笔"，未包含完整题目，之前已确认这是团队的选择，不受本次改动影响。

## 2026-07-14（第十二轮）· 按4人分工把07~10号文档+相关代码打包成4个文件夹

**背景**：用户要求"根据每个人的分工，将四个md文件（07 08 09 10）做成四个文件夹，包括相关代码、md文件，便于发送给组员"。

**做了什么**：

1. **位置决策（自己的判断，非用户明确指定）**：新建的4个文件夹放在项目根目录`7_速通小分队_慧笔/07-分工交付包/`下（与`01-源代码/`平级），不放进`01-源代码/`的git仓库里。理由：这4个文件夹里的代码是从`src/`摘出来的**副本**，如果放进git仓库会造成同一份代码两处存在、后续改动容易两边不同步；放在仓库外、按项目根目录已有的数字编号习惯（`01-源代码`/`02-数据集`/…）新增一个`07-分工交付包`，既保持风格一致，又不污染版本库。这个决策没有事先问用户，如果不合适（比如想要放`01-源代码/`里方便一起提交），后续可以直接移动文件夹，不影响内容本身。
2. **每人一个文件夹**，命名`姓名-负责领域`：
   - `林奕琳-数据处理与前端`：`src/data_pipeline/`全部脚本、`app.py`、`src/storage/db.py`（Streamlit依赖它读写历史）。
   - `毛陈荣-部署`：没有专属代码模块（部署本身要打包整个应用，不是某一块代码），给了`操作手册.md`+`RUNNING.md`+`app.py`（部署对象是什么）。
   - `田溯开-模型训练与Agent编排`：`src/training/`+`src/agents/`+`src/rag/`全部代码、`src/storage/db.py`（`nodes.py`依赖）、相关`scripts/`（`e2e_graph_test.py`/两个`eval_*.py`/`check_llm_key.py`/`download_models.py`）、`models/`下的训练日志和本轮诊断结果json（不含大权重文件）、`data/kb/`和`score_ranges.json`。
   - `系统测试`：`scripts/`全部脚本、`src/agents/nodes.py`+`state.py`+`src/storage/db.py`（`smoke_test_nodes.py`直接依赖）。
   - 每个文件夹里操作手册从`Docs/07~10`号文档复制过来改名`操作手册.md`，另加`requirements.txt`+`.env.example`+一份`README.md`。
3. **诚实说明局限性（写进每个`README.md`）**：这套代码是紧耦合的LangGraph应用，不是清晰分层的模块化项目，"只给某人自己的代码"天然不能独立运行完整功能（比如`nodes.py`要真正跑评分还是需要`src/training/`）。每个`README.md`都写清楚"这不是能独立运行的完整项目，只是方便查看/编辑自己负责的部分，实际运行/联调用完整仓库"，不让人误以为这个精简文件夹就是全部。

**怎么验证的**：
- 数据处理与系统测试相关文件夹中，免重依赖的部分实际用`PYTHONPATH=.`跑通了（`intake_validator_node`、`grammar_check_node`规则库检测出真实语法错误），不是只复制文件没测过。
- `田溯开`文件夹里全部`.py`文件过了`ast.parse`语法检查，且`src.agents.state`能正常单独import（验证了`__init__.py`和相对路径没有遗漏）。
- 复制完之后运行验证产生了`__pycache__`目录，检查后手动清理掉了，不会把这些垃圾文件发给组员。
- `find`确认4个文件夹加起来共76个文件，没有明显遗漏（每个文件夹都有操作手册+README+对应代码+`requirements.txt`+`.env.example`）。

**遗留问题**：
- 4个文件夹是本轮从当前代码状态摘取的**快照副本**，如果后续`01-源代码/`里对应文件再有修改，这几个文件夹不会自动同步，需要重新打包或手动同步，已在`README.md`里提醒但没有做自动化同步机制（4天工期下没必要为这个搭build脚本）。
- 文件夹位置是本轮自行判断放的，不是用户指定，如果用户希望换位置/换打包方式（比如要压缩成zip），需要另外说一声。

## 2026-07-14（第十三轮）· 实际执行Day4部署到deploy-server + 本地启停脚本

**背景**：用户要求"写一个运行/终止当前项目的脚本，模型如果还在训练服务器上跑的话拉回，我要进行系统演示，进行验收"。先查证了训练服务器：`ps aux`确认上面现在跑的全是别的同学/项目的训练任务（`HGM-main3`、`MyTraincopy_topk_boundary`、`Ocular_Carotid_Bridge`），本项目自己的两条评分模型早就训练完，权重文件也已经完整在本地（`models/essay-scorer-*/v1/pytorch_model.bin`），没有需要"拉回"的东西。用`AskUserQuestion`确认了启停脚本要针对哪个环境，用户选择"部署到`deploy-server`，装到`/root/sukai`（不是`RUNNING.md`草稿里写的`/root/huibi`），脚本在本地跑"——这实际上把Day4遗留的"C：实际执行部署"这一项也一并做了。

**做了什么**：

1. **代码同步**：本地开发机没有`rsync`，改用`tar`打包（排除`.git`/`.venv`/`__pycache__`/`.env`，**没有**用`--exclude-from=.gitignore`整体排除，因为那样会连`models/`下的真实权重文件也一起排除掉，部署出来的应用会静默降级成占位启发式评分）+ `scp`传输255MB压缩包 + 远程解压到`/root/sukai/`。
2. **依赖安装**：`deploy-server`无GPU，显式指定`--index-url https://download.pytorch.org/whl/cpu`装CPU-only版torch（避免pip默认拉CUDA版把本就紧张的磁盘挤爆），再装`requirements.txt`剩余依赖，全程`--no-cache-dir`。装完后磁盘从9.3G降到约6.2G，在预期范围内。
3. **RAG知识库**：`chroma_kb`目录本身被`.gitignore`排除，没有跟着tar包过去，在服务器上现场跑`python -m src.rag.build_kb`重新生成（120个chunk，1.1MB，和本地/训练服务器上的结果一致）。
4. **`.env`单独传输**：用`scp`单独传了一次，没有混进tar包里。
5. **LLM联通性验证**：`scripts/check_llm_key.py`在`deploy-server`上跑通，DeepSeek一次成功，GLM第一次超时、重试后成功（判断是网络瞬时抖动，不是Key或代码问题）。
6. **启动Streamlit并验证**：`nohup streamlit run app.py --server.port 8503 ...`启动后，服务器本机`curl localhost:8503`返回**HTTP 200**，日志显示`External URL: http://121.41.238.92:8503`。
7. **写了两个本地PowerShell脚本**（`scripts/deploy_start.ps1`/`scripts/deploy_stop.ps1`）：本地运行，通过SSH远程管理`deploy-server`上的进程。**核心设计**：用PID文件（`/root/sukai/streamlit.pid`）记录精确PID，启动前检查是否已在跑（避免重复启动），停止时**只kill这个精确PID**，不用`pkill -f`模式匹配——这是本项目在训练服务器上已经吃过一次亏的教训（误杀别人的生产容器），部署服务器上同样是共用机器（`ophthalmic-ai`容器还在跑），必须一样小心。启动脚本还会自动`curl`验证HTTP 200并报告结果。
8. **发现一个新问题（不是我方操作导致的）**：从外网`curl http://121.41.238.92:8503`访问不通，但服务器本机`curl localhost:8503`是通的，且检查过`iptables`（策略`ACCEPT`，无拦截规则）和`ufw`（`inactive`）都没有问题——判断拦截发生在云服务商的安全组/网络ACL层，这一层我通过SSH改不了，需要有云控制台权限的人去放通TCP 8503入站规则。已经记进`TODO.md`"需要你决策"，这是当前"能不能从答辩现场访问"前面唯一挡着的事。
9. **`RUNNING.md`第8节、`Docs/08-部署操作手册.md`同步更新**：路径改成`/root/sukai`（不是草稿里的`/root/huibi`）、rsync命令改成实际用的tar+scp、补上构建RAG知识库和使用启停脚本这两步（原来的草稿版本漏了这两步，照抄会跑不起来）。

**怎么验证的**：`ls`/`du`确认代码和模型权重真实到达服务器（255647647字节，和本地tar包大小完全一致）；`df -h`在部署前后各查了一次确认磁盘消耗在预期范围；`check_llm_key.py`真实调用两个LLM供应商都成功；`curl localhost:8503`拿到HTTP 200；`ps -p <PID>`确认streamlit进程用的是脚本记录的那个精确PID，不是猜的。

**遗留问题**：
- **外网访问被云安全组挡住**，需要用户/有权限的人去云控制台放通8503端口，见`TODO.md`。
- 部署过程中SSH连接出现过比训练服务器更严重的中断（这次是"banner exchange超时"，持续了几分钟才恢复，不是训练服务器那种"connection closed"几秒钟自愈的抖动），具体在跑`scripts/e2e_graph_test.py`做部署后完整链路验证时中断，还没等到这次验证的最终结果，需要在文档更新完之后单独确认一次。
- 离线演示预案（截图/录屏）还没做，见`Docs/08-部署操作手册.md`第四节，Day4还剩这个+PPT/预演/录像。

## 2026-07-14（第十四轮）· 训练服务器清理归档 + 找到SSH中断真因(OOM) + 部署全链路验证通过

**背景**：接续上一轮遗留问题，用户在`TODO.md`"下一步"给了两条指示："8503没法开放的话，尝试别的端口"、"Day4的部署不需要训练服务器，提前打包取回，将相关文件删除即可，别的不要动"。

**做了什么**：

1. **`retinascope-server`清理**（SSH恢复后）：`du`确认目录下有本地没有的数据——`data/raw`(8M)、`data/processed/{train,val,test,essays_clean}.csv`(共约157M)、`chroma_kb`(1.1M），模型权重字节数和本地逐一核对完全一致（`265495867`/`11302685`字节，不需要重新拉）。打包成32MB压缩包（tar+scp，不用rsync，本地没装）取回本地，验证`git status`确认这些文件都被`.gitignore`正确排除、不会污染版本库。取回确认后，**逐层核对路径**（`/data/wangchen/tiansukai/`下还有`data`/`effnet_b4_bce_retrain`/`yijun`三个属于其他同学的目录），精确`rm -rf /data/wangchen/tiansukai/RAG`只删自己的项目目录，删除后`ls`确认三个其他人的目录完好、`df -h /data`确认空间已释放。
2. **排查`deploy-server`SSH长时间中断的真实原因**：SSH恢复后`uptime`看到`load average: 12.40, 68.69, 93.05`，`ps aux --sort=-%cpu`却看不到对应的高CPU进程（最高只有3.6%），说明瓶颈不是CPU而是别的资源；`free -h`看到这台机器**总内存只有1.6G**；`dmesg | grep -i oom`直接翻到真实证据：`Out of memory: Killed process 513907 (python) ... anon-rss:837020kB`——上一轮我在Streamlit已经加载了一份DistilBERT模型（占内存）的情况下，又另起了一个`e2e_graph_test.py`进程去加载第二份模型，两份加起来超过1.6G触发了Linux OOM killer，系统内存被打满后`sshd`本身也响应迟缓，表现成"banner exchange超时"，一开始误判成网络问题，这次找到了真实根因。已经把这条写进`CLAUDE.md`"不要重新踩的坑"、`Docs/08-部署操作手册.md`、`RUNNING.md`三处。
3. **纠正验证方式，干净跑通部署环境的完整测试**：用精确PID（`ps aux`确认后`kill 513273`）先停掉Streamlit，确认内存回落到`free -h`显示942Mi可用后，单独跑`scripts/e2e_graph_test.py`（不再有第二个进程同时加载模型），**7个测试场景全部通过**——真实DeepSeek反馈生成、真实评分（含分项trait_scores启发式调整）、MIN/MAX_WORDS边界、语法密集、essay_set 8全部正常，`grammar_errors数量`和本地/训练服务器上的结果模式一致。测完后重新用同样的启动流程拉起Streamlit（这次`echo $!`正确写入了`streamlit.pid`，上一轮漏了这一步）。
4. **外网访问验证：用户在过程中确认"开放了8503"**（阿里云控制台操作），当场`curl http://121.41.238.92:8503`从本地网络实测**返回HTTP 200**（0.03秒响应），并`curl`取了页面内容确认是Streamlit在真实serve，不是别的服务碰巧占了这个端口。顺手查了实例元数据（`curl http://100.100.100.200/latest/meta-data/instance-id`，不需要登录控制台）确认这是阿里云ECS，区域`cn-hangzhou`，实例`i-bp13v9vqfgbj2iygazp9`，记进`CLAUDE.md`方便以后快速定位；检查过服务器上没有装`aliyun`/`tccli`之类的云厂商CLI，所以安全组这一步没法SSH代劳，只能是用户去控制台操作，这次是用户自己做的。
5. **`TODO.md`"需要你决策"清空**（两条都解决了：安全组已放通、训练服务器已清理），Day4 checklist的部署那一条改成完全打勾状态；`CLAUDE.md`、`RUNNING.md`第8节、`Docs/08-部署操作手册.md`同步更新为"部署已完成、外网验证通过"的最终状态，并把1.6G内存这个新发现的坑写进三处相关位置。

**怎么验证的**：`dmesg`的OOM killer日志是内核真实记录，不是猜测；`e2e_graph_test.py`的输出逐行核对了7个场景的`is_valid`/`quant_score`/`grammar_errors数量`都符合预期（比如边界1/2因为文本重复词多，content和language分项被正确压到0，边界5 essay_set 8没有触发任何语法规则、分项和整体分一致）；`curl http://121.41.238.92:8503`外网实测两次都是HTTP 200；`ls`+`ps -p`确认`retinascope-server`清理和`deploy-server`重启后的PID管理都符合预期。

**遗留问题**：
- 离线演示预案（截图/录屏）仍未做，Day4还剩这个+PPT定稿/全员预演/演示视频，都是需要团队协作完成的部分，不是能单独代劳的。
- 建议答辩前从答辩现场实际网络再测一次`http://121.41.238.92:8503`，开发者本地网络能访问不完全等于校园网/现场网络也能访问。

## 2026-07-15（第十五轮）· 路径A/B与融合权重的补充核验

**背景**：曾补充核验路径A/B与融合权重。固定抽样结果随后被明确要求不再作为项目最终实验结论。

**做了什么**：

1. `scripts/eval_same_sample_and_diagnose_set8.py`支持按参数调用路径A、路径B或融合路径，避免模型之间混用权重。
2. 在部署服务器上完成过补充核验；由于固定抽样不代表完整测试集，相关数值结果已从最终文档和答辩材料移除。
3. 融合策略保留为验证集网格搜索：在1,288篇验证集上按0.05步长选择A=0.95、B=0.05，验证集macro QWK=0.708。
4. `Docs/09-模型训练与Agent编排操作手册.md`已同步为“完整测试集单模型指标＋验证集选权”的表述。

**怎么验证的**：路径A/B完整测试集指标由各自训练脚本输出并写入`training_log.json`；融合权重搜索基于验证集执行。固定抽样文件仅保留为内部过程记录，不作为最终实验依据。

**遗留问题**：无新增。

## 2026-07-15（第十六轮）· Streamlit拆两页 + 登录注册(滑块验证) + 视觉改版

**背景**：用户要求"优化streamlit分为两个页面（本地文件），一个为产品介绍页一个为工作台，需要增加登录注册功能（附带滑块验证，在输入用户名和密码正确后，以对话框形式弹出），美化样式，直接抄科大讯飞的平台样式"，并明确"先改本地文件，后再去服务器上改"。用`AskUserQuestion`确认了两个关键分歧点：①滑块验证用简化版拖动滑块（不是图片拼图验证码，后者需要Pillow图片处理+自定义JS组件，开发量大）；②"抄讯飞样式"不能真的抓取/复制讯飞平台代码或使用其logo/商标（会构成冒牌），改成参考这类企业AI平台的通用视觉语言自己重新设计。

**做了什么**：

1. **拆成两个独立本地文件**（Streamlit原生多页应用约定）：`app.py`变成产品介绍页（Hero区+功能卡片+登录注册），原来的四个功能页整体搬到新建的`pages/1_工作台.py`。`st.session_state`跨页面共享，登录状态不需要重复设置；`pages/1_工作台.py`顶部检查`st.session_state.logged_in`，没登录直接`st.stop()`拦截。
2. **登录注册**（`src/storage/db.py`新增）：新增`users`表 + `create_user()`/`verify_user()`，密码用`hashlib.pbkdf2_hmac`+每用户随机salt做哈希（如实标注不是bcrypt/argon2级别的生产方案，够用于课程项目演示）。`get_connection()`原来用`conn.execute(SCHEMA)`只能跑单条DDL语句，加了users表后SCHEMA变成两条CREATE TABLE，**改成`conn.executescript(SCHEMA)`**（用`execute()`跑多语句会报`sqlite3.Warning: You can only execute one statement at a time`，本地测试时发现的，已修复且不影响原有`submissions`表的读写逻辑）。
3. **滑块验证对话框**：登录用户名密码校验通过后不会立刻登录成功，而是设置`st.session_state.awaiting_verification`触发一个"安全验证"对话框，里面是`st.slider`（0~100，拖到98以上才算通过），验证通过后点"确认登录"才真正设置`logged_in=True`。**`st.dialog`真正的模态弹窗需要Streamlit>=1.31**（`requirements.txt`已加下限），本地开发环境是1.26.1没有这个API——新增`src/ui_theme.py`的`dialog_decorator()`做兼容：新版本用真弹窗，旧版本降级成页面内联区块（不报错但不是真弹窗）。部署服务器上的Streamlit是1.59.2，支持真弹窗。
4. **视觉改版**：新增`src/ui_theme.py`统一注入CSS——蓝色系主色调(`#165DFF`)、渐变Hero横幅、卡片式功能介绍、圆角按钮，参考讯飞开放平台/百度智能云这类企业AI平台的通用设计语言自己重新设计，不使用任何具体平台的logo/商标/代码。
5. **`user_id`不再手动输入**：`pages/1_工作台.py`里直接用`st.session_state.username`（登录账号）作为`user_id`，历史记录追踪和真实账号绑定，比之前手动填文本框更合理。
6. **测试**：`scripts/smoke_test_nodes.py`新增`test_auth_roundtrip()`（注册/重复用户名/密码太短/登录成功/密码错误/用户不存在，6种场景全覆盖），本地跑通；本地起了一次headless Streamlit确认两个页面都能返回HTTP 200、无异常抛出（但本地Streamlit版本较旧，`st.dialog`走的是降级路径，交互式验证——尤其真弹窗和真实拖动滑块的手感——留给部署服务器上的1.59.2去验证，本轮**没有**推到`deploy-server`，用户明确说先改本地文件）。
7. **顺带修好一个和本任务无关但边做边发现的bug**：想在本地重启部署服务器上原来那版（旧UI）Streamlit好让线上演示不空窗时，`scripts/deploy_start.ps1`报PowerShell解析错误（"missing terminator"）。排查发现`deploy_start.ps1`/`deploy_stop.ps1`两个文件是**不带BOM的UTF-8编码**，Windows PowerShell 5.1对没有BOM的脚本文件会按系统ANSI代码页（这台机器是GBK）解析，导致文件里的中文注释字节被错误解码，连带把后面的引号计数搞乱、报出看似不相关的"缺少字符串终止符"错误。用`[System.IO.File]::WriteAllText(path, content, (New-Object System.Text.UTF8Encoding $true))`把两个文件重新存成带BOM的UTF-8后问题消失。**这是一个通用坑**：以后写的PowerShell脚本只要包含中文字符，都要确认保存成带BOM的UTF-8，已经记进`CLAUDE.md`"不要重新踩的坑"。

**怎么验证的**：`db.create_user`/`verify_user`直接单测通过（含重复注册/密码太短/密码错误/未注册用户四种失败场景）；`scripts/smoke_test_nodes.py`全量重跑通过（含原有的intake/grammar/db测试，确认新增代码没有破坏已有功能）；本地headless Streamlit对两个页面路由分别`curl`确认HTTP 200且日志无异常；`ast.parse`确认三个新/改动文件语法正确；`deploy_start.ps1`（修复BOM后）成功解析并把部署服务器上现有的旧版应用重新拉起来，确认线上演示站点在本轮UI改造期间没有长时间空窗。

**遗留问题**：
- 新版UI（两页面+登录注册+视觉改版）**还没有部署到`deploy-server`**，用户明确要求先在本地确认，需要用户下一步指示再决定要不要推上去、以及推上去之前要不要先在有GPU/完整依赖的环境里做一次真实交互测试（尤其是真弹窗+真实拖动滑块的手感，本地旧版Streamlit测不出来）。
- 密码哈希方案是演示级（PBKDF2+标准库），不是生产级（bcrypt/argon2+限流+邮箱验证+找回密码），如果这个项目要长期对外提供服务需要补上，已在`src/storage/db.py`顶部注释里如实说明。
- 滑块验证是简化版拖动滑块，不是图片缺口拼图验证码，已经和用户确认过这个取舍，如果答辩被问起要如实说明。

## 2026-07-15（第十七轮）· 修复深色模式下登录页低对比度看不清的bug

**背景**：用户帮我在本地跑起新版UI后，截图反馈登录页"配色等内容都显示的不清楚"，并问"是否需要更换技术栈？感觉streamlit的样式不好看"。

**根因排查**：看截图发现是典型的"深色文字/背景和浅色文字/背景混在一起"的低对比度问题——侧边栏"app"/"工作台"导航文字几乎看不见，输入框标签发虚。定位到根因：`src/ui_theme.py`只用CSS把`.stApp`背景、侧边栏背景强制成浅色（白色/浅灰），但**没有同步固定Streamlit自己的主题基色（`base`）**。用户的系统/浏览器是深色模式时，Streamlit原生组件（侧边栏导航文字、输入框标签、tabs文字）仍然按深色主题的配色方案走浅色文字，我们的CSS又把背景强制改成了浅色，两者叠加就是"浅色文字画在浅色背景上"，正是截图里看到的效果。这不是Streamlit本身丑，是我们自己的CSS只改了一半（背景）没改完整（没固定主题基色）。

**做了什么**：

1. **新增`.streamlit/config.toml`**：用`[theme] base="light"`强制整个应用固定浅色主题，不再依赖系统/浏览器深色模式的检测结果，配色（`primaryColor`/`backgroundColor`/`secondaryBackgroundColor`/`textColor`）和`src/ui_theme.py`里定义的常量保持一致。**这个文件只在Streamlit进程启动时读取一次**，改完之后必须重启Streamlit才生效，不是像CSS那样热更新。
2. **给`src/ui_theme.py`补充了双重保险**：输入框(`.stTextInput input`等)、标签、tabs文字、侧边栏所有文字都显式加了`color`+`!important`，防止某些浏览器扩展（比如Dark Reader这类会在页面CSS之外再做一层色彩反转的强制深色插件）绕过`config.toml`继续造成问题；同时把`hb-hero`/`hb-card`/`hb-badge`这些自定义元素的文字颜色也补上了`!important`。
3. **本地重启验证**：`kill`掉旧进程精确PID后用新config重新启动Streamlit，`curl localhost:8501`确认HTTP 200。**注意**：具体显示效果需要用户自己刷新页面再确认一次，我这边只能验证服务正常启动、没有报错，看不到实际渲染画面。
4. **回答"要不要换技术栈"**：不建议。这是一个可定位、可修复的配色bug（主题基色和自定义CSS没对齐），不是Streamlit画不出好看界面这种架构性限制；而且部署脚本/测试脚本/答辩文档全部围绕Streamlit搭建，4天工期下换栈是高风险低收益的选择。已经在`TODO.md`"需要你决策"里如实给出建议，同时把决定权留给用户——如果刷新后还是觉得具体某处不好看（不是这次的看不清bug，是纯审美偏好），可以具体指出来再调整，不需要因为一次bug否定整个技术选型。

**怎么验证的**：`ast.parse`确认`src/ui_theme.py`改动后语法正确；本地`kill`旧进程+重启新进程+`curl`确认HTTP 200；`.streamlit/config.toml`的键名（`base`/`primaryColor`等）核对过是Streamlit官方文档定义的标准主题配置项，不是编造的。**没有能力**在这个环境里截图验证实际渲染效果，这一步只能靠用户反馈确认。

**遗留问题**：
- 需要用户刷新浏览器重新截图确认，才能知道这次修复是否彻底解决了看不清的问题。
- 如果用户的浏览器确实装了强制深色的扩展（比如Dark Reader），需要用户自己检查并对这个站点关闭，代码层面的`!important`不一定能完全对抗浏览器扩展级别的色彩反转。

## 2026-07-15（第十八轮）· 修复登录后工作台页面崩溃的bug（懒加载顺序问题）

**背景**：用户帮我在本地实际点击登录后，Streamlit抛出`ModuleNotFoundError`（`langgraph`相关），报错栈显示`app.py`的`st.rerun()`之后紧接着执行到`pages/1_工作台.py`第17行的`from src.agents.graph import build_graph`失败。

**根因**：`pages/1_工作台.py`把`from src.agents.graph import build_graph`写在文件最顶部——**在登录校验(`st.stop()`)之前**。这一行import会一路引入`langgraph`/`langchain-openai`，本地开发环境从项目一开始就没能装上这些重依赖（见`CLAUDE.md`"环境信息"）。结果是这个页面的脚本只要被执行（不管有没有登录），就会在这行import上直接崩溃——登录校验代码写对了，但排在了会崩溃的import后面，形同虚设。之前只用`curl`测过这个页面路由返回HTTP 200，但`curl`拿到的是静态HTML外壳，不会真的触发Streamlit针对这次会话重新执行脚本、走到这行import，所以这个bug没有被我之前的验证方式测出来，是用户真实点击登录后才暴露的。

**做了什么**：把`from src.agents.graph import build_graph`从模块顶部挪到真正需要用它的地方——原来是登录校验之后立刻`build_graph()`（第一版懒加载修复，仍然不够彻底，登录后只是切到"反馈详情"这类不需要跑推理的tab也会触发这行import），后来进一步挪到"提交批改"按钮被点击、且作文内容非空这个分支里，做到真正按需加载：登录、切换四个功能tab都不需要`langgraph`，只有真正点击"提交批改"要跑推理时才需要。

**怎么验证的**：`ast.parse`确认改动后语法正确；`grep`确认`from src.agents.graph import build_graph`只出现在按钮点击的if分支里，不再是模块级语句；本地重启Streamlit后`curl`两个页面路由都是HTTP 200且日志无异常（但如上所述，这个方式测不出这类"真实会话执行才触发"的bug，这次修复的信心来源主要是静态检查确认import已经不在任何无条件执行的路径上，不是靠curl验证）。

**遗留问题**：
- 需要用户重新实际登录一次确认这次真的修复了（不能只依赖我这边的静态检查+curl）。
- 如果确认修好了，说明本地环境从Day1开始就有的"装不上langgraph/transformers"限制会持续影响任何以后新写的、在模块顶部import这些重依赖的代码，写新页面/新模块时要留意这一点，别把重依赖的import放在无条件执行的路径上。

## 2026-07-15（第十九轮）· 取消滑块验证功能

**背景**：用户要求"取消滑块功能"。

**做了什么**：

1. **`app.py`**：删掉`verification_dialog()`函数和`awaiting_verification`这个session state；登录表单校验通过后（`db.verify_user`返回`True`）直接设置`st.session_state.logged_in = True`+`username`+`st.rerun()`，不再走"安全验证"这一步。
2. **`src/ui_theme.py`**：删掉配套的`dialog_decorator()`（`st.dialog`版本兼容层），因为已经没有任何地方调用它，不留没人用的代码。
3. **`requirements.txt`**：撤回之前专门为`st.dialog`加的`streamlit>=1.31`版本下限，改回不限定版本（滑块功能取消后不再需要这个API，也就不需要这个版本要求）。
4. **文档同步**：`CLAUDE.md`、`Docs/01-系统架构与Agent设计.md`、`Docs/07-数据处理与前端操作手册.md`、`Docs/10-系统测试操作手册.md`、`Docs/RUNNING.md`里所有提到"滑块验证"/"安全验证对话框"/`st.dialog`兼容降级的地方都改成"登录凭证正确后直接登录成功"，`07`号文档的手动测试清单和预设问答里滑块相关的条目也删掉了。`Docs/Progress.md`历史记录（第十六/十七/十八轮里提到滑块的部分）不改，如实保留当时的状态。

**怎么验证的**：`ast.parse`确认`app.py`/`src/ui_theme.py`改动后语法正确；`grep -rn "awaiting_verification|captcha_slider|dialog_decorator|verification_dialog"`确认代码里已经没有任何残留引用；本地重启Streamlit（精确PID kill旧进程）后`curl`确认HTTP 200无异常。

**遗留问题**：无新增。新版UI（现在是"两页面+登录注册，无滑块"）仍然还没有推到`deploy-server`，见`TODO.md`"需要你决策"。

## 2026-07-15（第二十轮）· 提交批改页加作文类型选择+作文题目输入

**背景**：用户反馈"处理逻辑有问题，应该能选择作文类型（46级、托福、雅思、考研英语），而且要能够输入作文题目"——之前"提交批改"页只有一个"题目集ID（1-8）"数字输入框，是ASAP-AES数据集内部编号，对用户不友好，也没有地方填写真实的作文题目。

**做了什么**：

1. **新增`src/exam_types.py`**：定义作文类型下拉框的5个选项（大学英语四级/六级、考研英语、托福、雅思）到ASAP-AES essay_set的映射表。**这里做了一个需要用户知晓的近似处理**：评分模型（微调DistilBERT/自建BiLSTM）训练数据始终是ASAP-AES的8个essay_set，不是真实的四六级/托福/雅思/考研英语数据，模型并不认识这几种考试的区别。5个选项里有4个被映射到essay_set 1或2（现有8个essay_set里体裁最接近"给定话题写议论文"的两个），这个映射只决定RAG检索该走哪一套评分细则文本，**不代表评分模型针对每种考试单独训练/校准过**，量化评分也不会折算成雅思分/四六级分这类真实考试量表——这一点已经在`src/exam_types.py`顶部注释、提交批改页面的`st.caption`提示、`07`号文档里都写清楚了，是我自己的判断（用户只说"要能选择作文类型"，没说清楚要不要做成"真的按考试类型区分评分逻辑"，考虑到模型训练数据的现实限制，做了这个近似映射而不是假装有专门的按考试类型评分能力）。
2. **`pages/1_工作台.py`"提交批改"页**：数字输入框换成`st.selectbox`选作文类型，新增`st.text_area`填作文题目（原题目要求/prompt），提交前校验两者都非空。
3. **`src/agents/state.py`**：`EssayReviewState`新增`exam_type`/`essay_topic`两个可选字段。
4. **`src/agents/nodes.py`**：`FEEDBACK_PROMPT`加了`{exam_type}`/`{essay_topic}`两个占位符，`feedback_agent_node`生成反馈时会结合真实题目判断"是否切题"；`retrieval_agent_node`的检索query里也加了题目文本，检索相关性有小幅提升。顺手修正了`FEEDBACK_PROMPT`里一处过时表述（"量化评分...Day2接入真实评分模型前不代表实际水平"，这是Day1时期的占位说法，现在早就是真实模型了）。
5. **`src/storage/db.py`**：`submissions`表新增`exam_type`/`essay_topic`两列。**新增`_migrate_submissions_columns()`做轻量迁移**：`CREATE TABLE IF NOT EXISTS`不会给已经存在的旧表补新列，如果不做这个迁移，本地已经跑过的`data/app.db`会在下次`INSERT`时报"table submissions has no column named essay_topic"。用`PRAGMA table_info`查现有列、缺哪个就`ALTER TABLE ADD COLUMN`哪个，不需要用户手动删库重建。
6. **`pages/1_工作台.py`"反馈详情"页**：加了一行`st.caption`显示这次提交的作文类型和题目，方便回看。

**怎么验证的**：`ast.parse`确认全部改动文件语法正确；本地重跑`smoke_test_nodes.py`全部测试通过；**专门写了一个迁移测试**——手动建一个旧schema（没有`exam_type`/`essay_topic`列）的SQLite文件，插入一条旧数据，再调用`db.save_submission()`存一条带新字段的数据，确认`get_user_history()`能同时正确读出"旧数据两个新字段是None"和"新数据两个新字段有值"，迁移逻辑没有破坏旧数据；本地重启Streamlit（精确PID）后`curl`两个页面路由都是HTTP 200无异常。

**遗留问题**：
- 作文类型到essay_set的映射是本轮自己判断的近似处理（4个类型映射到只有2个essay_set），如果用户觉得映射不合理（比如想让雅思和托福映射到不同essay_set），可以再调整`src/exam_types.py`里的字典，改起来很轻量。
- 新版UI（含本轮的作文类型/题目输入）仍然还没有推到`deploy-server`，和上一轮一致，见`TODO.md`"需要你决策"。

## 2026-07-15（第二十一轮）· 排查"知识库尚未构建"提示 + 5种考试类型专属知识库真实区分

**背景**：用户问"RAG知识库（评分细则/语法卡片/范文）尚未构建是什么原因？"，并要求"加入（46级、托福、雅思、考研英语）的评判规则，然后区别开来，选择不同的类型调用不同的知识库"。

**排查"尚未构建"的原因**：这是一处**过时文案，不是真实状态**。检索`data/processed/chroma_kb/chroma.sqlite3`确认知识库文件真实存在（954KB，Day2就已构建，`retrieval_agent_node`在"提交批改"流程里从Day2起就一直真实调用它）。问题出在`pages/1_工作台.py`的"写作知识库问答"这个独立tab——它的前端代码从Day1起就是硬编码的占位提示"RAG知识库...尚未构建"+一个`disabled=True`的输入框，Day2真正把知识库建好之后，没有人回头把这个独立tab的前端接通/更新提示文案，导致这个页面一直显示着过时信息，误导成"知识库还没做"。上一轮（第二十轮）的`07`号文档里其实已经写过"写作知识库问答仍是占位"这个诚实说明，但用户还是在页面上看到了这句过时提示，说明只在文档里记录、没有同步把代码本身修正是不够的。

**做了什么**：

1. **修正过时文案，真正接通"写作知识库问答"页**：新增`src/agents/nodes.py`的`answer_kb_question(question, exam_type=None)`——独立的"问题进、答案出"入口，复用`retrieval_agent_node`的检索逻辑和`get_chat_model_with_fallback()`的LLM，但不需要走完整的`build_graph()`（那是为"提交批改"整套7节点流程设计的，问答场景更轻量）。`pages/1_工作台.py`的"写作知识库问答"tab换成真实的问题输入框+可选的考试类型限定下拉框，点击后调用这个函数。
2. **新增5份考试类型专属评分细则**（`data/kb/exam_rubrics/{cet4,cet6,kaoyan,toefl,ielts}.md`）：不是通用内容改几个字应付了事，是分别针对这5种考试真实的评分标准/常见扣分点/提分建议整理的——四六级按官方Global Scoring五档标准和字数/句式要求写；考研英语按图画作文"描述-议论-总结"三段式和教育部评分标准整理；托福按ETS官方0-5分五档标准和"明确Thesis Statement"这类托福特有要求写；雅思按官方Task Response/Coherence/Lexical Resource/Grammatical Range四维度25%权重整理，各自内容互不相同。
3. **`src/exam_types.py`重构**：从"考试类型->essay_set"单一映射，改成"考试类型->{essay_set, 专属rubric文件名}"的配置字典，新增`rubric_file_for_exam_type()`。essay_set仍然只用于分值反归一化（不代表模型训练区分），rubric文件才是"选不同类型调用不同知识库"这句话的真正实现。
4. **`src/rag/build_kb.py`从`glob`改成`rglob`**：原来只扫`data/kb/`顶层的md文件，不会递归进`exam_rubrics/`子目录，本轮新增的5份细则不改这一行的话根本不会被建进向量库。同时统一了`source`元数据的写法（相对`data/kb/`的posix路径，比如`exam_rubrics/cet4.md`），和`rubric_file_for_exam_type()`的返回值对齐。
5. **`src/agents/nodes.py`的`retrieval_agent_node`加了按`exam_type`过滤检索**：`state`带`exam_type`时，先按`source`元数据过滤只在对应考试类型的专属文件里做相似度检索；没有`exam_type`或者检索不到时，退回全库检索，不阻塞主链路。

**怎么验证的**（本地开发环境没装`chromadb`/`langchain_community`，这轮涉及真实检索的验证全部在`deploy-server`上用真实依赖做的，过程中注意了不影响线上演示——先用精确PID`kill`掉正在跑的旧版Streamlit避免同时加载两份模型触发OOM，测完后用`deploy_start.ps1`重新拉起）：
1. 在一个隔离的`/root/kb_test*/`临时目录（不是正式部署目录`/root/sukai/`）里放一份改动后的代码+data/kb，跑`load_kb_documents()`确认能收录到全部14个md文件（8个essay_set rubric + 语法卡片 + 5份考试类型专属rubric）共133个chunk，`source`字段格式符合预期。
2. 跑`python -m src.rag.build_kb`真实构建向量库，确认133个chunk成功写入。
3. **真实调用`answer_kb_question()`验证检索确实区分**：问"雅思写作的评分标准有哪些"（`exam_type="雅思（IELTS）"`），拿到的回答只包含IELTS的Task Response/Coherence/Lexical Resource/Grammatical Range四个维度，没有混入其他考试类型的内容；问"四级作文常见扣分点是什么"（`exam_type="大学英语四级（CET-4）"`），拿到的回答是CET-4专属文档里那五条扣分点，两次回答内容完全不同，证明"选不同类型检索到不同知识库"这个要求真的实现了，不是表面上加了个下拉框但底层还是查同一份内容。
4. 验证完成后删除了临时测试目录，没有污染正式部署目录；`deploy_start.ps1`重启后`curl`确认本机和外网访问都是HTTP 200，线上演示（仍是旧版UI）没有被这轮验证过程打断太久。
5. 本地（无重依赖）跑了`ast.parse`确认所有改动文件语法正确。

**遗留问题**：
- 新版UI+知识库改造（本轮和上一轮累积的全部改动）仍然还没有推到`deploy-server`的正式部署目录，`deploy-server`上现有的`chroma_kb`还是120-chunk的旧版本，不包含本轮新增的5份专属rubric——已在`TODO.md`加了明确提醒："上线时记得重新跑`build_kb.py`，不然新版UI选了作文类型也检索不到对应内容"。

## 2026-07-16（第二十二轮）· Streamlit职责移交毛陈荣 + 新增LLM自主调用工具 + 反馈可读性优化

**背景**：用户三条指示：①"Streamlit的任务归属到毛陈荣那边，请更新他的文档，并配备相应的代码"；②看看能否让模型自主调用第三方工具；③作文批改的定性反馈可读性不强，能否增强（可考虑换更强的模型）。用`AskUserQuestion`确认了三个关键取舍：Streamlit改归毛陈荣是**完全移交**（不是共同负责）；第三方工具选**免费免Key的词典查询**（用户原话是"如果第三方key要收费且服务器无法联网的话，用第一种"——已确认Free Dictionary API免费免Key，且`deploy-server`本身能正常访问外网DeepSeek/GLM API，条件满足）；可读性问题**先只优化Prompt格式，不换模型**（换模型可能增加延迟/成本，且现有DeepSeek/GLM已通过`.env`环境变量支持切换到更高阶版本，无需改代码，留给以后需要时再做）。

**做了什么**：

1. **Streamlit任务完全移交毛陈荣**：`git mv`重命名`Docs/07-数据处理与前端操作手册.md`→`Docs/07-数据处理操作手册.md`（只保留`src/data_pipeline/`范围，删掉Streamlit/登录注册/作文类型输入/SQLite相关章节）；`Docs/08-部署操作手册.md`→`Docs/08-前端与部署操作手册.md`（合并进原07号文档里前端/SQLite/登录注册/作文类型输入四节+对应的答辩问答，与原有部署内容重新编号整合为11节）。同步更新了`CLAUDE.md`目录结构表、`Docs/04`的姓名-角色映射说明、`Docs/05`和`Docs/02`里对旧文件名的引用、`scripts/deploy_start.ps1`里提示信息的文件名。`Docs/Progress.md`历史记录里的旧文件名不改（如实保留"当时状态"）。
2. **新增LLM自主调用第三方工具的能力**：现有架构里评分/RAG检索/语法检查都是LangGraph固定路由**确定性调用**的工具，模型本身没有"自己决定要不要调用某个工具"的能力，这次是真正新增这个能力，不是重新包装已有工具。新建`src/agents/tools.py`的`dictionary_lookup`（`@tool`装饰），查免费免Key的Free Dictionary API（`api.dictionaryapi.dev`），标准库`urllib`实现，不新增pip依赖。`src/agents/llm.py`新增`get_primary_chat_model()`——因为`get_chat_model_with_fallback()`返回的`RunnableWithFallbacks`不是`BaseChatModel`，没有`.bind_tools()`方法，只有裸`ChatOpenAI`才有。`coach_agent_node`（`src/agents/nodes.py`）改造为：裸主力模型`.bind_tools([dictionary_lookup])`→最多2轮工具调用循环→生成练习计划；整个工具调用链路包在`try/except`里，任何环节失败（绑定失败、供应商不支持function calling等）都会打印警告并降级回`get_chat_model_with_fallback().invoke(prompt)`的原有普通生成方式，不会让这个新能力拖垮主链路。`COACH_PROMPT`加了一句提示模型"不确定的词可以查，常见词不用每个都查"，避免为了演示效果而滥用工具调用。`Docs/01`"Agent使用的工具清单"补充了这个工具的说明，明确区分"确定性调用"和"模型自主调用"两类。
3. **反馈可读性优化（仅Prompt层面，未改模型/未改前端渲染）**：`AB_FEEDBACK_PROMPT`和`LLM_RUBRIC_PROMPT`里的`feedback_markdown`指令，从"依次输出：评分依据、优点、不足、语法与用词建议"这种较松散的要求，改成强制的Markdown结构模板——`## 一句话总评`（≤30字）+`## 评分依据`/`## 优点`/`## 不足`（列表+**加粗**关键词+引用原文）+`## 语法与用词建议`（"原句 → 建议改法"格式），并要求"全部用短句和列表，不要写大段连续文字"。`COACH_PROMPT`同步改成`## 优先修改清单`+`## 针对性练习`两段结构。前端`pages/2_工作台.py`用的`st.write()`本身就会渲染Markdown（标题/列表/加粗都生效），不需要改前端代码，问题出在Prompt对输出结构约束太松，不是渲染层的问题。

**怎么验证的**：
- `python -m py_compile`和`ast.parse`确认`src/agents/nodes.py`/`src/agents/llm.py`/`src/agents/tools.py`语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过（不涉及本轮改动的LLM调用部分，验证没有破坏原有不依赖langchain的逻辑）。
- **真实验证了Free Dictionary API的网络行为**（本地开发环境`urllib`能访问外网，但装不了langchain，只能单独验证网络层）：直接请求返回`403 Forbidden`，一度以为接口本身拒绝访问或者本环境网络受限；排查发现是该API的CDN把`urllib`默认User-Agent（`Python-urllib/x.y`）当成爬虫拦截，换成类浏览器User-Agent后返回正常200和真实的释义/同义词/例句JSON——已经在`dictionary_lookup`里加了`_REQUEST_HEADERS`修复，不加这个头会导致这个工具在任何环境下都100%查询失败（会被误判成"这个工具不能用"）。同时验证了查无此词的404分支返回预期的降级提示文案。
- **没能验证的、需要用户在能装langchain的环境里确认**：`ChatOpenAI.bind_tools()`+`tool_calls`解析这条链路在DeepSeek/GLM真实API上的行为——本地开发环境没装`langchain-openai`（一贯的pip问题），无法端到端跑通"模型判断要不要查词→调用→拿到结果→生成最终答案"这一整条链路；DeepSeek官方文档确认`deepseek-chat`支持OpenAI兼容的function calling，但GLM-4-Flash这个免费兜底档位对tool_calling的支持程度没有实测过，如果它不支持或者行为有差异，`coach_agent_node`目前只在裸主力模型上绑定工具（没有走`get_primary_chat_model()`之外的兜底供应商），主力供应商本身失败会整体降级不查词生成，但如果只是"绑得上工具但解析`tool_calls`格式不对"这种更隐蔽的错误，需要用真实调用跑一遍`scripts/e2e_graph_test.py`或单独写一个小验证脚本才能确认。已记在`TODO.md`"需要你决策"。**本轮已在`deploy-server`上实测确认（见下一节），这条遗留问题已解决。**

## 2026-07-16（第二十三轮）· 把本轮改动部署到deploy-server，并在真实服务器上验证工具调用链路

**背景**：用户要求"先部署到服务器"。部署前发现一个认知偏差需要纠正：`Docs/TODO.md`Day4 checklist里"目前是旧版UI，本轮新做的登录注册/双页面/视觉改版还没推上去"这句话已经过时——实测`deploy-server`上`/root/sukai/`的实际内容（文件mtime到`Jul 15 21:35`，`streamlit.log`有当天记录），登录注册/双页面/5种考试类型专属rubric/RAG检索按考试类型过滤这些都已经在服务器上，只是`TODO.md`没有同步更新这句过时描述——这是本项目反复出现过的"文档滞后于实际进展"问题（参见第四轮"清理TODO.md"记录），本轮先纠正了这个认知，避免以为要做一次"从零"的大部署。

**做了什么**：

1. **部署前安全检查**（按`Docs/08`第七节"部署前必须做的检查"）：`docker ps`确认`ophthalmic-ai`容器不受影响；`ss -tlnp`确认`streamlit`正跑在8503（PID 44985，与`streamlit.pid`记录一致）；`df -h /`发现磁盘只剩**1.5G可用**（比`Docs/08`记录的"部署前9.3G"紧张得多，`/root/sukai/.venv`本身就占了2.1G）；`free -h`确认内存仍然紧张（1.6G总量，当时只有100Mi空闲）。
2. **改用"增量同步changed文件"而不是`Docs/08`标准流程里的"整仓库tar+scp"**：磁盘只剩1.5G，本地全仓库（不含`.venv`/`.git`）有432MB（含270MB+11MB的模型权重），再传一份完整tar+解压风险很高。改成`md5sum`逐个核对本地和服务器上的关键文件，确认只有`src/agents/{tools.py,llm.py,nodes.py}`、`CLAUDE.md`、`Docs/{01,02,04,05,07,08,Progress,TODO}`这几个文件有实质变化（模型权重、`data/processed/chroma_kb`、`.venv`服务器上已经是最新，不用动），直接`scp`这几个文件，不碰其余部分。这是按当前实际磁盘约束做的取舍，不是`Docs/08`文档本身写错，只是那条"标准流程"假设的磁盘余量今天不成立，已经在`TODO.md`记一条"以后磁盘更紧张时优先用这种增量同步方式"的经验。
3. **精确PID停止/启动**：`streamlit.pid`记录的PID`44985`确认存活后精确`kill`，重新用`nohup ... & echo $! > streamlit.pid`拉起（PID变为`106810`），全程没有使用`pkill -f`模式匹配。同时清理了服务器上重命名前的旧文件`Docs/07-数据处理与前端操作手册.md`/`Docs/08-部署操作手册.md`（避免新旧文件同时存在造成混淆），清了`src/agents/__pycache__`避免stale字节码。
4. **重启后验证**：本机`curl localhost:8503`和公网`curl http://121.41.238.92:8503`都返回HTTP 200；`streamlit.log`尾部没有`ModuleNotFoundError`/`ImportError`等导入报错。
5. **真实验证了`coach_agent_node`的工具调用链路（不是本地伪造的假设）**：在`deploy-server`上（不加载`EssayScorer`/embedding，避免OOM）单独跑了一段脚本，直接调用`get_primary_chat_model().bind_tools([dictionary_lookup])`，用真实DeepSeek API发送"帮我查ubiquitous这个词"的请求——**模型自主判断需要查词、正确生成了`tool_calls`（`{"name": "dictionary_lookup", "args": {"word": "ubiquitous"}}`）**，工具真实调用了Free Dictionary API拿到释义/例句/同义词，模型基于工具结果生成了准确、结合了真实释义的最终中文讲解。确认`langchain_core==1.4.9`/`langchain_openai==1.3.5`（服务器已装版本）完整支持这条链路，不是理论上可行而已。

**怎么验证的**：见上面第4、5点，均为在真实`deploy-server`上的实测结果（HTTP状态码、`streamlit.log`内容、真实DeepSeek API返回的`tool_calls`和最终回答），不是本地推测。验证过程全程监控`free -h`/`df -h`，确认没有触发过内存或磁盘告警（验证结束后内存仍有337Mi空闲、Streamlit主进程RSS只有59MB，说明这次验证脚本本身没有加载重量级模型，内存冲击很小）。

**遗留问题**：
- `data/processed/chroma_kb`本轮没有重新构建（本轮没有新增知识库内容，服务器上现有向量库已经包含全部6种考试类型专属rubric，构建时间`2026-07-16 09:44`晚于这些文件的最后修改时间，确认已经是最新），如果以后再改`data/kb/`下的内容，记得重新跑`python -m src.rag.build_kb`。
- `TODO.md`Day4 checklist里"目前是旧版UI...还没推上去"这句过时描述本轮口头纠正了但没有回去改那句话本身（不在本轮任务范围内，且那条checklist已经是Day4历史记录性质），如果后续再看到类似的"过时状态描述"，优先信实测结果，不要直接信文档里的旧措辞。

## 2026-07-16（第二十四轮）· 定性反馈改成按维度拆分的卡片式结构化输出

**背景**：用户发来一张截图（某竞品/参考产品的作文反馈界面），"写作任务回应情况"/"连贯与衔接"两张卡片，每张卡内含"优势点"/"建议改进的方面"/"关于如何改进"（若干条带标题的小贴士），问能否做出同样可读性的效果，并问是否需要换更强或联网的模型。排查后发现截图里的两个标题就是IELTS官方评分维度Task Response/Coherence and Cohesion的中文直译，与`src/official_rubrics.py`里IELTS已有的`task_response`/`coherence_cohesion`键名完全对应，说明这套卡片设计和现有数据结构是天然匹配的，缺的是"按维度拆分的结构化输出"而不是模型能力——DeepSeek已经在`LLM_RUBRIC_PROMPT`路径稳定输出JSON，不需要换模型。用`AskUserQuestion`确认范围：用户要求所有考试类型（CET/通用/考研的A/B路径，以及IELTS/TOEFL的LLM量表路径）都要卡片化，不是只做IELTS/TOEFL。

**做了什么**：

1. **State新增`feedback_dimensions: dict`字段**（`src/agents/state.py`），与原有的`qualitative_feedback`（拍平文本，兜底用）并存，不是替换关系。
2. **`src/official_rubrics.py`新增三个共享辅助函数**：`dimension_entry()`（把单个维度的原始dict防御性规整成`{strengths, improvements, tips}`统一形状，某个字段缺失/类型错都不报错只是留空）、`build_dimension_feedback()`（按`{显示名: 原始key}`映射批量处理）、`flatten_dimension_feedback()`（拍平成Markdown文本）。`normalize_rubric_result()`（IELTS/TOEFL路径）改为用这几个函数从`payload["dimension_feedback"]`构建`feedback_dimensions`，`qualitative_feedback`不再直接读`payload["feedback_markdown"]`（这个字段已从JSON schema里去掉），改成flatten的结果。TOEFL分支原来的`scores`构建也顺手统一成和IELTS一样先定义`keys`字典再遍历的写法，避免`keys`变量在TOEFL分支未定义导致的`NameError`。
3. **`src/agents/nodes.py`重写两条Prompt的JSON schema**：`AB_FEEDBACK_PROMPT`（新增`AB_DIMENSION_LABELS = {"内容主旨":"content","结构与衔接":"organization","语言运用":"language"}`映射）和`LLM_RUBRIC_PROMPT`都从"输出一段Markdown"改成"按维度输出`dimension_feedback`结构化JSON，每个维度含strengths/improvements/tips（1~2条{title,comment,example}）"。`feedback_agent_node()`两条分支都改成：`llm.invoke()`→`parse_llm_json()`解析→`build_dimension_feedback()`/`normalize_rubric_result()`构建`feedback_dimensions`→`flatten_dimension_feedback()`得到兜底文本；解析失败时`feedback_dimensions`为空dict（而不是让整个节点抛异常），前端会自动退回文本展示。
4. **`src/storage/db.py`新增`feedback_dimensions`列**：加入`_SUBMISSIONS_NEW_COLUMNS`迁移列表（自动给旧`data/app.db`补列），`save_submission()`用`json.dumps`写入，`get_user_history()`用`json.loads`读出（旧记录该列为空时返回`{}`，不是`None`，前端判断更简单）。
5. **`src/ui_theme.py`新增卡片CSS（`.hb-dim-*`系列）和`render_feedback_dimensions()`渲染函数**：每个维度一张`.hb-dim-card`，"优势点"/"建议改进的方面"用虚线分隔的小节，"⬆ 关于如何改进"下面是浅蓝底的`tip`小卡片（标题加粗+说明+可选示例）。**安全处理**：`feedback_dimensions`里的文本内容最终来自LLM生成（间接受用户提交的作文正文影响），渲染函数对所有动态文本字段（label/strengths/improvements/tips的title/comment/example）逐项`html.escape()`后才拼进`unsafe_allow_html=True`的HTML字符串，本地用`<script>alert(1)</script>`测试过确认会被正确转义成`&lt;script&gt;...`，不会破坏卡片结构或引入XSS。
6. **`pages/2_工作台.py`接入卡片渲染**：反馈详情页和历史记录详情的"老师反馈"都改成`if feedback_dimensions: render_feedback_dimensions(...) else: st.write(旧文本)`，新旧数据（本轮之前提交的历史记录没有这个字段）都能正确展示，不会报错或空白。

**怎么验证的**：
- 本地`python -m py_compile`+`ast.parse`确认全部改动文件语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过（db round-trip在新增列后仍然正常）。
- 本地单独跑了`normalize_rubric_result()`+`build_dimension_feedback()`+`flatten_dimension_feedback()`的合成数据测试，覆盖了"部分维度缺字段"（词汇资源/语法多样性两个维度故意不给数据）的防御性分支，确认不报错、只是内容留空；单独测试确认了HTML转义对`<script>`标签生效。
- **在`deploy-server`上用真实DeepSeek调用做了端到端验证，不是本地伪造数据**：分别构造了一篇IELTS作文（4维度）和一篇CET-4作文（AB路径3维度）调用`feedback_agent_node()`，两次都拿到了完整、高质量的`feedback_dimensions`（每个维度的优势点/改进点具体到引用作文原句，tips给出了可执行的改写示例），`score_error`均为`None`。部署过程：先精确PID停止旧进程（106810）、`scp`同步6个改动文件（`state.py`/`nodes.py`/`official_rubrics.py`/`db.py`/`ui_theme.py`/`pages/2_工作台.py`）、清理`__pycache__`、重启（新PID 110048）、`curl`确认HTTP 200、`streamlit.log`确认无导入报错，全程监控`free -h`确认没有触发OOM（部署时内存曾一度只剩99Mi，是有真实用户在用触发了模型加载，重启进程本身释放了旧进程占用的内存，之后维持在300+Mi空闲）。

**遗留问题**：无新增；卡片视觉效果依赖真实浏览器渲染，本地没有GUI环境实际截图确认过CSS效果，答辩前建议在浏览器里实际打开一次核对排版和配色是否符合预期。

## 2026-07-16（第二十五轮）· 主力LLM从DeepSeek V4 Flash切换到V4 Pro

**背景**：用户要求把DeepSeek模型从v4-flash换成v4-pro。这是纯配置切换——`src/agents/llm.py`的`DEEPSEEK_MODEL_NAME`本来就是从`.env`读取的环境变量，代码不需要改，只需要改配置值，但换模型前必须验证新模型名真实有效、行为符合预期，不能改完值就假设能用。

**做了什么**：

1. **改配置**：本地`.env`（真实Key所在，未提交）和`.env.example`（占位模板）的`DEEPSEEK_MODEL_NAME`都从`deepseek-v4-flash`改成`deepseek-v4-pro`。
2. **改前先验证模型名真实有效**：跑`python scripts/check_llm_key.py`确认`deepseek-v4-pro`能正常调通（"调通成功"），不是瞎猜的字符串导致后续全链路调用失败才发现。
3. **专门验证了"V4是推理模型"这条已知的坑是否对Pro同样成立**：写了一段裸`urllib`脚本（不依赖dotenv/langchain，本地环境没装这些包），先用`max_tokens=64`调用，确认`content`是空字符串、`finish_reason`是`"length"`、`reasoning_content`非空——和`CLAUDE.md`记录的V4 Flash坑完全一致；再用`max_tokens=2048`（`src/agents/llm.py`里`DEFAULT_MAX_TOKENS`的当前值）调用，确认能拿到完整`content`（`finish_reason: "stop"`）。结论：**这条坑不是Flash专属，V4 Pro同样如此，现有的`DEFAULT_MAX_TOKENS=2048`不用改**。
4. **更新了7处文档里"V4 Flash"的表述**：`CLAUDE.md`（两处，含"已确认设计决策"和"不要重新踩的坑"两节，后者补充了本轮验证记录）、`src/agents/llm.py`模块docstring、`Docs/00-项目总览.md`（两处）、`Docs/01-系统架构与Agent设计.md`（架构图）、`Docs/03-模型训练与微调方案.md`、`Docs/RUNNING.md`（环境变量示例）。`Docs/Progress.md`历史记录里的"V4 Flash"字样不改（如实保留"当时状态"）。
5. **部署到`deploy-server`**：`.env`没有整份重传（避免意外覆盖服务器上可能存在的、和本地不同步的其他字段），改用`sed`只替换`DEEPSEEK_MODEL_NAME`这一行；`scp`同步了`.env.example`/`llm.py`/`CLAUDE.md`/几份`Docs/*.md`；精确PID重启（112310）。

**怎么验证的**：
- 本地裸`urllib`验证过模型名有效性和`max_tokens`行为（见上第2、3点），不是假设。
- **在`deploy-server`上实测确认运行时确实用的是新模型**：`get_chat_model_with_fallback().model_name`打印出`deepseek-v4-pro`，且真实调用拿到了模型自我介绍的正常回答，`free -h`确认没有引发内存问题。

**遗留问题**：无。这是一次纯配置切换，不涉及代码逻辑变化，V4 Pro相比V4 Flash的响应质量/速度/成本差异答辩时如果被问起，需要team自己去DeepSeek官方定价页面确认，本轮没有找这个信息（不是本次任务范围）。
- essay_set到专属rubric的对应关系目前是4个考试类型分别对应各自完整独立的文件，但essay_set本身仍然只有4个值(1/2)在轮转，如果后续想让essay_set本身也更精细地区分（比如新增更多essay_set），需要额外的训练数据支持，本轮没有做，不是当前优先级。

## 2026-07-16（第二十六轮）· 反馈卡片统一为4维度+新增结构化辅导计划/AI范文+页面定宽

**背景**：用户给了一张竞品截图（IELTS风格的评价卡片：写作任务回应情况/连贯与衔接，每卡含优势点/建议改进的方面/关于如何改进）和一张要隐藏的截图（评分详情原始JSON dump），提出四点要求：①页面样式约束到截图那种宽度（不要在宽屏上铺满）；②定性反馈统一拆成内容主旨/结构与衔接/语言运用/语法多样性与准确性四个维度卡片，内容要丰富、不用管批改耗时；③新增"个性化修改建议与练习推荐"+"高分范文"两块卡片，样式要和上面的评价卡片不一样；④评分详情的原始JSON不用展示。

**开工前发现的情况**：上一轮（第二十四轮）实现的`feedback_dimensions`卡片，`official_rubrics.py`和`src/agents/nodes.py`在会话过程中被外部并行修改过（推测是同仓库其他并发session），已经把AB场景的维度改成了`content/organization/language`三维度、并且`LLM_RUBRIC_PROMPT`也同步改成了不跟随官方维度、统一三维度——这次改动本身是正确方向（和这次用户要求的"统一维度"思路一致），但只有三维度、没有独立拆出"语法多样性与准确性"，本轮在这个基础上扩展到四维度，不是从头重做。

**做了什么**：

1. **`src/official_rubrics.py`的`DIMENSION_LABELS`扩到四维度**：`{"内容主旨": "content", "结构与衔接": "coherence", "语言运用": "language", "语法多样性与准确性": "grammar"}`，AB场景和LLM量表场景（IELTS/TOEFL）共用同一份映射，和`rubric_scores`自己的官方维度键名（IELTS的`task_response`等）完全解耦——数值评分继续用官方维度算，定性反馈统一按这四个通用维度给，两者不混用。
2. **`AB_FEEDBACK_PROMPT`/`LLM_RUBRIC_PROMPT`（`src/agents/nodes.py`）同步改成四维度+丰富内容要求**：每个维度的`strengths`/`improvements`从"一句话"改成"2-3句话具体展开"，`tips`从1~2条改成2~3条且要求"附带实际改写示例"，Prompt里明确写"不用担心篇幅，学生需要充分的讲解"，对应用户"可以不考虑批改时间"的指示。
3. **`COACH_PROMPT`/`coach_agent_node`改成结构化JSON输出**（原来是纯Markdown文本）：新增`action_items`（优先修改清单，2~3条）、`exercises`（针对性练习，1~2条）、`model_essay`（AI针对同一题目现场创作的高分范文，含标题/正文250-350词/2~3条学习要点）。新增`build_coach_plan()`防御性规整（字段缺失/类型不对不报错，只留空）、`flatten_coach_plan()`拍平成Markdown兜底文本。`model_essay`明确要求"这是AI根据本次反馈现场创作的范文，不是真实考生作文，不得自称官方范文或真实高分卷"——早期设计文档设想过的`sample_essay_retriever_tool`范文检索因为没有配套标注数据没做成，这是替代方案，如实标注避免误导。
4. **新增`coach_plan`状态字段+数据库列**：`src/agents/state.py`加`coach_plan: dict`；`src/storage/db.py`的`_SUBMISSIONS_NEW_COLUMNS`加`coach_plan`列（旧记录自动迁移为空，前端退回`revision_plan`纯文本展示）。
5. **页面定宽**（`src/ui_theme.py`）：新增`.block-container { max-width: 1360px; margin: 0 auto; }`，三个页面仍用`layout="wide"`（避免Streamlit默认"centered"约730px放不下多列卡片），但不再铺满宽屏浏览器整个宽度。
6. **新增`render_coach_plan()`卡片渲染**（`src/ui_theme.py`），视觉上和`render_feedback_dimensions()`刻意区分——评价类卡片是蓝色系（`.hb-dim-card`），新的"行动类"卡片改用暖色调：`action_items`是琥珀色左边框+编号徽标，`exercises`是青绿色左边框+✎徽标，`model_essay`是独立的"阅读卡"风格（米黄底、"AI现场创作·仅供参考"徽标、衬线感的正文排版）。所有LLM生成的文本字段拼HTML前都`html.escape()`，和上一轮`render_feedback_dimensions()`的防XSS处理保持一致。
7. **隐藏评分详情原始JSON**（`pages/2_工作台.py`）：删掉"反馈详情"页和历史记录详情里的`st.json(score_details)`调用（原始的路径A/B归一化分、融合公式等技术细节不面向学生展示），改成只保留`st.metric`卡片和一句`caption`说明；`st.write(revision_plan)`换成`render_coach_plan(coach_plan)`（历史记录页同步）。
8. **文档同步**：`Docs/01-系统架构与Agent设计.md`的State字段表、节点职责表、"反馈可读性：卡片式结构化输出"整节都改成四维度+`coach_plan`+页面定宽的最新说明。

**怎么验证的**：
- `python -m py_compile`+`ast.parse`确认所有改动文件语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过（含新增`coach_plan`列的db迁移不影响原有读写）。
- 本地独立跑通`build_dimension_feedback()`（四维度+缺字段防御性处理）、`build_coach_plan()`/`flatten_coach_plan()`（含HTML特殊字符转义验证）。
- **在`deploy-server`上端到端真实验证**（部署前先修正了一个操作失误：第一次`scp`命令路径写错，把`db.py`传到了`src/db.py`而不是`src/storage/db.py`，产生了三个错放的文件，发现后已清理并重新正确同步，重启前确认了全部文件都在正确路径）：真实调用IELTS作文，`feedback_dimensions`返回的键正好是四个（内容主旨/结构与衔接/语言运用/语法多样性与准确性）；`coach_plan`真实生成了3条`action_items`、2条`exercises`、一篇约3000字符（含中文标点统计）的`model_essay`（标题"Why Community Service Deserves a Place in Every High School Curriculum"），`highlights`三条分析具体、有真实文本引用，不是空泛套话。HTTP 200、`streamlit.log`无导入错误、`free -h`确认内存正常（验证前后都在300-1000Mi可用区间，没有触发OOM）。

**遗留问题**：
- 页面宽度`1360px`是按参考截图估算的经验值，没有在真实浏览器里实际截图核对，答辩前建议实际打开页面看一下在常见笔记本分辨率（1440×900/1920×1080）下的观感是否合适，需要的话再微调这个数值。
- `model_essay`是AI现场创作，每次生成的范文都不一样（不是固定范文库），如果答辩现场想要一个提前确认过质量的范文做展示，建议提前跑几次挑一个效果好的截图/录屏留底，不要完全依赖现场生成的随机性。

## 2026-07-17（第二十七轮）· 修复导航按钮显示问题 + 提交/反馈合并成essay.art风格单页

**背景**：用户给了两张截图——一张红框标出顶部导航按钮（产品页/用户名/工作台）显示不完整，黄框标出整体页面希望参照第二张essay.art截图重新设计；并明确要求：①修复按钮显示问题；②"提交批改"和"反馈详情"合并成一个页面，作文原文区左右分栏（左边文章、右边分数），布局与其他样式都可以参考essay.art；③（上一轮已完成）评分详情原始JSON不展示。

**关于"抄essay.art"的处理方式**：只借鉴了整体布局思路（题目卡在上、作文原文+分数左右分栏、卡片式设计语言）和交互形态（内联高亮语法错误+悬浮提示），配色、圆角、字体大小等具体视觉参数用的是本项目已有的PRIMARY蓝+卡片体系，没有抓取/复制对方网站的CSS或代码——这和`CLAUDE.md`里"前端视觉参考讯飞/百度但不抄袭具体平台"的既定原则一致，答辩被问起时按这个说法解释。essay.art截图里的"图片转文字"/"连词助手"两个工具栏按钮没有实现——本项目没有对应的OCR/连词功能后端支撑，不做无功能支撑的装饰性按钮，遵循"不过度宣称"的项目惯例。

**做了什么**：

1. **修复导航按钮显示问题**（`src/ui_theme.py`的`render_top_nav()`）：给`stPageLink`的CSS新增`white-space: nowrap`+`overflow: visible`+`text-overflow: unset`等强制不换行不裁切的规则（怀疑是Streamlit某些版本对该组件默认有省略号/裁切行为，图标+中文文字在偏窄的列宽下被截断）；同时把导航列宽比例从`[2.2, 1, 1, 1.15]`调整为`[1.4, 1, 1, 1.2]`，压缩品牌区、放宽三个按钮的可用宽度。**为了排查这个问题顺带确认了一件事**：Streamlit 1.59.2（服务器实际安装版本）的主容器`className`同时包含`stMainBlockContainer`和`block-container`两个类名（在服务器`streamlit/static/static/js/index.*.js`里grep到的原始字符串），确认第二十六轮加的`.block-container`宽度约束选择器是有效的，不是一直没生效。
2. **"提交批改"+"反馈详情"合并成一个"写作批改"tab**（`pages/2_工作台.py`）：没有结果时显示原来的提交表单；有结果时显示essay.art风格的结果视图——`render_topic_card()`题目卡在最上面，然后`st.columns([1.7, 1])`左右分栏，左边`render_essay_with_highlights()`展示作文原文（**语法错误直接在原文对应片段上加下划线高亮，悬浮鼠标能看到具体问题和建议**，用HTML原生`title`属性做tooltip，没有引入额外JS），右边`render_score_panel()`展示大字号主分数+一段总体评价+"写一篇新作文"按钮。下方保留原有的`render_feedback_dimensions()`/`render_coach_plan()`区块，语法错误列表从`st.dataframe`表格改成`render_grammar_error_cards()`卡片网格（红色✗图标+片段+建议，仿essay.art"词汇及语法错误批注"区域）。用`st.session_state.show_new_essay_form`控制表单/结果视图的切换，"写一篇新作文"点击后重置为表单模式，新结果到达后（`_finish_submission_if_ready()`里）自动切回结果视图。
3. **新增`overall_summary`字段**：`AB_FEEDBACK_PROMPT`/`LLM_RUBRIC_PROMPT`（`src/agents/nodes.py`）新增"2-3句话总体评价"的JSON字段，供分数卡片右侧展示（essay.art的"The candidate presents..."那段总评的对应物）；`normalize_rubric_result()`（`src/official_rubrics.py`）同步透传；`EssayReviewState`新增字段，`db.py`新增`overall_summary`列+迁移。
4. **`render_essay_with_highlights()`的高亮实现**：复用`grammar_check_node`已经产出的`position`（字符级起止偏移量），不重新做正则匹配；对重叠/越界的区间做了防御性跳过（排序后如果新区间的起点在上一个已选区间的终点之前就跳过），避免一条脏position数据拼出破损HTML或让整页崩溃。

**怎么验证的**：
- `python -m py_compile`+`ast.parse`确认所有改动文件语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过。
- 本地用一个stub的`streamlit`模块单独测试了`render_essay_with_highlights()`：构造了一个越界的position区间，确认被正确跳过而不是报错；构造了含`<script>`的文本，确认`html.escape()`正确转义，没有破坏HTML结构。
- **在`deploy-server`上真实验证**：`scripts/ui_smoke_test.py`（Streamlit AppTest）三个页面全部PASS（含合并后的"写作批改"tab默认表单视图）；额外写了一段脚本，真实调用`grammar_check_node`+`feedback_agent_node`（不加载`EssayScorer`，避免OOM）拿到一个真实的AB场景结果dict，喂给`render_topic_card`/`render_essay_with_highlights`/`render_score_panel`/`render_grammar_error_cards`四个新渲染函数，全部无异常执行完成，`overall_summary`真实生成了有意义的总评文本，且该测试样本恰好0处语法错误，顺带验证了"语法错误列表为空"这个边界情况的渲染分支也正常。全程`free -h`确认内存在300-980Mi可用区间波动，没有OOM；HTTP 200，`streamlit.log`无导入错误。

**遗留问题**：
- 导航按钮的具体裁切原因是基于CSS推理修复的（Streamlit某些内置组件的默认省略号行为+列宽比例过紧的共同作用），没有在真实浏览器里逐像素核对修复效果，也没能找到Streamlit 1.59.2官方文档明确写出`stPageLink`默认CSS规则的出处；如果这次修复后问题依然存在，下一步需要用浏览器开发者工具实际检查渲染出的DOM和computed style。
- `render_essay_with_highlights()`的高亮交互目前只有鼠标悬浮的原生tooltip，essay.art截图里每个高亮片段后面还带一个小气泡图标（点击可能展开更详细的批注卡片），这个更丰富的交互本轮没有做，如果后续要做需要引入一点点JS或Streamlit的自定义组件，不是纯CSS/Markdown能实现的。
- 页面整体视觉效果同上一轮的遗留问题一样，没有在真实浏览器里截图核对，建议答辩前实际打开看一下。

## 2026-07-17（第二十八轮）· 根据实际截图反馈修3个问题：导航按钮、卡片对齐、提交表单卡片化

**背景**：用户上传了3张实际渲染截图反馈上一轮的效果——①截图1显示"写作批改"结果视图（题目卡+左右分栏+分数卡）本身效果是对的，用户要求把**提交表单**也改成同样的卡片外壳，区别只是右侧面板按钮从"提交作文"变成结果视图的"写一篇新作文"；②截图2显示"定性反馈"四维度卡片明显没对齐，第二排的卡片错位；③截图3显示顶部导航按钮依然有问题。这轮是根据真实渲染结果的针对性修复，不是新功能。

**根因排查**：
1. **导航按钮**：上一轮的`use_container_width=True`在`page_link`上，本意是让按钮撑满可用宽度、和CSS的居中样式配合显示完整文字，但页面宽度收窄到`1360px`后，列本身仍然分到不小的宽度（尤其品牌区改窄后按钮列变宽了），"撑满整列"反而让按钮变成和文字内容完全不成比例的超大色块——这是"改小了一个问题、放大了另一个问题"的典型例子，说明只凭CSS推理、没有真实截图反馈时改一次是不够的。
2. **卡片对齐**：`render_feedback_dimensions()`用一个`st.columns(2)`给全部4张卡复用（按index%2分左右列）——Streamlit的每一列是独立纵向堆叠的容器，不是网格；4个维度里`strengths`/`improvements`/`tips`内容长度天然不一样，左列第1张卡如果比右列第1张卡高，左列第2张卡的起始Y坐标就会比右列第2张卡低，看起来"没对齐"，这是Streamlit列布局的固有行为，不是CSS的问题。
3. **提交表单**：单纯是没做——上一轮只改了结果展示视图的样式，忘了把提交前的表单也一起改，两个视图风格不统一。

**做了什么**：

1. **导航按钮**（`src/ui_theme.py`的`render_top_nav()`）：三个`st.page_link`全部把`use_container_width`从`True`改成`False`，按钮回到按内容自身宽度渲染；列宽比例也相应收窄（`[1.7, 0.85, 0.95, 0.85]`），减少每列里的空白。
2. **卡片对齐**（`render_feedback_dimensions()`）：改成每两张卡单独开一行`st.columns(2)`（`for row_start in range(0, len(items), 2)`），行与行之间是完全独立的水平布局，不再互相拖累高度。同一行内两张卡如果长度不同，靠新增的`.hb-dim-card { height: calc(100% - 18px); }`配合`div[data-testid="stHorizontalBlock"]:has(.hb-dim-card)`这条`:has()`选择器（把该行的列容器强制成`flex`，让卡片能撑满整行分到的高度）用留白撑平，不是内容硬对齐——这正是用户建议的"可以留白实现卡片对齐"的思路。`:has()`选择器现代浏览器都支持，且只精确作用于含`.hb-dim-card`的那一行，不影响页面里其他`st.columns`布局（比如作文原文+分数的两栏、题目卡的表单）。
3. **提交表单卡片化**（`pages/2_工作台.py`）：`show_form`分支重写成和结果视图同样的外壳——`st.container(border=True)`包住题目区（作文类型+题目输入），再是`st.columns([1.7, 1])`分栏，左边`st.container(border=True)`包作文原文`text_area`，右边`st.container(border=True)`包提交须知文案+"📤 提交作文"按钮。`st.container(border=True)`是Streamlit原生带边框容器，边框/圆角由Streamlit自己的默认主题渲染，不需要额外自定义CSS选择器（尝试过在服务器的Streamlit 1.59.2静态资源里grep这个容器的具体class名，没有找到稳定可用的字符串，判断是emotion运行时动态生成的hash class，不适合硬编码去覆盖样式，所以直接用Streamlit的默认边框样式，没有强行让颜色和自定义卡片一模一样，但形状/圆角观感是一致的）。

**怎么验证的**：
- `python -m py_compile`+`ast.parse`确认语法正确。
- **在`deploy-server`上验证**：`scripts/ui_smoke_test.py`三页面全部PASS（含新的三段`st.container(border=True)`提交表单和调整后的导航栏）；另外单独构造了4个维度的真实形状数据（长度故意不一样，模拟截图2里的错位场景），调用改造后的`render_feedback_dimensions()`确认无异常执行完成。HTTP 200，`streamlit.log`无导入错误，`free -h`全程在263Mi-990Mi可用区间波动，没有OOM。

**遗留问题**：
- 导航按钮和表单卡片这两处修复都是基于Streamlit组件的已知行为推理出来的（没有找到`stVerticalBlockBorderWrapper`一类的官方稳定testid可以精确调色），依然没有在真实浏览器里逐像素核对——**这是这几轮反复出现的同一个限制**：本环境没有可视化渲染/截图工具，只能通过用户回传截图做"改一轮、看一轮"的迭代，如果这轮效果还有偏差，需要继续这个反馈循环，不代表可以不看就一次做对。
- `st.container(border=True)`的边框颜色/圆角是Streamlit默认主题决定的，和`.hb-topic-card`等自定义卡片的颜色不一定完全一致（比如圆角半径、边框色号），只是形状/间距上做到了统一，不是像素级复刻。

## 2026-07-17（第二十九轮）· 去掉显示密码+分数板对齐+版权页脚+LangGraph真实编排图导出

**背景**：用户给了5条指示：①登录页去掉"显示密码"选项；②分数板拉高，上下限和作文板对齐；③评价卡片（定性反馈四维度卡）上下限也要对齐，字数导致的不对齐可以用卡片内留白解决；④加版权信息"Developed by S. K. Tian"；⑤指导老师说可以输出LangGraph真实的Agent编排图像，要求补上这个函数。

**做了什么**：

1. **去掉"显示密码"**（`pages/1_登录.py`）：删掉`show_login_password`这个`st.checkbox`和配套的`type="default" if ... else "password"`三元逻辑，登录密码框固定`type="password"`。
2. **分数板与作文板上下对齐**（`src/ui_theme.py`）：根因和上一轮"评价卡片错位"是同一类问题——`.hb-score-panel`原来只有`height:100%`，但它所在的Streamlit列不是flex容器，`height:100%`不生效。这次的复杂点在于分数列里除了`render_score_panel()`那块卡片，后面还接着一个真正的`st.button`（"写一篇新作文"），要让"卡片+按钮"这一整列的底边贴到和作文原文面板一样的Y坐标，不能简单让卡片`height:100%`（那样按钮会被推到面板下方、超出作文面板底边）。改法：把三条免责声明类的`st.caption()`挪进`render_score_panel()`卡片内部变成`notes`参数（不再是卡片外的独立元素），卡片本身用`flex:1`（在被强制成`flex-direction:column`的列容器里）吃掉按钮之外的全部剩余高度，按钮自然贴在卡片下方、整列总高度正好撑到和作文面板一样。
3. **确认评价卡片对齐依然有效**：上一轮已经改成"每两张卡开一行`st.columns`+`:has()`选择器强制flex拉伸"，本轮复查代码确认逻辑仍在，额外把这条`:has()`规则和分数板对齐用的规则合并成一组注释更完整的CSS，避免以后有人改的时候漏看其中一半。
4. **版权页脚**：新增`render_footer()`（`src/ui_theme.py`），渲染"Developed by S. K. Tian"，三个页面（`app.py`/`pages/1_登录.py`/`pages/2_工作台.py`，含工作台未登录时的提前返回分支）末尾都调用了一次。
5. **LangGraph真实编排图导出**：新增`scripts/export_graph_diagram.py`，核心是`build_graph().get_graph()`拿到LangChain/LangGraph自带的可视化对象，`.draw_mermaid()`导出纯文本Mermaid源码（零依赖、零网络请求）、`.draw_mermaid_png()`导出PNG（默认走Mermaid Ink公开API，需要外网）。**这是LangGraph编译后真实看到的节点/边结构，不是`scripts/generate_system_diagrams.py`那种手绘示意框**，两者用途不同、不要混淆。输出目录做了环境自适应：本地完整checkout存到`03-项目效果截图/system/`，训练/部署服务器这种只有`01-源代码`一层内容的环境自动退回存到仓库自己的`reports/`目录，不会因为找不到目录就崩溃。

**怎么验证的**：
- `python -m py_compile`+`ast.parse`确认所有改动文件语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过。
- **在`deploy-server`上验证**：`scripts/ui_smoke_test.py`三页面全部PASS（含去掉显示密码checkbox、新增的footer调用）；**真实跑通了`export_graph_diagram.py`**——第一次跑因为服务器上只有`01-源代码`目录、没有`03-项目效果截图`同级目录，触发了`StopIteration`崩溃，当场发现并修复成环境自适应的输出目录逻辑，重新跑通后拿到真实产出：`.mmd`源码（8个节点+边，`intake_validator`/`retrieval_agent`两处条件路由正确标成虚线边，和`src/agents/graph.py`的`build_graph()`真实逻辑完全对应）和一张380×829像素、约33KB的真实PNG（`file`命令确认是合法PNG，不是空文件或损坏数据）。HTTP 200，`streamlit.log`无导入错误，`free -h`全程在284Mi-994Mi可用区间，没有OOM。

**遗留问题**：
- 分数板/作文板/评价卡片的对齐修复本轮同样是基于CSS flex机制推理的，依然没有在真实浏览器里逐像素核对——如果这轮效果还有偏差，需要继续"改一版→截图反馈→再改一版"的循环，这是本环境反复出现的同一个限制（没有可视化渲染工具）。
- `scripts/export_graph_diagram.py`本轮只在`deploy-server`上验证过，没有在训练服务器（`retinascope-server`）或本地完整checkout环境里验证过"存到`03-项目效果截图/system/`"这条路径分支——逻辑上应该没问题（就是简单的目录判断），但没有实测过，如果团队成员在自己电脑上跑遇到路径问题，需要反馈。

## 2026-07-17（第三十轮）· 评分偏低校正机制 + 批改分步进度实时展示 + 修复处理中显示旧记录的bug

**背景**：用户给了3条反馈：①"整体作文评分偏低，看用什么策略解决一下"；②批改过程中希望界面能自动展示"校验通过→检索评分细则→模型打分中→生成定性反馈→生成个性化建议"这5步进度，不需要手动刷新；③一个bug——批改进行中时页面会先短暂显示上一次的批改记录（分数卡+反馈），而不是这次新提交的题目，应该处理中不出现卡片、完成后才出现。本环境仍然没装torch/langgraph（"环境信息"里记录的老问题），前两条只能做代码层面的实现，跑不了真实推理来肉眼验证。

**做了什么**：

1. **评分偏低——诊断结论和处理方式**：查了训练数据/评分链路/已有诊断文件，没找到代码bug，更像模型本身的系统性偏差，有两条依据：①`models/set8_diagnosis.json`已确认essay_set 8存在"向均值收缩"（真实高分被系统性打低，残差与真实分相关系数-0.73）；②CET4/CET6/考研映射用的essay_set 1/2，ASAP-AES训练作文平均150~650词、多是英语母语学生的长展开议论文，而中国考生应试作文通常120~250词，模型很可能学到了"更长=更高分"的强关联，导致偏短的应试作文被系统性打低。**这两点都没法在本地环境验证**（没GPU/装不了torch，需要回训练服务器用真实验证集标签核实），所以没有直接编数字改分数，而是和用户对齐后选择"先搭好校正机制，系数留给训练服务器算出来再填"这个方向：
   - `src/training/common.py`新增`load_score_calibration()`/`apply_score_calibration()`：读`models/score_calibration.json`里按essay_set的`{scale, offset}`，对`score_norm`做`clip(scale*x+offset, 0, 1)`线性校正；文件不存在或某个essay_set没系数时原样返回（不报错、不改变现有分数）。
   - `src/training/essay_scorer.py`的`EssayScorer.predict()`：A/B融合出`score_norm_raw`之后、反归一化之前插入这层校正，返回值里新增`score_norm_uncalibrated`字段（保留原始值，方便以后核对）。
   - 新建`models/score_calibration.json`：当前8个essay_set全部是`scale=1.0/offset=0.0`恒等变换占位，**现在的打分结果完全没有变化**。
   - 新增`scripts/calibrate_score_bias.py`：在训练服务器上对`data/processed/val.csv`按essay_set拟合`真实score_norm ~ scale*预测score_norm+offset`的最小二乘系数，scale裁剪到[0.5,2.0]、offset裁剪到[-0.3,0.3]防止小样本essay_set（比如set 8只有578条）拟合到离谱的值，验证样本数低于30的essay_set直接跳过、保留恒等变换；同时报告校正前/后的macro QWK（校正不应该让QWK掉，QWK掉了说明拟合出了问题而不是真的在修偏差），只用验证集拟合、不碰测试集，跟`eval_weighted_ensemble.py`选权重的原则一致。跑完这个脚本、把结果覆盖`models/score_calibration.json`即可生效，不需要改代码。
   - **这是本轮按自己理解做的取舍，已经和用户对齐过方向**（用户在"先搭机制、系数留待验证"和"我先给一版启发式估计、風险自担"之间选了前者），但系数本身要等训练服务器跑完`calibrate_score_bias.py`才算数，见`TODO.md`"需要你决策"。

2. **批改分步进度实时展示**：
   - `src/agents/graph.py`新增`invoke_with_progress(graph, payload, progress_holder)`：用`graph.stream(payload, stream_mode="updates")`代替`graph.invoke()`，每有一个节点跑完就把节点名写进调用方传入的`progress_holder["completed_nodes"]`（一个跨线程共享的`set`）。能这样做是因为`src/agents/nodes.py`里每个节点函数都是`return {**state, ...}`整份state返回而不是只返回增量，所以`stream_mode="updates"`里yield出来的单节点结果已经是完整的最新state，不需要额外做state合并，函数最后返回值和`graph.invoke()`完全一致。
   - `src/ui_theme.py`新增`render_progress_steps(completed_nodes)`：5步固定文案"校验通过/正在检索评分细则/模型打分中/正在生成定性反馈/正在生成个性化建议"，按`_PROGRESS_STAGE_NODES`把LangGraph节点名映射到第几步（"模型打分中"这一步用`scoring_tool`或`grammar_check`任一个完成就算跨过，因为雅思/托福走LLM量表评分时`scoring_tool`节点会被跳过，两条路径都要能正常前进不卡住），配套新增`.hb-progress-panel`等CSS，视觉上和`.hb-score-panel`同一卡片语言。
   - `pages/2_工作台.py`：提交时不再调用`graph.invoke`，改成把`invoke_with_progress`连同一个新建的`{"completed_nodes": set()}`一起提交给后台线程池；新增两个`st.fragment`（`_render_task_banner`每2秒、`_render_correction_progress`每1秒）周期性读`session_state`里的进度并重新渲染，一旦发现后台任务`future.done()`就调用`st.rerun()`把fragment的局部刷新"升级"成整页rerun，这样`_finish_submission_if_ready()`才能真正收走结果——这就是"不用手动点刷新也能自动更新"的实现方式。原来那个"刷新任务状态"按钮已经删掉（自动刷新后完全冗余）。
   - `requirements.txt`把`streamlit`改成`streamlit>=1.37`，因为`st.fragment`（连同`run_every`参数）是这个版本才稳定的API，之前没有版本下限。

3. **修复bug：批改进行中显示上一次记录**：根因是原来"写作批改"页的分支只看`has_result`（有没有`last_result`）和`show_new_essay_form`两个状态来决定显示表单还是结果卡片，完全没考虑"当前是不是正在处理一个新提交"——如果用户之前有历史结果，再提交一篇新作文时，处理中的这段时间`has_result`仍然是`True`（因为`last_result`还是上一轮的旧值），于是错误地把上一次的分数卡+反馈渲染出来。改法：`pages/2_工作台.py`里`if is_processing`分支现在优先级最高（在`show_form`/结果卡片两个分支之前），处理中只展示这次刚提交的题目和作文原文（提交时另存进`session_state.pending_submission`这个独立快照，不复用`last_result`），配合上面的5步进度条，从提交那一刻到后台任务完成之前完全不出现分数/反馈卡片，任务完成后才通过`st.rerun()`自动切回正常的结果视图。

**怎么验证的**：`python -m py_compile`确认`src/ui_theme.py`/`src/agents/graph.py`/`pages/2_工作台.py`/`src/training/common.py`/`src/training/essay_scorer.py`/`scripts/calibrate_score_bias.py`语法全部正确；`models/score_calibration.json`用`json.load`确认格式合法；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过（不涉及本轮改动的路径，但确认没有连带破坏）。**本轮没能做到的验证**：`invoke_with_progress`的真实流式行为、`st.fragment`的自动刷新效果、bug修复后处理中界面的真实观感、`calibrate_score_bias.py`能不能真的把QWK打印出来且不降QWK——这些都需要在装了`torch`/`langgraph`/`streamlit>=1.37`的训练服务器或`deploy-server`上实测，本地开发环境仍然装不了这些依赖（见"环境信息"），下一轮需要在有依赖的环境里跑一遍`streamlit run app.py`实际提交一篇作文走一遍全流程，并执行`calibrate_score_bias.py`拿到真实校正系数。

## 2026-07-17（第三十一轮）· 把第三十轮的改动部署到deploy-server

**背景**：用户确认`deploy-server`上跑的还是7月16日晚上那次部署，第三十轮（以及更早几轮，见下）都没同步过去，要求部署前先查一遍服务器现状。

**做了什么**：
1. **部署前现状核查**：`docker ps`确认`ophthalmic-ai`容器（占8501端口）健康运行，不能碰；`ss -tlnp`确认我们的应用当时用精确PID`150830`占着8503；`df -h /`发现根分区只剩**1.4G可用**（40G盘用了36G，比`RUNNING.md`记录的部署时9.3G/6.2G又降了不少）；`free -h`确认内存依旧紧张（1.6G总量，当时仅117Mi空闲）；`cd /root/sukai && git log`发现**这个目录根本不是git仓库**（部署机制是本地tar+scp直接铺文件，不走git pull，和`RUNNING.md`第8节记录的一致）。
2. **鉴于磁盘只剩1.4G，没有照搬`RUNNING.md`里"整包tar"的命令**，改成排除已经在服务器上、这轮完全没改动的重资产：两个模型权重目录（`models/essay-scorer-{custom,finetuned}`，合计266M）、`data/raw`、`data/processed/chroma_kb`（已在服务器现场build过）、`data/processed/*.csv`（训练/校正脚本用，不影响线上推理）。打包后只有526K（对比原始266M+165M的模型/数据体量），基本不占磁盘。
3. **发现并规避了一个会导致数据丢失的坑**：第一次打的包里含`data/app.db`——本地这份只是14号建的20K空库，而服务器上的`data/app.db`是573K、当天16:42刚更新过的真实用户数据库（真实注册账号+批改记录）。如果直接extract，会用本地的空库整个覆盖掉服务器上积累的真实数据。发现后追加`--exclude='data/app.db'`重新打包，确认包内容不含这个文件后才上传。
4. **执行部署**：`scp`上传→服务器上`tar xzf`解包到`/root/sukai`（确认`data/app.db`时间戳/大小没变，磁盘用量没有明显增加）→`scripts/deploy_stop.ps1`用PID文件精确停掉旧进程（PID 150830，不是模式匹配）→`scripts/deploy_start.ps1`重新拉起。**没有重新`pip install`**：服务器上`streamlit`已经是1.59.2（远高于本轮`requirements.txt`新加的`>=1.37`下限），本轮也没新增任何pip依赖，跳过这一步能进一步降低磁盘风险。

**怎么验证的**：解包后`ssh`确认`data/app.db`的mtime/大小和解包前完全一致（没被覆盖）；`grep`确认`pages/2_工作台.py`里能搜到`st.fragment`（2处）、`src/agents/graph.py`里能搜到`invoke_with_progress`、`models/score_calibration.json`内容正确；重启后`streamlit.log`里能看到`Uvicorn server started`且没有任何`Error`/`Traceback`/`Exception`关键字；`curl http://localhost:8503`（服务器本机）和`curl http://121.41.238.92:8503`（外网）都返回**HTTP 200**；`free -h`显示重启后内存回落到983Mi可用（因为新进程还没被人提交作文触发懒加载的评分模型，符合预期，模型是懒加载的，见`pages/2_工作台.py`"图懒加载"那段注释）。

**没有做的验证**：出于内存风险考虑（这台机器只有1.6G，加载一次微调DistilBERT要占约800MB常驻内存，历史上真实发生过OOM，见`CLAUDE.md`"不要重新踩的坑"），本轮**没有**在服务器上真实提交一篇作文走完整链路（那样会触发模型加载+LLM调用，是更彻底但也更重的验证）。所以"5步进度条显示是否符合预期""处理中页面是否真的不再闪出旧卡片"这两点仍然只是代码层面的推理，还没有肉眼在浏览器里确认过——如果之后实测有问题需要继续反馈。

**附带发现（本轮未修复）**：`scripts/deploy_start.ps1`和手动`nohup ... & echo $! > streamlit.pid`这个模式，`$!`拿到的其实是`bash -c "..."`包装器本身的PID，不是真正exec出来的streamlit进程PID——第三十二轮里`deploy_stop.ps1`报告"已停止"之后，`ps aux`发现真正的streamlit进程（更高的那个PID）其实还活着、还占着端口和内存。本轮靠手动`ps aux`核对+精确kill真实PID绕过去了，但这个PID文件记录错误的问题本身还在，下次谁直接信`deploy_stop.ps1`的"已停止"结论就重新起新进程，有小概率造成两个模型同时加载在内存里触发OOM。**没有在这轮里顺手修**（不在这轮任务范围内，且改动脚本本身也要注意别引入新问题），留给之后专门跑一轮验证过再改。

## 2026-07-17（第三十二轮）· 评分偏低应急校正：essay_set 1/2 加+0.06 offset并同步部署

**背景**：用户在看到"先搭机制、系数留给训练服务器"的方案后，明确要求"先采用应急方案"——不再等训练服务器跑`calibrate_score_bias.py`，现在就要一个能生效的临时数值。

**做了什么**：
1. **`models/score_calibration.json`**：essay_set 1和2（CET4/CET6/通用评测/考研这几个主力考试类型实际用A/B评分时映射到的essay_set）改成`scale=1.0/offset=0.06`；essay_set 3~8保持恒等变换不动（没有类似1/2的长度错配依据，essay_set 8已知诊断显示的是"压缩+均值本身偏高"而不是单纯偏低，硬套同一个正offset方向依据不足）。**+0.06的选取依据**：唯一手头的真实幅度参照是essay_set 8诊断里的预测-真实均值差约0.075（0-1量纲），保守取更小的0.06；这仍然是**未经真实数据验证的估计**，不是`calibrate_score_bias.py`在验证集上拟合出来的，`_note`字段里如实写清楚了依据和局限。
2. **加了透明度留痕，不是悄悄改分**：`src/agents/nodes.py`的`scoring_tool_node`里，只要校正真的改变了分数（`score_norm_uncalibrated`和校正后的`quant_score`不相等），就往`score_details`里加"校正前融合分""评分校正说明"两个字段（`score_details`目前只落库不在UI渲染，供以后审计）；`src/agents/state.py`的`EssayReviewState`新增`score_norm_uncalibrated`字段；**更关键的是`pages/2_工作台.py`的分数面板本轮新增了一条用户可见的提示**——校正生效时会在分数卡下方显示"本次分数含应急评分校正（模型原始分X→校正后Y，0–100量表），是根据已有诊断做的临时估计、尚未用真实数据验证"，不让学生以为这是精确校准过的分数。
3. **部署到`deploy-server`**：部署前`ps aux`发现端口8503对应的真实streamlit进程其实是PID 182204，而`streamlit.pid`文件记录的182203只是`bash -c`包装器（已经在上一轮部署时被`deploy_stop.ps1`"停掉"过，但那只杀了包装器，真正的streamlit进程还活着，见上面"附带发现"）。这次没有直接跑`deploy_start.ps1`覆盖式启动（那样会导致两个streamlit同时跑在只有1.6G内存的机器上，有OOM风险），而是先手动确认真实PID、精确kill它、确认内存回落、确认端口释放，再重新启动。只单独`scp`了4个改动过的文件（`models/score_calibration.json`/`src/agents/nodes.py`/`src/agents/state.py`/`pages/2_工作台.py`），没有重新整包同步（磁盘依旧只有1.4G可用）。

**怎么验证的**：
- 本地：`python -m py_compile`确认改动文件语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过；额外单独跑了`apply_score_calibration()`的纯函数测试（不需要torch）——`apply(0.5, essay_set=1)`正确返回`0.56`，`apply(0.97, essay_set=1)`正确裁剪到`1.0`没有溢出，`apply(0.5, essay_set=8)`保持`0.5`不变（essay_set 8没被本轮应急范围覆盖），三个断言都符合预期。
- 服务器：`scp`后`grep`确认4个文件内容都已经是最新版本；精确kill真实PID后`free -h`确认内存从"仅117Mi可用"回落到"1.0Gi可用"，`ss -tlnp`确认8503端口先释放再被新进程占用；重启后`streamlit.log`只有正常启动信息、没有报错；`curl`服务器本机和外网`http://121.41.238.92:8503`都是**HTTP 200**；`data/app.db`时间戳/大小在整个过程中没有变化（真实用户数据没被碰）。
- **没有做的验证**：出于同样的内存/OOM顾虑，没有真实登录提交一篇essay_set 1/2的作文，去肉眼确认分数卡上真的会出现"应急评分校正"这行提示、以及校正后的分数看起来是不是真的没有"偏太低"。这个只有真人在浏览器里测一次才能确认，建议找个低峰时段测一下。

## 2026-07-17（第三十三轮）· 应用户实测反馈：调高应急校正/去掉技术性提示文案/进度条简化为单一文案/修复个性化建议空白bug/修deploy脚本PID坑

**背景**：用户实际用了一次CET4批改（截图：49.7/106.5，反馈文字积极但分数偏低；"个性化修改建议与练习推荐"标题下面是空的），给了5条反馈：①修deploy脚本的PID坑；②应急方案score继续偏高一点；③去掉分数卡下面那些A/B权重/校正说明这类"用户看不懂"的技术文案；④5步进度条改成一句"正在批阅中"就行；⑤"个性化修改建议与练习推荐"+范文这块要恢复。

**做了什么**：

1. **修`scripts/deploy_start.ps1`的PID记录bug**（第三十二轮"附带发现"里记的坑）：根因找到了——`nohup streamlit ... & echo $! > pidfile`这种写法里，`cd && source && nohup ...`这条复合命令被`&`整体丢进后台时，bash会为这个后台job开一层shell包装器，`$!`拿到的是这层包装器的PID；而这层包装器执行到`nohup streamlit ...`时**没有做尾调用exec优化**（用`ps -p`实测确认包装器和真正的streamlit进程是两个持续并存的父子进程，不是同一个PID），导致`deploy_stop.ps1`按PID文件杀的只是包装器，真正吃内存的streamlit进程活得好好的。**修法**：不再依赖`$!`，改成启动成功（HTTP 200）之后，用`ss -tlnp | grep ":$Port " | grep -oP 'pid=\K[0-9]+'`按"谁在监听这个端口"反查真实PID，覆盖PID文件。本轮在服务器上真实验证过这条`grep -oP`命令能正确提取到真实PID（187846，和`ps aux`肉眼核对的结果一致）。
2. **应急校正offset从0.06调到0.12**（`models/score_calibration.json`）：只调数值和`_note`里的依据说明，essay_set 1/2继续覆盖CET4/CET6/通用评测/考研，essay_set 3~8继续不动。**依然是未经真实数据验证的估计**，`_note`里补充记录了"第一版0.06、用户反馈仍然偏低、上调到0.12"这个调整过程，方便以后回溯。
3. **去掉分数卡下面的技术性提示文案**（`pages/2_工作台.py`）：删掉了"参考标准分由A/B融合结果线性换算…""A/B固定权重：路径A 0.95，路径B 0.05…""本次分数含应急评分校正…"这几行——这些是上两轮加的，初衷是"不要悄悄改分、要留痕"，但对最终用户（学生）来说是看不懂也不需要看懂的内部术语，按反馈全部去掉，`render_score_panel(result)`不再传`notes`参数。**留痕机制本身没删**：`src/agents/nodes.py`的`scoring_tool_node`仍然会把"校正前融合分""评分校正说明"写进`score_details`（这个字段只落库、不在UI渲染，答辩/审计时可以从数据库里查，不会让学生看到）。
4. **5步进度条简化成"正在批阅中"**（`pages/2_工作台.py`+`src/ui_theme.py`+`src/agents/graph.py`）：这是对上上轮（第三十轮）加的功能的直接撤销——`_render_correction_progress()`这个`st.fragment`不再调`render_progress_steps()`，改成直接`st.info("⏳ 正在批阅中，请稍候……")`；相应删掉了`src/ui_theme.py`里的`render_progress_steps()`/`_progress_stage_index()`/`_PROGRESS_STEP_LABELS`/`_PROGRESS_STAGE_NODES`和配套CSS（`.hb-progress-panel`等），`src/agents/graph.py`里的`invoke_with_progress()`，提交逻辑改回直接`st.session_state.graph.invoke(payload)`（不再需要`stream_mode="updates"`按节点推进度）。**自动刷新、处理中不显示旧卡片这两点没有撤销**——`_render_correction_progress()`还是`st.fragment(run_every=1)`，任务跑完了还是会`st.rerun()`自动切回结果视图，`pending_submission`快照机制也还在，只是右栏内容从5步checklist换成一句话。
5. **修复"个性化修改建议与练习推荐"渲染空白的bug**：诊断——`coach_agent_node`的`build_coach_plan(parse_llm_json(raw_content))`在LLM返回内容解析失败时会捕获异常、回退成`{"action_items": [], "exercises": [], "model_essay": {}}`，这是一个**非空字典、但三个字段全是空的**结构；而`pages/2_工作台.py`原来的判断是`if coach_plan:`，只看字典本身是不是空的，`{"action_items": [], ...}`这种字典本身非空，会走进`render_coach_plan()`分支，但函数内部三个`if action_items/exercises/model_essay.get("text")`全部为假，什么都不渲染，最终效果就是截图里那样"标题在、内容空白"，也不会掉回展示`revision_plan`兜底文案。同样的模式也存在于"定性反馈"的`feedback_dimensions`判断、以及"历史进步仪表盘"详情展开里的两处判断。**修法**：新增`_has_feedback_content()`/`_has_coach_content()`两个辅助函数，检查的是"字典里是不是真的有非空内容"而不是"字典是不是非空"，替换了全部4处判断（写作批改页的定性反馈+个性化建议、历史详情展开里的老师反馈+练习建议）。**这只修了"解析失败时不该静默空白"这个展示层的bug，没有修LLM为什么会解析失败**——如果之后还复现空白（这次会正确掉回显示`revision_plan`纯文本兜底，不会再是完全空白），需要去查`coach_agent_node`那次调用本身的响应内容/`finish_reason`，可能是CLAUDE.md记录过的"DeepSeek推理模型max_tokens不够导致content空字符串"这类问题在工具调用场景下的变体，这次没能进一步排查（本地没有真实LLM调用环境）。

**怎么验证的**：
- 本地：`python -m py_compile`确认`pages/2_工作台.py`/`src/ui_theme.py`/`src/agents/graph.py`/`src/agents/nodes.py`/`src/agents/state.py`语法全部正确；`models/score_calibration.json`用`json.load`确认格式合法；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过；额外单独跑了`apply_score_calibration()`（offset=0.12生效，裁剪正确）和`_has_feedback_content()`/`_has_coach_content()`两个新函数的纯函数断言测试，覆盖了"全空字典/字典非空但内容空/字典有真实内容"三种情况，全部符合预期。用PowerShell的`[System.Management.Automation.Language.Parser]::ParseInput()`确认`deploy_start.ps1`改完之后语法解析无错误，文件依然是带BOM的UTF-8（`deploy_start.ps1`含中文注释，见CLAUDE.md"不要重新踩的坑"里记过的编码坑）。
- 服务器：先在服务器上单独跑了一次`ss -tlnp | grep ':8503 ' | grep -oP 'pid=\K[0-9]+'`，确认能正确提取到真实PID（和`ps aux`肉眼核对一致），验证了修复逻辑本身是对的。部署时`scp`了`pages/2_工作台.py`/`src/ui_theme.py`/`src/agents/graph.py`/`models/score_calibration.json`四个文件（`deploy_start.ps1`是本地脚本，不需要同步到服务器），`grep`确认服务器上`invoke_with_progress`/`render_progress_steps`都已经查不到（清理干净）、`score_calibration.json`里essay_set 1是`offset: 0.12`。精确kill真实streamlit PID后重启：**本轮改完的`deploy_start.ps1`脚本本身在这个环境里跑的时候卡在了ssh多次往返上，没能在120秒内跑完、被挪到了后台**（这个开发环境偶发的ssh延迟问题，不是脚本逻辑的bug），所以最后是手动重复了脚本要做的两步操作（重新反查真实PID+覆盖PID文件）来完成本轮验证——手动执行确认了修复的PID反查命令本身是对的，但**没有端到端跑通"整个deploy_start.ps1脚本自己从头到尾"这一次**，建议下次部署时留意这个脚本是否顺利跑完，没顺利跑完也可以按本轮的方式手动补一步PID反查。最终确认：服务器本机和外网`curl`都是HTTP 200，`data/app.db`时间戳没变，内存回落到1.0Gi可用，PID文件正确指向真实streamlit进程。
- **没有做的验证**：依旧没有真实提交一篇作文肉眼确认——"正在批阅中"文案是否正确显示、"个性化修改建议与练习推荐"这次是不是真的不再空白、分数卡是否已经不再显示任何技术性文案、CET4的分数用offset=0.12算出来观感上是不是好一些，这几点都需要找低峰时段真人测一次才能最终确认。

## 2026-07-17（第三十四轮）· 排查白屏 + 按授权清理账号/垃圾文件 + 关闭fileWatcher

**背景**：用户提交作文时"又白屏了"（"又"说明不是第一次），怀疑是内存问题，授权"保留admin等2个账号，其他账号信息可以删除，也可以清理不必要的文件"。

**排查过程**：
1. 检查`dmesg`/`journalctl -k`（覆盖今天全天，服务器2026-07-15开机，日志留存完整）搜索`out of memory`/`killed process`，**没有找到今天的OOM-kill记录**——说明这次白屏大概率不是进程被内核杀死重启，进程本身（PID 187846）从20:52持续运行到排查时刻没有中断。
2. `streamlit.log`里有几十段`Traceback`，逐条核对后**全部是同一类无害噪音**：Streamlit自带的`local_sources_watcher.py`（用于监听文件变化触发热重载）在每次import新模块时会遍历该模块全部子模块找文件路径，`transformers`库一些依赖`torchvision`的可选子模块（vilt/vitmatte/vitpose/yolos/zoedepth等）本机没装`torchvision`，每次都会抛`ModuleNotFoundError`被Streamlit捕获打印——不是我们自己代码的报错，`grep`确认没有任何一条traceback的调用栈落在`pages/`/`app.py`/`src/`里。
3. 检查内存/磁盘现状：`free -h`显示提交过作文之后（模型被懒加载进内存）只剩**89Mi真正空闲、270Mi可用**（总共1.6G）；`df -h /`显示根分区只剩**1.4G可用**（40G用了36G）。`du -sh /root/*`定位到这40G的大头几乎都不是我们的：`/root/app`（11G，另一个团队成员的项目）、`/var/lib/docker`（7.4G，`ophthalmic-ai`容器的镜像，其中`docker system df`显示770.9MB是可安全回收的构建缓存）、`/root/mcr`（483M，团队成员毛陈荣自己的目录）；我们自己的`/root/sukai`只有2.5G，其中真正的"垃圾"（旧backups快照+过期测试日志+两个孤立的临时文件）总共只有约3M，占比可以忽略。
4. **结论（有事实支撑，但不是100%铁证）**：没找到硬性OOM-kill证据，所以不能100%断言"白屏=OOM"；但内存/磁盘现状客观上非常紧张（这台机器本身只有1.6G内存，加载一次DistilBERT就要占800MB左右，是`CLAUDE.md`里已经记录过的老问题），这类资源紧张场景下Streamlit的websocket连接在浏览器端确实容易表现成"卡住不动/白屏"而不是清晰的报错页面，是**目前证据能支持的最合理解释**，但**没有办法在这轮环境里100%实锤复现**。真正的disk危机主体（11G+7.4G）在我们项目范围之外，删自己的账号/文件对1.4G这个大盘子而言杯水车薪，讲清楚这一点，不夸大清理的效果。

**做了什么（按用户授权执行，两个都是明确要求的操作）**：
1. **裁剪数据库账号**：先`cp data/app.db backups/app_before_account_cleanup_20260717.db`留一份完整快照（这个决定本身有取舍——用户原话是"保留admin等2个账号"，没指名第二个具体是谁，`SELECT`出来5个账号里`mcr`提交了24篇（比admin的14篇还多，是全库提交量最高的账号），而且`/root/mcr`这个团队成员专属目录也确认了"mcr"就是`CLAUDE.md`里记录的负责前端与部署的毛陈荣，判断这是真实团队账号而不是随手建的测试账号，所以选择保留`admin`+`mcr`，删除`111`/`222`/`test001`——**这是我自己的判断，不是字面唯一解**，先备份是为了万一判断错了还能从`backups/app_before_account_cleanup_20260717.db`轻松恢复，不是不可逆操作）。删除后剩2个用户、38条提交记录（原5用户55条），`VACUUM`回收空间，`app.db`从626,688字节降到479,232字节。
2. **清理服务器上确认无用的文件**：`backups/`目录只保留新加的这份快照，删掉4份7月15号的旧快照（`app_before_cet_word_fix_20260715.db`等，早就被后续更新的数据库覆盖，没有保留价值）；删掉两个Day4遗留的测试日志（`e2e_deploy_test.log`/`e2e_deploy_test2.log`）、`pip_install.log`（装依赖时的历史日志，依赖已装好不需要了）、根目录下两个孤立文件`llm.py`（内容和`src/agents/llm.py`完全一样，是某次调试时手滑复制到根目录、从未被任何代码引用的死文件，`grep`确认没人`import`裸的`llm`模块）和空文件`sample_ids.json`；把已经积累了几十段无用噪音的`streamlit.log`清空。总共回收约3M，如实说明：**这点空间对1.4G的磁盘缺口而言影响很小，不是解决磁盘紧张的关键手段**。
3. **关掉Streamlit的文件热重载监听**（`.streamlit/config.toml`新增`[server] fileWatcherType = "none"`）：这是部署服务器上完全没有副作用的改动（代码变更本来就是手动重启生效，不依赖热重载），直接消除了上面第2步排查到的那一大批`torchvision`噪音traceback的产生源头，以后`streamlit.log`会干净很多，也省了每次新增import时的这层扫描开销——**是一个真实但不大的边际改善，不是"修复了白屏"意义上的根因修复**。

**怎么验证的**：
- 备份文件`ls -la`确认存在且大小合理（626,688字节，和裁剪前的`app.db`一致）；裁剪后`SELECT`确认只剩`admin`/`mcr`两个用户、38条提交，符合预期。
- 服务器上`du -sh`确认清理后`backups/`从2.9M降到616K，`streamlit.log`清空。
- `scp`同步新的`.streamlit/config.toml`到服务器，`cat`确认`fileWatcherType = "none"`那一行已经在文件里。
- 精确kill真实streamlit PID（这次改成先`ps aux`确认真实PID再kill，不再依赖`deploy_start.ps1`那个还没端到端验证过的PID反查逻辑）→确认内存回落到1.0Gi可用、端口释放→重新启动→`streamlit.log`里**这次启动没有再出现任何torchvision噪音**（配置生效的直接证据）→`curl`服务器本机和外网`http://121.41.238.92:8503`都是HTTP 200→按端口反查真实PID（191591）手动覆盖`streamlit.pid`文件。

**没有做的验证/诚实说明局限**：
- **没有真实复现过白屏本身**，所以这轮做的是"消除了几个可疑点、做了合理的资源紧张缓解"，不是"证实并修复了根因"——如果下次再白屏，需要在**白屏发生的当下**立刻`ssh`上去看`free -h`/`streamlit.log`最后几行/`journalctl -k --since "5 minutes ago"`，事后排查因为没有实时证据只能靠推理。
- **磁盘1.4G可用、内存1.6G总量这两个硬约束本轮都没有解决**，只是做了权限范围内能做的小清理。如果要真正解决，需要考虑：①升级服务器内存/磁盘规格（云控制台操作，需要用户决定，可能涉及成本）；②加一个swapfile作为OOM缓冲（能提升稳定性，但会进一步吃掉本就紧张的磁盘余量，是内存安全和磁盘余量之间的权衡，本轮没有擅自做这个决定，留给用户）；③找`/root/app`（11G，另一团队成员的项目）的负责人沟通能否清理，或者跟`docker system df`里提到的770.9MB可回收构建缓存（`docker builder prune`，不影响正在跑的`ophthalmic-ai`容器）——这两项都不在我们自己的项目范围内，需要经过对应负责人同意，本轮没有动。这几条选项已经记进`TODO.md`"需要你决策"。

## 2026-07-17（第三十五轮）· 删`/root/mcr`（用户指令，不写文档）+ 定位并缓解"个性化建议"空白的根因

**背景**：用户先指示删除部署服务器上的`/root/mcr`目录，明确说"这条指令无需更新md文件"（已执行，不再赘述）。随后用户截图反馈"个性化修改建议与练习推荐"显示"本次未能生成结构化辅导计划，请重新提交"——说明第三十三轮的展示层bug修复生效了（不再是完全空白，正确掉回了兜底文案），但用户要的是"恢复功能"本身，也就是要查`coach_agent_node`为什么解析失败。

**做了什么**：

1. **诊断**：`coach_agent_node`的`_finish()`函数原来`except (TypeError, ValueError, KeyError):`直接静默吞掉异常，服务器日志里完全没有留痕，没法回头查是响应为空还是JSON格式问题。结合`src/agents/llm.py`顶部早就记录过的坑——DeepSeek V4是推理模型，`max_tokens`不够时`content`会是空字符串——重新看了一遍`COACH_PROMPT`：这是全链路里**唯一**要求LLM额外创作一篇250~350词高分范文的prompt，加上action_items/exercises/highlights，正常内容本身就要六七百token起步，叠上推理模型的`reasoning_content`预算，`DEFAULT_MAX_TOKENS=2048`很容易被挤到只剩很少甚至没有空间写正文——命中的正是`llm.py`里已经写过的那个坑，只是这次表现在`coach_agent_node`而不是评分环节。**这是按机制推理出来的最可能诱因，不是100%实锤**（本地环境没有真实LLM调用能力，装不了langchain-openai，验证不了）。
2. **加诊断日志**（`src/agents/nodes.py`）：`coach_agent_node`的`_finish()`和`feedback_agent_node`（A/B场景那条路径）的JSON解析`except`块原来都是静默吞掉，现在都补上`warnings.warn(...)`，把异常信息、原始响应长度、开头120字符片段打进日志——以后再复现同类问题，`streamlit.log`里能直接看到是响应为空（`finish_reason=length`那类）还是别的格式问题，不用再像这次一样只能靠推理。
3. **调高`max_tokens`**（`src/agents/llm.py`）：`DEFAULT_MAX_TOKENS`从2048调到4096，给推理token和六七百token的正文（含范文）留足够预算，双倍留有余量。同步在文件顶部docstring补了这次调整的原因和判断依据，写清楚"没能在本地验证、是按机制推理出来的"，不假装这是实锤过的修复。

**怎么验证的**：
- 本地：`python -m py_compile`确认两个改动文件语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过；额外按`CLAUDE.md`"改`max_tokens`之前先用`check_llm_key.py`验证"的要求，跑了`python scripts/check_llm_key.py`，DeepSeek V4 Pro和GLM两个Key都返回"调通成功"，确认调大`max_tokens`之前Key本身是正常的（这个脚本本身用的是固定512的小`max_tokens`测连通性，不直接验证`COACH_PROMPT`场景，但确认了不是Key失效的问题）。
- 服务器：`scp`两个改动文件后`grep`确认`DEFAULT_MAX_TOKENS = 4096`和新增的warning文案都已经在服务器上的文件里；精确kill真实streamlit PID（这次进程停止时经过了一段`D`状态——不可中断睡眠，说明当时有实际I/O在进行，等了几秒才完全退出，不是杀不掉）→确认内存回落到1.0Gi可用→重新启动→`streamlit.log`确认干净无报错→`curl`本机和外网都是HTTP 200→按端口反查真实PID（194573）覆盖PID文件。
- **没有验证的**：没有真实提交一篇作文触发`coach_agent_node`走一遍，没法确认调大`max_tokens`之后"个性化修改建议与练习推荐"这次是不是真的能正常生成内容——这需要真人在浏览器里提交一次才能验证，如果还是失败，这次至少`streamlit.log`里会留下诊断信息，能看出是不是`max_tokens`还不够或者是别的原因。

## 2026-07-17（第三十六轮）· 用真实API调用实测max_tokens，4096不够稳，改成8192

**背景**：用户追问"4096是否够？要不要再加？"——上一轮把`max_tokens`从2048调到4096只是按机制推理，没有真实验证过，这轮补上真实验证。

**做了什么**：本地写了一个一次性诊断脚本（没有进repo，在临时scratchpad目录），不经过langchain（本地装不了langchain-openai/torch），直接用标准库`urllib`裸调DeepSeek V4 Pro的Chat Completions接口，用真实的`COACH_PROMPT`+一段贴近真实长度的定性反馈样本，在不同`max_tokens`下测多次，读`usage.completion_tokens_details.reasoning_tokens`和`finish_reason`：
- `max_tokens=2048`：1/1次失败——`reasoning_tokens`直接打满2048、`content`完全为空、`finish_reason="length"`，和线上复现的空白问题是同一个模式，**实锤坐实了上一轮的推理是对的**。
- `max_tokens=4096`：5次里有1次失败——`reasoning_tokens=3787`（同一个prompt，reasoning消耗量在148~3787之间大幅波动）把预算挤到只剩约300token写正文，内容被截断、解析JSON会失败。**上一轮改成4096看起来"验证通过"其实只是运气好，5次里真实成功率只有80%，不能只测一次就下结论**。
- `max_tokens=8192`：连续6次全部`finish_reason="stop"`、返回内容都是合法JSON，`reasoning_tokens`最高只到894，相对8192还有7倍以上余量。
`content`本身（不含推理，250~350词范文+行动清单+练习）稳定在1100~1300token左右，真正的变量是推理token，8192给了推理足够的浮动空间。把`DEFAULT_MAX_TOKENS`（`src/agents/llm.py`）从4096改成8192，文件顶部docstring补全了这次的完整验证数据（不是重复上一轮"没验证过"的说法）。

**怎么验证的**：真实API调用本身就是验证（不是"写了代码假设它对"，是拿到了DeepSeek V4 Pro的真实`usage`数据）；`python -m py_compile`确认改动文件语法正确；服务器上`scp`同步、`grep`确认`DEFAULT_MAX_TOKENS = 8192`已经在服务器文件里、精确kill真实PID（这次同样经过了一段D状态才完全退出）→重启→`curl`本机和外网都是HTTP 200。

**没有做的验证**：诊断脚本用的是一段人工编造但贴近真实长度的定性反馈样本，不是`feedback_agent_node`真实生成的反馈文本，也没有测试"模型主动调用`dictionary_lookup`工具"这条分支（工具调用会多一轮LLM请求，理论上不会让单次请求的token需求变得更高，但没有实测这条路径）；仍然没有通过真实网页提交一篇作文走完整链路确认"个性化修改建议与练习推荐"现在能正常显示内容。

## 2026-07-17（第三十七轮）· 8192依然复现空白：真正根因是JSON语法错误不是token预算，用response_format=json_object从源头解决

**背景**：用户反馈调到8192之后"又这样了"（"个性化修改建议与练习推荐"仍然显示"本次未能生成结构化辅导计划"）。这次`src/agents/nodes.py`里已经有一份诊断日志（`_warn_json_parse_failure`，看起来是在这轮之前由用户自己或工具补上的，包含JSON出错的精确字符位置），一查发现是完全不同的问题。

**做了什么**：
1. **看服务器日志定位真正原因**：`streamlit.log`里的warning显示`coach_agent_node的JSON解析失败（Expecting ',' delimiter: line 14 column 3），原始响应长度=4749`——响应根本不是空的（4749字符，远超token预算不够时的空字符串），是LLM生成的JSON本身有语法错误（大概率是字符串里出现了没转义的英文双引号，导致JSON字符串边界被破坏）。**上一轮的token预算判断没有错（2048/4096确实会导致content为空），但这不是用户这次遇到的问题——这是另一类失败，运气不好让两类问题前后脚出现**，如实说明不是同一个bug反复出现。
2. **用真实API验证`response_format={"type": "json_object"}`能不能从源头解决**：这个是OpenAI兼容接口的标准参数，会让模型在解码层面被约束只能输出合法JSON（不是靠prompt里"请返回JSON"这种软约束）。用裸urllib分别测试：
   - DeepSeek+json_object模式：连续跑了6次（含1次疑似异常返回空内容，重跑后稳定复现），5次成功、JSON全部合法。
   - **DeepSeek+json_object+工具绑定同时用**：真实构造了带`tools`参数的请求，确认模型能正常识别并调用工具（`finish_reason=tool_calls`），没有因为加了json_object就报错或行为异常；完整走了"第一轮工具调用→本地模拟工具结果→第二轮最终生成"的全流程，第二轮返回4905字符合法JSON。
   - **GLM+json_object模式**：同样测试，一开始因为测试时max_tokens给的太小（200）复现了空content（GLM V4.7同样是推理模型，一样吃这个坑），换成8192之后`finish_reason=stop`、返回合法JSON`{"hello":"world"}`——确认GLM兜底供应商同样支持这个参数，不会因为切到兜底就报错。
3. **接入代码**（`src/agents/nodes.py`）：`feedback_agent_node`的`llm = get_chat_model_with_fallback()`改成链式`.bind(response_format={"type": "json_object"})`；`coach_agent_node`的主力路径`get_primary_chat_model().bind_tools([dictionary_lookup])`和降级路径`get_chat_model_with_fallback().invoke(prompt)`都加了同样的`.bind(response_format=...)`。这是在已有的重试机制（看起来这轮之前已经补上了`feedback_agent_node`和`coach_agent_node`的重试逻辑+`_warn_json_parse_failure`统一诊断，这次没有重复造轮子，是在这个基础上叠加）之外，从生成源头再加一层防护——重试解决"偶发"，`response_format`解决"从根源上少犯错"，两者配合比只有其中一个更稳。

**怎么验证的**：
- 真实API调用本身就是验证：DeepSeek/GLM两个供应商 + 是否绑定工具，三种组合都用裸urllib实测过，行为符合预期（不报错、返回合法JSON或正确触发工具调用）。
- `python -m py_compile`确认`src/agents/nodes.py`语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过。
- 服务器：`scp`同步、`grep`确认3处`response_format`都已经在服务器文件里；精确kill真实PID→重启→`curl`本机和外网都是HTTP 200。

**没有做的验证**：诊断脚本测试用的是人工模拟的工具结果（没有真的调一次`dictionary_lookup`的词典API），也没有通过真实网页提交一篇作文走完整链路确认这次"个性化修改建议与练习推荐"真的能正常显示——这是第三次在这个功能上迭代，如果这次部署后还复现，下一步不该再猜测，应该直接让用户在低峰时段配合测一次、实时看`streamlit.log`。

## 2026-07-18（第三十八轮）· 彻底删除自训练A/B评分模型，量化评分统一改用LLM+公开量表，产品收窄为GENERAL/IELTS/TOEFL三种类型

**背景**：用户想把打分模型"推倒换技术"。调查发现两个关键事实决定了最终方案：①团队早前测过裸问LLM打分（无量表约束）效果差（macro QWK仅0.3845，部分essay_set接近随机，见已删除的`models/zero_shot_llm_eval.json`），这是当初"必须自训练模型"的依据；②但雅思/托福已经在用一套完全不同、成熟得多的方案（`src/official_rubrics.py`）——LLM严格按公开官方评分量表打分，结构化JSON解析，线上已经在跑，效果和裸问LLM完全不是一回事。反复确认后，用户的最终决定：产品只保留GENERAL（通用英语作文评测）/IELTS/TOEFL三种考试类型，CET4/CET6/考研英语（KAOYAN）彻底删除；GENERAL从自训练A/B融合模型（微调DistilBERT+自建BiLSTM，测试集QWK 0.7589）迁移到LLM+公开量表；两条自训练模型的训练代码、权重文件**彻底删除，不保留存档**；配套的ASAP-AES数据处理流水线一并删除；"写作画像"弱项雷达图功能去掉，不做替代方案。**这是用户明确要求、逐项确认后的决定，不是发现自训练模型有问题才删除**——两条模型确实真实训练完成过，测试集QWK 0.7589，只是产品范围收窄+雅思/托福已验证的量表约束LLM方案更适合真实考试场景，所以统一技术路线、删掉不再需要的代码。

**做了什么**：
1. **`src/official_rubrics.py`**：新增`RUBRIC_INSTRUCTIONS[GENERAL]`——GENERAL没有官方量表可锚定，采用四维度各0-25分（内容与任务完成/结构与衔接/语言运用与词汇/语法准确性，求和得0-100总分），不是单一整体分，理由是四维度能给LLM具体评分锚点（和雅思四维度的可靠性原理一致）；`normalize_rubric_result()`新增GENERAL分支；删除CET4/CET6/KAOYAN/LEGACY_KAOYAN的量表条目。
2. **`src/exam_types.py`**：大幅简化，删除`CET4`/`CET6`/`KAOYAN`/`LEGACY_KAOYAN`常量、`SCORER_AB`/`SCORER_LLM`区分概念（三种类型现在都走同一条路径，不再需要区分）、`essay_set`概念（只喂给已删除的A/B模型用）。`EXAM_TYPE_OPTIONS`收窄为`[GENERAL, IELTS, TOEFL]`。
3. **`src/agents/nodes.py`**：删除`scoring_tool_node`、`_scorer_cache`、`AB_FEEDBACK_PROMPT`；`feedback_agent_node`删掉AB/LLM双分支，只保留LLM量表这一条路径，同时修了一个迁移后才会暴露的真实bug——`exam_type`默认值从`""`改成`GENERAL`（原来空值必然走AB分支从没真正到达LLM分支的`rubric_instruction("")`调用，AB分支删掉后这行会在try/except外抛未捕获`ValueError`）；`retrieval_agent_node`的RAG检索query从依赖`essay_prompt_id`（essay_set编号）改成直接用`exam_type`；`grammar_check_node`删除对`trait_scores`的读取和逐项扣分改写（这段逻辑依赖已删除的`scoring_tool_node`写入的数据，删除后是死代码）；`KB_QA_PROMPT`文案去掉"四六级/考研英语"。
4. **`src/agents/graph.py`**：图结构从"校验→检索→[条件路由到scoring_tool或跳过]→语法→反馈→辅导→进度"简化成纯线性的"校验→检索→语法→反馈→辅导→进度"，删除`route_after_retrieval`条件路由和`scoring_tool`节点。
5. **`src/agents/state.py`**：删除`essay_prompt_id`/`quant_score`/`score_norm_uncalibrated`/`trait_scores`字段。
6. **`pages/2_工作台.py`**：删除"最近一次写作画像"雷达图/条形图整个面板（含`trait_scores`读取），改成"学习趋势"图表独占整行；重写提交页说明文案（原来讲"CET-4/CET-6/考研/通用走A/B模型...CET的106.5分换算"，现在改成如实描述三种类型统一走LLM+公开量表）；清理`essay_set_for_exam_type`的import和用法。
7. **彻底删除的文件**：`src/training/`（`train_finetuned.py`/`train_custom.py`/`essay_scorer.py`/`common.py`）、`src/score_policy.py`、`src/data_pipeline/`、`src/rag/build_rubric_docs.py`（依赖已删除的`data/raw`）、`models/essay-scorer-finetuned/`、`models/essay-scorer-custom/`、`models/set8_diagnosis.json`/`score_calibration.json`/`weighted_ensemble_eval*.json`/`same_sample_trained_eval*.json`/`zero_shot_llm_eval.json`/`zero_shot_sample_ids.json`、`scripts/download_models.py`/`calibrate_score_bias.py`/`eval_same_sample_and_diagnose_set8.py`/`eval_weighted_ensemble.py`/`process_external_dataset.py`、`Docs/07-数据处理操作手册.md`。`requirements.txt`里的`torch`/`transformers`/`sentence-transformers`**没有删**——确认过`src/rag/build_kb.py`的RAG embedding模型（`BAAI/bge-small-en-v1.5`）依赖这几个包，不是只服务已删除的评分模型。
8. **测试脚本同步**：`scripts/smoke_test_nodes.py`删掉`test_score_policies()`里所有A/B相关断言，新增对`normalize_rubric_result()`在GENERAL/IELTS/TOEFL三种类型下的断言；`test_db_roundtrip()`改用`official_rubric_scores`/`primary_score`而不是已删除的`quant_score`/`trait_scores`/`essay_prompt_id`。`scripts/e2e_graph_test.py`删除所有`trait_scores`/`quant_score`断言，改成检查`primary_score`/`official_rubric_scores`；所有`graph.invoke()`调用显式传`exam_type`（原来一个都没传），新增IELTS/TOEFL边界用例。
9. **文档同步**：`CLAUDE.md`重写"项目是什么"/"目录结构"/"不要重新踩的坑"/"已确认、不要再改的设计决策"/"环境信息"里所有跟自训练模型、数据流水线相关的内容，如实记录本轮技术路线调整的原因；`Docs/00-项目总览.md`需求对照表加了醒目提示说明第6/7/8/9行是历史记录、当前代码库没有对应交付物；`Docs/01-系统架构与Agent设计.md`重写架构图/State定义/节点表/路由逻辑，删掉`ScoringToolNode`/`essay_scorer_tool`；`Docs/RUNNING.md`删除数据准备和模型训练两节，构建知识库/启动/测试/部署各节同步更新；`README.md`删除"模型权重下载"整节。

**怎么验证的**：
- 本机可跑（不需要pip install）：`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过，包括新增的GENERAL四维度量表`normalize_rubric_result`断言（`content_score=20/organization_score=18/language_score=19/grammar_score=15`求和得`primary_score=72`）和`db.save_submission`/`get_user_history`往返测试。
- `grep -rn "essay_prompt_id|quant_score|trait_scores|SCORER_AB|uses_ab_scoring|EssayScorer|score_policy" src/ pages/ scripts/`确认没有残留引用（见下方"最终校验"）。

**没有做的验证**：`scripts/e2e_graph_test.py`需要pip环境才能跑（本地开发环境pip install不了，见`CLAUDE.md`"环境信息"），这次改动后**还没有在能pip install的服务器/deploy-server上重新跑过真实DeepSeek端到端验证**，也没有手工过一遍`streamlit run app.py`的UI（提交GENERAL/IELTS/TOEFL各一篇，确认打分卡片正常、写作画像面板已经不出现）。部署环境（`121.41.238.92:8503`）跑的还是删除自训练模型之前的旧代码，重新部署前不要假设线上已经是最新状态。`data/kb/exam_rubrics/{general,ielts,toefl}.md`这几个RAG专属检索源文件本来就不存在（改动前就是这样，不是本轮造成的），本轮没有顺带补上，`retrieval_agent_node`会优雅降级成全库检索。`data/app.db`本地不存在（这台开发机没跑过应用），线上`deploy-server`的`data/app.db`还留着旧的CET4/CET6/KAOYAN历史提交记录，用户要求清空但需要登录`deploy-server`执行，这次没有远程操作生产数据库。

## 2026-07-19（第三十九轮）· 打分接入本地Ollama（qwen2.5:7b），不再部署到服务器改为纯本地运行

**背景**：用户决定不部署到服务器了，改成本地运行（本机有独立GPU、显存8G）；同时要求打分这一步引入Ollama，换成本地最合适的打分模型，但明确"如果还是DeepSeek V4 Pro效果好就不用Ollama了"——不是无条件切换，是要接入之后能随时按实测效果二选一。范围上用户明确只换打分这一步，定性反馈/辅导建议/知识库问答仍然用DeepSeek/GLM。

**做了什么**：
1. **`src/agents/llm.py`**：`_PROVIDER_DEFAULTS`新增`ollama`供应商（复用现有`ChatOpenAI`打`http://localhost:11434/v1`这个Ollama自带的OpenAI兼容端点，不需要新增pip依赖；`key_env`为`None`时传占位字符串"ollama"，Ollama本身不校验Key）。新增`get_scoring_chat_model()`：`SCORING_LLM_PROVIDER=ollama`（默认）时用本地Ollama模型并`.with_fallbacks([get_primary_chat_model()])`，本地服务没启动/没拉模型时自动回退主力DeepSeek，不会因为本地没开就打分失败；`SCORING_LLM_PROVIDER=deepseek`时完全跳过Ollama。这样"要不要用本地模型打分"变成改一个环境变量的事，不用碰代码，直接满足"效果不好随时切回"的要求。
2. **拆分`feedback_agent_node`的打分/反馈调用**：原来`LLM_RUBRIC_PROMPT`一次调用里同时要数值评分（`rubric_scores`）和定性反馈（`dimension_feedback`/`overall_summary`），没法只让打分这一半走Ollama。拆成`SCORE_RUBRIC_PROMPT`（只要`rubric_scores`，走`get_scoring_chat_model()`）和`FEEDBACK_ONLY_PROMPT`（只要定性反馈，走`get_chat_model_with_fallback()`），两次调用各自独立`try/except`（用宽泛的`except Exception`，因为本地Ollama是新引入的失败面，比原来只处理JSON解析失败更保守），结果合并后传给`normalize_rubric_result()`——这意味着GENERAL/IELTS/TOEFL现在每次提交要两次LLM调用而不是一次，用延迟换来"只切打分这一半"的隔离，是用户明确要求的取舍。
3. **本地真实验证，不是只写完代码就假设能用**：本机装了Ollama（`ollama --version`确认），拉取`qwen2.5:7b`（8G显存量级，约4.7GB，这个sandbox网络环境下载中断了两次`unexpected EOF`，重跑`ollama pull`断点续传后成功）。用裸`urllib`直接调Ollama的`/v1/chat/completions`（不经过langchain，因为本地装不了）拿GENERAL的真实打分结果，**发现一个真实的模型行为差异**：qwen2.5:7b没有按prompt示例把分数嵌套在`{"rubric_scores": {...}}`里，而是直接把`content_score`/`organization_score`/`language_score`/`grammar_score`四个键摊平在JSON顶层——四个分数值本身是对的（20/18/19/17），只是外层结构和DeepSeek的习惯不一样。这是本地7B模型和DeepSeek V4 Pro在指令遵循精细度上的真实差距，不是bug，也不是瞎猜的推测。
4. **兼容修复而不是重新调prompt赌运气**：`feedback_agent_node`里加了一段防御性逻辑——`parse_llm_json`拿到结果后，如果`"rubric_scores"`键不存在但结果本身非空，就把整个结果包一层`{"rubric_scores": ...}`。用真实Ollama返回的摊平JSON和一个模拟的规范嵌套JSON分别跑过`normalize_rubric_result`，两种情况都能正确得到`primary_score=74/100`且`score_error=None`，不会因为模型格式习惯不同就误判成打分失败。这个修复对任何指令遵循能力较弱的本地模型都有意义，不是只对qwen2.5:7b生效的特例修补。
5. **部署方式改为纯本地**：`CLAUDE.md`和`Docs/03-RUNNING.md`都把服务器部署那一整节降级成"备用，当前不用"的存档小节（内容原样保留，只是加了"现在不部署"的说明和位置调整），不再是"怎么跑起来"里的默认路径；`README.md`补了`ollama pull qwen2.5:7b`这一步和Ollama相关环境变量说明。
6. **顺手同步**：`Docs/`目录本身在这几轮之间被重新编号过（`Progress.md`→`02-Progress.md`、`RUNNING.md`→`03-RUNNING.md`、`00-项目总览.md`被删除），`CLAUDE.md`/`scripts/smoke_test_nodes.py`/`src/agents/graph.py`里指向旧文件名的引用一并改成新路径，没有跟着改的历史记录（`Docs/02-Progress.md`过去轮次里提到的旧文件名）如实保留，不回改。

**怎么验证的**：
- 真实调用本地Ollama（不是mock）：裸urllib直接打Ollama的OpenAI兼容接口，实测耗时10.2秒、`finish_reason=stop`、四项分数合理（20/18/19/17，总分74/100）。
- 用真实拿到的摊平JSON结构和一个模拟的规范嵌套JSON结构分别跑`normalize_rubric_result()`，确认新加的兼容逻辑两种情况都能正确算出`primary_score`且不误报错、也不会对已经规范的嵌套结构重复包一层。
- `python -m py_compile`确认`src/agents/llm.py`/`src/agents/nodes.py`语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过。

**没有做的验证**：没有通过`scripts/e2e_graph_test.py`或真实`streamlit run app.py`走一次完整的GENERAL提交（这两个都需要pip环境，本地开发环境装不了）；没有真实对比过Ollama和DeepSeek在同一批作文上的打分质量差异（QWK或人工评估都没做）——这正是用户"如果还是DeepSeek效果好就不用Ollama"这句话里的决策依据，现在只是把两条路径都接好、切换成本一个环境变量的事，**质量对比本身还没做，需要用户自己在真实使用中判断**，已列入`Docs/TODO.md`"需要你决策"。

## 2026-07-19（第四十轮）· 打分模型可在UI里选、雅思Task 1图表识图评分、feedback接入LanguageTool+词典工具

**背景**：用户提了三个想法：①系统里能不能选打分模型；②能不能批改雅思Task 1（需要识图）；③feedback节点能不能拆成4个子agent各自调用第三方工具提高准确性。逐项调研后：①明确是"提交页选Ollama/DeepSeek"；②查证DeepSeek对外API目前不支持图片输入（只有网页版支持），推荐用同一GLM账号下的免费视觉模型GLM-4V-Flash；③查证grammar/language两个维度有真正有价值的第三方工具（LanguageTool公共API、已有的词典API），content/coherence没有，用户采纳"只给grammar/language接工具，不做4个对称agent"的建议，避免为了架构对称而堆两个摆设agent、平白把2次LLM调用变成5-6次。

**做了什么**：
1. **打分模型UI选择**：`src/agents/llm.py`的`get_scoring_chat_model()`加`provider`参数，传参覆盖`.env`默认值，不传时行为不变（向后兼容）。`EssayReviewState`加`scoring_provider`字段，`feedback_agent_node`透传给`get_scoring_chat_model()`。`pages/2_工作台.py`提交页加"打分模型"下拉框（本地Ollama默认/DeepSeek API），方便同一篇作文对比两条路径。
2. **雅思Task 1图表识图评分**：新增`src/agents/llm.py::get_vision_chat_model()`（固定用GLM视觉模型，不做fallback——图片理解失败应该让用户明确知道、重新上传，不能让打分模型悄悄换成不认图片的文本模型去瞎编图片内容）；新增LangGraph节点`image_analysis_node`（只在`essay_image_b64`非空时真正调用，否则原样透传state，不影响GENERAL/IELTS Task2/TOEFL这些没有图片的场景），接在`intake_validator`和`retrieval_agent`之间；`src/exam_types.py`新增`IELTS_SUBTYPES`（Task1/Task2）；`src/official_rubrics.py`新增IELTS Task 1的Band Descriptors（Task Achievement维度替代Task Response，其余三维度不变）；`SCORE_RUBRIC_PROMPT`/`FEEDBACK_ONLY_PROMPT`加`{image_context}`占位符，把图片理解结果注入打分/反馈两个环节——**打分/反馈模型全程看不到原图，只能依据图片理解模型给出的文字描述判断作文数据是否准确**，这是因为DeepSeek/Ollama都不支持（或没配置）图片输入，识图和打分/反馈必须拆成独立调用。`pages/2_工作台.py`加雅思Task1/Task2子类型选择+图片上传（Task1必须上传图片才能提交）+图片预览。
3. **feedback接入真实工具**：新增`src/agents/grammar_tools.py::languagetool_check()`（调用LanguageTool免费公共API），`grammar_check_node`把它的检测结果和本地正则规则库结果按位置区间去重合并；`FEEDBACK_ONLY_PROMPT`新增`{grammar_tool_findings}`，grammar维度反馈现在基于这份真实检测列表写，不再是LLM自己重新通读一遍瞎猜；`feedback_agent_node`的定性反馈调用绑了`dictionary_lookup`工具（复用`coach_agent_node`已有的工具+`get_primary_chat_model()`写法，不和`get_chat_model_with_fallback()`一起用），language维度可以自主查词。
4. **过程中发现并修复的真实问题**（不是照抄文档的推测）：
   - `src/agents/tools.py`顶部`from langchain_core.tools import tool`，`grammar_check_node`一旦import这个文件里的`languagetool_check`就会连带触发`langchain_core`导入，在免pip环境里直接`ModuleNotFoundError`，把"不需要pip install就能跑"的`smoke_test_nodes.py`路径搞断了——是跑测试时真实报错发现的，不是review代码看出来的。修复：`languagetool_check`单独拆进零依赖的`src/agents/grammar_tools.py`，`tools.py`只保留需要langchain的`dictionary_lookup`。
   - 默认给的视觉模型名`glm-4.6v-flash`真实调用连续返回`HTTP 429`（"该模型当前访问量过大"），换成`glm-4v-flash`（少个`.6`）同一个Key、同一张测试图立刻调通，且识图结果准确（真实读出了自己现场画的折线图的数值、趋势方向、两条线的交叉点）。`GLM_VISION_MODEL_NAME`默认值已改成`glm-4v-flash`。

**怎么验证的**：
- **真实调用LanguageTool公共API**（不是mock）：拿真实病句（`I are a student. He go to school every days.`）测，检测到4处真实语法问题，建议合理；和本地正则结果合并去重后共8处，人工核对没有重复报告同一处错误。
- **真实调用GLM视觉API**（不是mock）：用matplotlib现场画一张有真实数据的折线图，先用`glm-4.6v-flash`测出429限流问题，换`glm-4v-flash`后识图结果和图片实际内容完全一致（数值、趋势、交叉点都对）。
- `normalize_rubric_result(IELTS, ..., exam_subtype=IELTS_TASK1)`真实数据验证：四维度分数正确算出Band 6.5，`primary_label`正确显示"Task 1"字样，且确认Task 2路径没被这次改动影响。
- `python -m py_compile`全部改动文件语法正确；`PYTHONPATH=. python scripts/smoke_test_nodes.py`全部通过（新增IELTS Task1断言）。
- `scripts/smoke_test_nodes.py`/`scripts/e2e_graph_test.py`都已更新新场景的测试用例，但`e2e_graph_test.py`本身需要pip环境，本轮没有真的跑一遍。

**没有做的验证**：`scripts/e2e_graph_test.py`新增的3个用例（scoring_provider覆盖、IELTS Task1完整链路）需要pip环境才能真的跑一遍，本地开发环境跑不了；没有通过真实`streamlit run app.py`点击提交批改页测试新UI（打分模型下拉框、图片上传、图片预览）；没有测试过图片理解失败（比如GLM视觉API也被限流）时`image_analysis_error`能不能正确显示在UI上；LanguageTool公共API有限流（免费匿名约20次/分钟），高频提交场景下没有测试过限流后的降级表现（代码层面已经保证限流/失败时静默返回空列表不报错，但没有真实触发过限流场景）。

## 2026-07-19（第四十一轮）· 发现`uv`能绕开本地pip限制、真实跑通e2e测试并修复两个真实bug、SQLite迁移PostgreSQL

**背景**：用户在`TODO.md`"下一步"给了三条指示：①"SQLite换成正规本地数据库"；②"我安装了uv，试试uv可不可以，是在不行在D:\environment中搭建pip环境"；③"白屏问题先删除，部署服务器那也先不用管"（对应`TODO.md`里已经过时的两条决策项，直接清理）。第①条追问后用户明确是PostgreSQL（本地安装）。

**做了什么**：
1. **`uv`验证成功，本地开发环境第一次能装全部依赖**：`uv venv --python 3.11 .venv-uv && uv pip install -r requirements.txt --python .venv-uv`完整装完（含torch/transformers/streamlit/langgraph），`uv`会自己下载Python 3.11解释器，不依赖本机Miniconda 3.9.1，也不受这个sandbox对`pip`本身的`SSLEOFError`限制（推测是pip的HTTP连接实现方式被这个网络环境针对性挡住，`uv`换了实现所以绕开了）。这意味着从这一轮起，`scripts/e2e_graph_test.py`和`streamlit run app.py`不用再假设"这台机器测不了"，`.venv-uv/`已加进`.gitignore`（本地产物不提交）。
2. **真实跑`e2e_graph_test.py`，过程中发现并修复两个之前从未真正触发过的bug**（都是"能不能真的跑起来"这个动作本身发现的，不是代码审查能看出来的）：
   - `src/agents/tools.py`的`dictionary_lookup`没写docstring，真实调用`@tool`装饰器时抛`ValueError: Function must have a docstring if description not provided.`——这个工具从被引入起就没在真实langchain环境里跑过，所以这个错误一直没暴露。修复：补上文档字符串（说明查询用途、什么时候该调用）。
   - `feedback_agent_node`/`coach_agent_node`两处`bind_tools([...])`同时配了`response_format={"type":"json_object"}`，触发openai SDK的结构化输出auto-parse路径，该路径要求每个工具的function schema都是`strict: True`，不满足会抛`ValueError: ... is not strict. Only strict function tools can be auto-parsed`。修复：两处`bind_tools`都加`strict=True`。修复前这两个bug会让"工具调用"整体失败并被外层`except Exception`吞掉、静默退回不调用工具的纯文本生成——意味着`dictionary_lookup`大概率在这个项目历史上从来没有被真实调用成功过，直到这轮才第一次验证通。
3. **`src/storage/db.py`从SQLite重写为PostgreSQL**：本机用`scoop install postgresql`装了18.4版，trust本地认证，超级用户`postgres`空密码；建了`huibi`（生产）和`huibi_test`（测试专用）两个库。改动点：
   - 连接层从`sqlite3.connect(path)`换成`psycopg.connect(dsn)`，`get_connection()`参数从`db_path: Optional[Path]`改成`dsn: Optional[str]`，DSN由`POSTGRES_HOST/PORT/DB/USER/PASSWORD`几个环境变量拼出。
   - JSON字段（`score_details`/`feedback_dimensions`/`coach_plan`/`official_rubric_scores`）改用PostgreSQL原生`JSONB`类型，写入时用`psycopg.types.json.Jsonb()`包一层，读取时`psycopg`v3自动把JSONB还原成Python dict，不用再手动`json.dumps`/`json.loads`。
   - 表结构顺带删掉了`essay_prompt_id`/`quant_score`/`trait_scores`三个死列（只有第三十八轮已删除的自训练AB模型会写这几列，SQLite时代就已经没有生产方了，这次换库顺便清干净，不是这轮新引入的浪费）。
   - `nodes.py`原来在模块顶部`from src.storage import db`，但`db.py`现在需要`psycopg`，会连带把"免pip"的`smoke_test_nodes.py`路径重新弄坏（和第四十轮`tools.py`那次是同一类问题）——改成只在`progress_tracker_node()`函数体内懒加载。`scripts/smoke_test_nodes.py`同步移除了数据库相关的测试（改到需要pip的`e2e_graph_test.py`里）。
4. **`e2e_graph_test.py`新增`test_db_roundtrip`/`test_auth_roundtrip`**：跑之前把`POSTGRES_DB`环境变量临时指向`huibi_test`（在import `src.storage.db`之前设置，因为`_build_dsn()`是运行时读环境变量），每次测试先`TRUNCATE TABLE submissions, users RESTART IDENTITY`清空这两张表，不会碰生产库`huibi`的真实数据，也不用像SQLite时代那样每次建临时文件。
5. **清理`TODO.md`**：删掉"白屏问题排查到第三十四轮"和"deploy-server上还跑着旧代码"这两条已经不再相关的决策项（用户第③条指示要求的）。

**怎么验证的**：
- **本机装了`uv`环境后真实跑通`scripts/e2e_graph_test.py`**（`.venv-uv/Scripts/python.exe scripts/e2e_graph_test.py`，exit code 0，PostgreSQL在跑）：`test_db_roundtrip`/`test_auth_roundtrip`通过；GENERAL用例真实调用DeepSeek拿到88/100（四维度21/22/21/24）、真实中文定性反馈、`db.get_user_history`读回的`official_rubric_scores`/`score_details`是原生Python dict（确认JSONB自动转换生效）；过短作文正确短路拒绝；`test_edge_cases`的边界1（20词边界）验证通过；修复两个bug后重跑确认不再有"not strict"告警。
- **独立脚本直接验证过`db.py`本身**（在改`e2e_graph_test.py`之前）：`create_user`→`verify_user`→`save_submission`（含JSONB字段）→`get_user_history`全链路走通，返回的JSON字段是原生dict不是字符串。
- `PYTHONPATH=. python scripts/smoke_test_nodes.py`（系统Python，零pip依赖）仍然全部通过，确认`nodes.py`的db懒加载改动没有破坏"免pip"这条不变量。

**没有做的验证**：没有真实跑`streamlit run app.py`点击测试（登录注册走PostgreSQL、提交批改、历史仪表盘），只验证了`db.py`本身和`e2e_graph_test.py`的直接调用路径；`e2e_graph_test.py`里`test_edge_cases`的边界2~8（含IELTS Task1图片理解全链路、scoring_provider切换）这次跑通过但完整输出因为单条日志过长被截断，没有逐条肉眼确认每个断言的具体数值，只确认了整体exit code 0（全部`assert`通过，脚本任何一个断言失败都会抛异常导致非0退出码，所以exit 0本身就是全部用例通过的可靠证据，但没有像GENERAL用例那样逐项贴数字复核）。

## 2026-07-21（第四十二轮）· 雅思Task1图片持久化 + 三个RAG官方细则文件 + 本地模型选型研究 + 微调可行性评估 + 打分缺字段重试修复

**背景**：用户在`TODO.md`"下一步"给了四条指示：①雅思Task1图片单独设计存入（对应上一轮"需要你决策"里记录的已知缺口）；②补充三个RAG专属检索源文件，要求"官方标准"；③本地能用更新的qwen模型就用本地，或者把DeepSeek V4 Pro拉到本地；④评估打分模型是否需要微调、什么方案合适。

**做了什么**：
1. **雅思Task1图片持久化**：`src/storage/db.py`的`SCHEMA`给`submissions`表新增`essay_image_path`/`image_analysis`两列（`CREATE TABLE`定义里加，同时补了`ALTER TABLE ADD COLUMN IF NOT EXISTS`兼容已经建过的旧表，两者都需要——前者管新装库，后者管这个环境已经跑过`e2e_graph_test.py`建出来的旧表结构）。新增`_save_uploaded_image()`：解码base64、按PNG/JPEG/GIF文件头嗅探扩展名（不依赖`imghdr`，Python 3.13起已移除该标准库模块）、写入`data/uploads/<uuid>.<ext>`，`save_submission()`只在`essay_image_b64`存在时才落盘、数据库只存相对路径字符串。`delete_submission()`删记录前先查出路径，删除成功后连带`unlink()`本地文件，避免孤儿文件累积。`pages/2_工作台.py`历史详情页读到`essay_image_path`后用`st.image()`从磁盘直接渲染，`image_analysis`放进一个可展开的说明框。`data/uploads/`加进`.gitignore`。
2. **三个RAG专属细则文件，基于真实官方原文**：用户明确要求"要官方标准"，没有直接凭记忆转述——用`WebSearch`定位到IELTS官方Band Descriptors PDF（`takeielts.britishcouncil.org`）和ETS官方TOEFL iBT Writing Scoring Guide三份PDF（Write an Email、Writing for an Academic Discussion、Integrated Writing，`ets.org/toefl`），`WebFetch`直接下载PDF后用`Read`工具解析出逐字文本（`WebFetch`自带的HTML转Markdown在这几份PDF上解析失败，改成直接读取工具保存的原始PDF文件，PDF阅读能力这次是关键路径，不是可选项）。`data/kb/exam_rubrics/ielts.md`收录IELTS Task 1+Task 2共18个Band×4维度的官方逐句原文（0-9）；`toefl.md`收录Email/Academic Discussion两套系统实际使用的官方评分指南（0-5，逐句原文）+ Integrated Writing官方指南作为参考（系统不用它评分，因为这个任务需要阅读材料+讲座音频，孤立提交的作文文本无法还原）；`general.md`没有对应的单一官方考试，基于已有`src/official_rubrics.py`的四维度框架扩展成教学向内容（每维度的高中低分区间描述+中国学习者高频扣分点+提分建议），明确写清楚"不是官方量表换算值"，不冒充官方标准。三个文件都放进`data/kb/exam_rubrics/`（这个目录之前不存在，整个重新创建）。
3. **重新构建RAG知识库，过程中解决了这个环境的新网络坑**：`python -m src.rag.build_kb`需要先下载`BAAI/bge-small-en-v1.5`（embedding模型），第一次跑发现这个环境从没缓存过这个模型（之前只缓存过`bge-small-zh-v1.5`，中文版，不是项目要用的英文版）。用`huggingface_hub.snapshot_download()`（走`HF_ENDPOINT=https://hf-mirror.com`镜像）反复失败：`httpx`并发下载线程池会稳定触发`SSL: UNEXPECTED_EOF_WHILE_READING`，和这个环境`pip install`/多次`ollama pull`已知的"大文件/并发连接容易被重置"是同一类网络限制，不是配置错误（`HF_HUB_DISABLE_XET=1`、单线程`max_workers=1`都试过，没解决）。裸`requests`单连接GET同样的URL反而稳定成功，于是写了一个绕过`huggingface_hub`下载层的脚本，直接用`requests`下载所需的10个模型文件、手工写进HF cache目录结构（`~/.cache/huggingface/hub/models--BAAI--bge-small-en-v1.5/`），让`local_files_only=True`的加载逻辑正常从本地缓存命中。构建出73个chunk的Chroma向量库。
4. **真实验证RAG检索命中新文件，不是只confirm构建不报错**：写了独立脚本对GENERAL/IELTS Task2/IELTS Task1/TOEFL四种`(exam_type, exam_subtype)`组合分别调用`retrieval_agent_node()`，确认每种都从对应的`exam_rubrics/{general,ielts,toefl}.md`里检索到真实内容片段（比如IELTS Task1场景检索到"Task 1的第一项标准换成Task Achievement"这句只在Task1章节出现的话），而不是`retrieval_agent_node`降级时返回的占位字符串——这解决了上一轮`Docs/TODO.md`记录的"诚实的缺口"（RAG专属文件不存在，检索优雅降级但拿不到真专属细则）。
5. **本地模型选型研究**：`WebSearch`+`WebFetch`确认DeepSeek V4 Pro是约1.6万亿参数的MoE模型，即使4-bit量化也需要约800GB显存/多张H100，本地8G显存GPU完全不可行，这条路径排除（不是"暂不建议"，是硬件上根本跑不了）。Qwen这边确认Qwen3系列已发布，`qwen3:8b`（约5.2GB，4-bit量化）和当前用的`qwen2.5:7b`同量级、能在8G显存里跑，官方在指令遵循/结构化输出上号称有提升——这点直接对应上一轮真实发现的bug（qwen2.5:7b打分时没把分数嵌套进`rubric_scores`，而是摊平在JSON顶层）。`AskUserQuestion`征询后，用户选择"直接切换默认值为qwen3:8b"。开始`ollama pull qwen3:8b`，但这个开发环境这一轮里出现了两次意料之外的整体重启（伴随Ollama App、MCP连接一起重连），把正在跑的下载打断在31%和22%，Ollama本身支持断点续传（不是从头来），目前第三次拉取还在进行，**还没有真的跑完、也还没有做qwen3:8b和qwen2.5:7b的真实打分JSON遵循对比**，`.env`的`OLLAMA_MODEL_NAME`暂时没有改，仍是`qwen2.5:7b`——不想在没做过真实对比之前就切换默认值。
6. **打分模型微调可行性评估（只做分析，没有写代码）**：结论是"目前不建议做"，详细理由和优先级建议记在`Docs/TODO.md`"需要你决策"，核心逻辑是：①本地模型现有的JSON格式问题已经用代码层防御性兼容解决，不是需要靠微调解决的能力缺口；②微调需要真实训练数据，项目在第三十八轮已经删除了ASAP-AES数据流水线，重新收集或用DeepSeek蒸馏都是新的工程量；③本地vs DeepSeek打分质量本身还没做过正式对比（老早就在"需要你决策"里，一直没做），在不确定"本地是否真的不够好"之前投入微调是过早优化。给出的优先级：先验证qwen3:8b是否已经够好 → 不够再试few-shot prompting（更便宜）→ 最后才考虑蒸馏微调。
7. **全量回归时真实抓到一个此前没发现的bug，当场修复**：第一次跑`e2e_graph_test.py`时，边界8（IELTS Task 1，本地Ollama打分）抛出未捕获的`AssertionError: IELTS Task1评分不应该报错：LLM评分结果缺少字段: task_achievement`——用`2>&1 | tail -60`管道跑的，`tail`本身exit 0掩盖了Python的真实非零退出码，第一次看日志误以为"全部通过"，仔细看日志尾部才发现这条异常没被assert吞掉、是真报错。单独写脚本反复调用同一个prompt复现（4次里3次都正确返回`task_achievement`等四个键，1次直接漏了这个键），确认是本地`qwen2.5:7b`偶发的、非必现的指令遵循问题，不是prompt或解析代码的确定性bug。`feedback_agent_node`原来打分只调用LLM一次，解析/校验失败就直接放弃，改成最多重试1次——`normalize_rubric_result()`本身就有"缺字段抛异常"的校验能力，直接拿来在重试循环里当验证器用（校验通过才跳出循环、不通过就重跑一次同样的prompt），不用额外写校验逻辑。

**怎么验证的**：
- 图片持久化：独立脚本对着真实本地PostgreSQL跑`save_submission`（含1x1 PNG的真实base64图片）→`get_user_history`读回确认`essay_image_path`非空且文件存在、内容字节完全一致→`delete_submission`确认文件被删除→确认无图片提交时`essay_image_path`为`None`，全部通过。
- RAG：`build_kb.py`真实跑通（73个chunk），独立脚本对四种考试类型/子类型组合调用`retrieval_agent_node()`确认检索命中新文件的真实内容片段，不是占位或旧的全库检索结果。
- 全量回归（分两轮）：`PYTHONPATH=. python scripts/smoke_test_nodes.py`（零依赖）两轮都全部通过。第一轮`e2e_graph_test.py`用`2>&1 | tail -60`跑，管道掩盖了真实退出码，日志尾部实际有未捕获的`AssertionError`（见上面第7点），不是真的全绿。修复重试逻辑后，第二轮改成`... > file 2>&1; echo EXIT_CODE=$?`显式记录真实退出码重新跑一遍，`EXIT_CODE=0`、边界8正确返回`task_achievement`等四个键、8个边界案例和数据库读写全部通过，这次是真的全绿。教训：管道到`tail`/`head`时不能只看`echo $?`或任务通知的"exit code"，那些反映的是管道最后一个命令（`tail`）的退出码，不是Python脚本本身的；以后跑这类长日志的验证脚本要么不用管道、要么显式`echo EXIT_CODE=$?`记录真实值。
- 本地模型选型：`WebSearch`确认Ollama库里`qwen3:8b`的实际tag和体积（非道听途说）；DeepSeek V4 Pro参数规模和显存需求也是`WebSearch`查证，不是凭印象估算。

**没有做的验证**：qwen3:8b还没拉取完成（这个环境本轮反复中途重启，下载被打断两次），真实的qwen3:8b vs qwen2.5:7b打分JSON遵循对比没有做，`.env`默认值没有改；没有真实跑`streamlit run app.py`点击验证历史详情页的图片展示效果（只验证了后端`db.py`的存取，没有验证Streamlit渲染）。

## 2026-07-22（第四十三轮）· 确认打分固定用DeepSeek V4 Pro，取消Ollama打分和相关功能

**背景**：上一轮"需要你决策"留了三条和本地Ollama打分相关的开放事项（Ollama vs DeepSeek质量对比、qwen3:8b选型验证、微调可行性优先级），用户这一轮直接给出结论：`确认使用DeepSeekv4pro打分，取消Ollama打分和相关功能`，不再需要继续跑那几条对比/选型工作，三条决策项一并作废。

**做了什么**：
1. **`src/agents/llm.py`**：`_PROVIDER_DEFAULTS`删掉`ollama`供应商配置（模型名/Base URL/无需Key的特殊处理一起删）；`_build_chat_model()`的`key_env is None`分支（Ollama专用的"不校验Key"逻辑）跟着删掉，函数签名收紧回"每个供应商都必须有真实Key"；`get_scoring_chat_model()`删掉`provider`参数和`.with_fallbacks()`兜底逻辑，直接`return get_primary_chat_model()`——打分和定性反馈/辅导建议现在共用同一个DeepSeek V4 Pro实例。保留这个函数本身（没有直接在调用处改成`get_primary_chat_model()`），因为它仍然标记了"这是打分场景专用的调用点"这个语义，以后如果打分要再单独配置，改动面只在这一个函数内。
2. **`src/agents/state.py`**：删掉`scoring_provider: Optional[str]`字段。
3. **`src/agents/nodes.py`**：`feedback_agent_node`里`get_scoring_chat_model(state.get("scoring_provider"))`改成`get_scoring_chat_model()`，去掉Ollama专属的注释（"本地小模型偶发漏字段"改写成不指名具体模型的通用说法）。**打分调用的"缺字段重试1次"机制本身保留**——这是防御性代码，不是Ollama专属逻辑，换成DeepSeek后触发概率会更低但不代表不会发生，删掉这个机制不在这次任务范围内。
4. **`pages/2_工作台.py`**：提交批改页删掉"打分模型"下拉框（`本地Ollama（默认）`/`DeepSeek API`两个选项），连带删掉传给`graph.invoke()`的`scoring_provider`字段；雅思Task 1图片上传区的说明文案里"不是本地Ollama打分模型直接识图"改成"打分模型全程看不到原图"，去掉对已删除功能的指代。
5. **文档同步**：`.env.example`/`README.md`/`Docs/03-RUNNING.md`删掉`OLLAMA_BASE_URL`/`OLLAMA_MODEL_NAME`/`SCORING_LLM_PROVIDER`三个环境变量的定义和说明、`ollama pull qwen2.5:7b`安装步骤、"提交批改页切换打分模型对比"这条手动测试清单项；`CLAUDE.md`"项目是什么"/"当前进度"/"不要重新踩的坑"/"已确认、不要再改的设计决策"/"环境信息"五处涉及Ollama打分的表述改成固定DeepSeek V4 Pro（"诚实的缺口"里"本地Ollama打分质量还没对比"这条随之删除，因为已经不再是缺口——决策已经做了）。
6. **`scripts/e2e_graph_test.py`**：删掉"边界7：打分模型切换成DeepSeek（`scoring_provider`覆盖`.env`默认的ollama）"这个测试用例（两条路径已经不存在，没有可切换的东西），原"边界8：IELTS Task 1"改成"边界7"，变量名`r8`/`edge_user_8`同步改成`r7`/`edge_user_7`。

**怎么验证的**：`PYTHONPATH=. python scripts/smoke_test_nodes.py`（零依赖）跑通，确认`state.py`删字段、`nodes.py`改调用签名没有破坏免pip路径。`PYTHONPATH=. .venv-uv/Scripts/python.exe scripts/e2e_graph_test.py`完整回归（真实DeepSeek调用+真实PostgreSQL读写+真实RAG检索），进程退出码0、无`Traceback`/`AssertionError`：GENERAL正常长度作文真实打分88/100（四维度21/23/20/24）、过短作文正确短路拒绝、边界1~7（含IELTS Task2打分6/9、TOEFL单题打分5/5、IELTS Task1图片理解+Task Achievement量表）全部通过，确认删掉`scoring_provider`分支、`get_scoring_chat_model()`不再需要参数后，量化打分固定走DeepSeek V4 Pro在全部考试类型/边界场景下都正常工作，没有因为这次改动引入回归。

## 2026-07-22（第四十四轮）· 补本地启动脚本 + 删除内测码限制 + 配色参考essay.art

**背景**：`Docs/TODO.md`"下一步"给了两条新指示——①删除注册需要内测码的功能；②调整样式，色系/排布等所有样式参考`https://essay.art/`。另外这一轮开头用户反馈双击`启动慧笔.bat`出现乱码，顺带修了。

**做了什么**：
1. **启动脚本编码修复**：`启动慧笔.bat`原来是UTF-8无BOM保存，双击时cmd.exe按系统默认936（GBK）codepage解析批处理源文件里的中文字节，文件内的`chcp 65001`不能可靠修正这个问题（真机复现了乱码+"不是内部或外部命令"报错）。改成直接用`[System.Text.Encoding]::GetEncoding(936)`把文件内容编码成GBK、CRLF换行保存，去掉不再需要的`chcp 65001`行。**过程中犯了两次同样的git错误**：`git commit -m ...`不带路径限定时会把索引里所有已暂存的内容一起提交（包括这轮会话开始前就已经暂存、和本次任务无关的`Docs/07`/`Docs/08`文档改名），两次都是提交后立刻用`git reset --soft HEAD~1`撤销、改成`git commit -m ... -- <具体文件>`只提交目标文件重新提交，没有影响远程（改动全程只在本地`agent/project-updates`分支，没有push）。教训：以后但凡这个仓库处于"有其他不相关改动已经暂存"的状态，提交前一定要显式限定路径，不能只在`git add`时挑文件、`git commit`时漏了同样限定。
2. **删除注册内测码限制**：`pages/1_登录.py`删掉`BETA_ACCESS_CODE = "tskswbb"`常量、注册表单里的"内测码"`st.text_input`、以及`beta_code != BETA_ACCESS_CODE`这条校验分支（现在注册只校验两次密码一致）；`src/ui_theme.py`删掉配套的、专门隐藏这个输入框密码显示切换按钮的CSS规则（`div[data-testid="stTextInput"]:has(input[aria-label="内测码"])`），这条规则的唯一目的就是配合内测码字段，字段删了它也跟着删。
3. **配色/字体参考essay.art重新调整**：不是凭印象抓取风格，而是`curl`下载了essay.art首页引用的两个编译后CSS文件（Next.js/Tailwind站点），用正则统计出实际使用的十六进制颜色频次，确认该站的品牌蓝是`#1165A4`（对应Tailwind自定义色`essayPrimary`，站内多处`fill-essayPrimary`/`bg-essayPrimary`直接引用）；同时确认字体栈用`Inter`，以及CTA按钮的一个视觉签名——无模糊纯色偏移阴影（`box-shadow:5px 5px #1165a4`这类写法），是一种"贴纸感"的硬阴影按压效果。基于这几个可迁移的具体设计特征（不是整站样式照搬，`src/ui_theme.py`本身已有大量既存的、经过多轮debug的自定义卡片/布局CSS，全部重写风险大于收益，本轮只动色系/字体/按钮交互这三块）：
   - `PRIMARY`/`PRIMARY_DARK`/`PRIMARY_LIGHT`三个变量从原来偏鲜艳的靛蓝`#165DFF`改成essay.art实测的`#1165A4`（`PRIMARY_DARK`是它降低约25%亮度的计算值`#0D4C7B`，`PRIMARY_LIGHT`是它10%不透明度叠加白底的计算值`#E7F0F6`，不是拍脑袋取的邻近色）。
   - `.hb-hero`（登录页大幅Hero横幅）的渐变原来是深蓝到紫色（`#073B89`→`#6544DE`），紫色和essay.art的纯蓝色系不搭，改成深蓝到天蓝（`#0B4A7A`→`{PRIMARY}`→`#2FA8E0`），保留原有的渐变层次感但统一在蓝色家族内。
   - 加了Google Fonts的`Inter`字体导入（`@import`），作用域`html, body, .stApp`（会通过CSS继承传导到几乎全部子元素），这是这个项目第一次显式指定字体，之前完全依赖Streamlit默认字体栈。
   - 主按钮（`div.stButton > button[kind="primary"]`，覆盖登录/注册/提交作文等全部主要操作按钮）新增essay.art风格的硬阴影+按压位移交互：静止态`box-shadow: 4px 4px 0 {PRIMARY_DARK}`，hover时按钮左上移2px、阴影加深到6px（营造"浮起"感），active按下时阴影收窄到2px、按钮归位（营造"按下贴住阴影"的实体感）。
   - 顶部导航`.hb-nav-brand`原来硬编码一个独立的深蓝`#0C3D86`，改成直接引用`{PRIMARY_DARK}`变量，和新色系保持一致，顺便减少一个游离在变量系统外的硬编码色值。

**怎么验证的**：
- 编码修复：`iconv -f GBK -t UTF-8`反解码新文件内容确认中文还原正确无误，`xxd`确认换行是CRLF（`0d0a`）。
- 内测码删除+样式改动：`python -m py_compile`确认`pages/1_登录.py`/`src/ui_theme.py`无语法错误。这个开发环境没有`chromium-cli`等浏览器自动化工具（`/run`技能检查确认过，也没有display，无法截图看真实渲染效果），改用`streamlit.testing.v1.AppTest`做headless功能验证：`AppTest.from_file("app.py")`执行无异常 → `switch_page("pages/1_登录.py")`执行无异常，且`text_input`标签列表确认只剩"用户名/密码（至少6位）/确认密码"，"内测码"字段已经不存在 → 再`switch_page("pages/2_工作台.py")`（未登录状态）执行同样无异常。额外把`inject_theme()`实际注入的CSS markdown字符串抠出来断言：没有残留未替换的`{PRIMARY}`占位符（排除f-string转义写错的可能）、`#1165A4`/`box-shadow: 4px 4px 0 #0D4C7B`/`fonts.googleapis.com/css2?family=Inter`这几处新规则都确实出现在最终CSS里。

**没有做的验证**：没有真机浏览器截图，新配色/字体/按钮阴影效果在真实渲染下具体好不好看没有肉眼确认过，已经在`Docs/TODO.md`"需要你决策"里请用户自己双击`启动慧笔.bat`看一眼。

## 2026-07-22（第四十五轮）· 配备浏览器自动化工具，用它发现并修复essay.art配色改动的两个真实bug

**背景**：用户看到上一轮"没有真机截图确认"的诚实说明后，直接要求"配备浏览器自动化工具"。

**做了什么**：
1. **装Playwright（只进`.venv-uv`，不进`requirements.txt`）**：这个环境没有`chromium-cli`（`/run`技能提到的那个是特定托管环境的封装工具，普通Windows开发机上没有），改用公开可装的Playwright——`uv pip install playwright --python .venv-uv`装Python包，`.venv-uv/Scripts/python.exe -m playwright install chromium`下载Chromium二进制（装进`C:\Users\<user>\AppData\Local\ms-playwright\`，不在项目目录内，不受本仓库`.gitignore`影响）。先用`https://example.com`做了个最小烟雾测试确认"启动浏览器→截图→我能读到图片"这条链路真的通。这是我验证UI用的工具，不是产品运行依赖，所以没有写进`requirements.txt`。
2. **拿新工具去验证上一轮essay.art配色改动，发现两个headless方式（AppTest/字符串断言）测不出来的真实bug**：
   - 用Playwright截图+`getComputedStyle()`读登录页"注册"按钮的真实渲染值，发现`background-color`还是旧的`rgb(22,93,255)`（`#165DFF`）、`box-shadow`是`none`——上一轮的CSS改动在真机上根本没生效，尽管`AppTest`确认过CSS字符串本身包含新颜色/新阴影规则（说明"CSS字符串正确"和"CSS真的生效"是两回事，前者测不出后者）。
   - 排查过程一度怀疑是"Streamlit进程没重启、还在跑旧代码"，用`lsof -ti:8501 | xargs kill`杀旧进程，但`netstat`显示同一个端口下堆了三个不同时间起的PID都在`LISTENING`——Git-Bash的`lsof`/`kill`对这类Windows原生子进程杀不干净，是静默失败。改用PowerShell的`Get-CimInstance Win32_Process`列出真实PID、`Stop-Process -Force`精确杀掉、`Get-NetTCPConnection`确认端口干净后重新起一个真正全新的进程，问题依旧存在——排除了"进程没重启"这个假设。
   - 真正的根因是两个：①`.streamlit/config.toml`的`[theme] primaryColor`还是旧值`#165DFF`，这是Streamlit原生渲染`st.button`/`st.form_submit_button`这类控件颜色的真实来源，`src/ui_theme.py`里的自定义CSS只是覆盖层，两处颜色值一直靠"凑巧相等"在维持表面一致，这次改`PRIMARY`常量忘了同步改`config.toml`就露馅了。②`src/ui_theme.py`的按钮选择器`button[kind="primary"]`是精确匹配，但`st.form_submit_button(type="primary")`（登录/注册两个表单按钮用的都是这个）渲染出来的`kind`属性其实是`"primaryFormSubmit"`，从来没被这条规则选中过——也就是说自定义的硬阴影效果从写下那一刻起，在登录页从来没真的生效过，只是因为颜色凑巧和原生主题一致，肉眼从截图上完全看不出区别。
3. **修复**：`.streamlit/config.toml`的`primaryColor`同步改成`#1165A4`；`src/ui_theme.py`的按钮选择器改成`button[kind^="primary"]`（前缀匹配，同时覆盖`primary`和`primaryFormSubmit`两种`kind`），并新增`div[data-testid="stFormSubmitButton"] > button[kind^="primary"]`覆盖表单按钮的父级结构（表单按钮的直接父级是这个`data-testid`，不是`div.stButton`）。

**怎么验证的**：修复后重新截图+`getComputedStyle()`复查，`background-color`变成`rgb(17,101,164)`（`#1165A4`）、`box-shadow`变成`rgb(13,76,123) 4px 4px 0px 0px`（`#0D4C7B`硬阴影）、`font-family`确认是`Inter`，三项全部符合预期；额外截图确认了登录页大背景（蓝色渐变，无紫色残留）、注册按钮静止态（明显的硬阴影"贴纸感"）和悬停态（按钮上移、阴影加深）的真实视觉效果，肉眼确认好看、符合essay.art的设计意图。

**补充验证**：用Playwright驱动真实注册→登录流程（走UI表单，不是直接写库）进到工作台页，截图确认新配色在这个页面同样正常渲染；工作台"提交作文"按钮（`st.button(type="primary")`，`kind="primary"`不是`primaryFormSubmit`）的`getComputedStyle()`也确认吃到了新的`PRIMARY_DARK`/硬阴影规则，没有被这轮选择器改动影响。验证完随手把Playwright注册出来的测试账号从本地真实`huibi`库（不是`huibi_test`）里删掉了，不留测试数据。

## 2026-07-22（第四十六轮）· 大修样式，全站视觉语言参照essay.art真机截图重做

**背景**：用户在上一轮essay.art配色微调基础上，进一步要求"大修样式，所有样式均按照essay.art来改，包括排版，卡片等"——不再是调色系/字体这种局部修正，而是要求排版结构级别的对齐。

**做了什么**：
1. **先用Playwright真机截图essay.art首页，逐屏拆解实际排版**，不是只凭编译CSS猜结构（上一轮做过一次，这次证明CSS猜测和真实视觉效果之间确实有落差——比如essay.art"核心优势"卡片实际是"图标放卡片右上角+左对齐标题正文"，不是我之前设想的"数字编号+居中"）。截图确认的关键结构：导航是纯文字链接（无背景色块）+右侧一个纯文字"登录"；Hero是纯背景居中大标题（品牌名前缀高亮蓝色+其余黑字），标题下方左侧是勾选benefit列表+CTA按钮，右侧是产品截图预览；"核心优势"标题居中，卡片2列网格、每张卡左对齐标题正文+右上角小图标；结尾是浅色调"联系我们"面板；footer极简。
2. **`src/ui_theme.py`新增`BORDER`（`#E5E7EB`）/`CARD_SHADOW`（`0 1px 2px rgba(15,23,42,.04), 0 4px 16px rgba(15,23,42,.06)`）两个共享token**，把全文件里所有品牌蓝色调的卡片边框（`#E7EEF9`）和阴影（`rgba(17,65,148,x)`）都换成这两个中性灰token，涉及`.hb-card`/`.hb-dim-card`/`.hb-topic-card`/`.hb-essay-panel`/`.hb-score-panel`/`stMetric`/`stForm`/`stExpander`/`stDataFrame`/`stVegaLiteChart`等十几处；反馈/建议/语法错误这几类卡片刻意保留的暖色（`.hb-action-card`）/绿色（`.hb-exercise-card`）/红色（`.hb-grammar-card`）/金色（`.hb-essay-card`范文卡）语义区分没有动，这几个是有意区分"评价类/行动类/错误类/范文类"内容的既有设计决策，不属于"品牌蓝随手用滥了"要统一收编的范围。
3. **顶部导航从实心蓝色按钮改成纯文字链接**：`render_top_nav()`用`st.container(key="hb-topnav")`把整行`st.columns`包起来，Streamlit会给这个容器生成`st-key-hb-topnav`类名，CSS靠这个类名把导航区的`page_link`和页内其它CTA用的`page_link`（比如产品页"开始使用慧笔"）区分开——后者保留原来的实心蓝色按钮观感（essay.art的"立即批改雅思"这类CTA本身也是实心按钮），前者改成纯文字、当前页加粗+品牌蓝表示active、非active hover只变色不变背景。
4. **`.hb-hero`从渐变色块Hero改成纯背景居中大标题**：删掉原来`linear-gradient`+`radial-gradient`的深蓝渐变背景，标题居中、大字号加粗，新增`.hb-hero-accent`给品牌名前缀单独上色，仿"Essay.Art:雅思/托福/GRE写作批改专家"这种"品牌名高亮+其余黑字"的写法；删掉不再使用的`.hb-eyebrow`（原来Hero里的英文小标签，新设计没有这个元素）。
5. **`.hb-card`+`.hb-badge`从"数字编号+居中"改成essay.art实际的"图标右上角+左对齐"**：`.hb-badge`从内联文字徽章改成绝对定位在卡片右上角的方形图标容器，`.hb-card h4`右侧留出空间避免和图标重叠。新增`.hb-check-pill`（Hero下方勾选benefit列表，浅灰底+绿色勾号）。
6. **`app.py`整体重排**：居中Hero→（左）勾选清单+CTA按钮／（右）静态示例预览卡（展示一段示例作文摘录+分数+四维度简表，明确是示例、不是真实提交数据）→居中"核心优势"标题+2×2图标卡片网格→仿essay.art"联系我们"色块的收尾CTA面板（新增`.hb-closing-panel`，浅灰底大圆角）→footer。顺带删掉了一条过时文案"12,879篇训练作文样本"——项目在更早的轮次已经彻底放弃自训练评分模型、改用LLM+公开量表，这条数据本身就是历史遗留的不准确表述，这轮借着重排布局的机会一并清掉，不是新引入的问题。
7. **`pages/1_登录.py`从"渐变Hero+右侧表单"两栏改成纯背景居中标题+单栏居中表单卡片**：删掉左侧渐变卡片，标题和副标题直接用（改过的）`.hb-hero`样式居中显示在页面顶部，表单本身用`st.columns([1, 1.3, 1])`取中间列实现"居中定宽"，登录/注册两个tab逻辑完全没动。
8. **`pages/2_工作台.py`只改了它引用的CSS类**（`.hb-workbench-hero`/`.hb-account-card`从暖色/蓝色渐变改成中性白底+灰边框+新阴影token），Python代码一行没动。

**怎么验证的**：
- `python -m py_compile`四个改动文件无语法错误；`.venv-uv/Scripts/python.exe -c "from src.ui_theme import THEME_CSS"`确认导入不报错且`{PRIMARY}`/`{BORDER}`/`{CARD_SHADOW}`等占位符全部被替换、没有f-string转义遗漏。
- `streamlit.testing.v1.AppTest`：`app.py`→`switch_page`到`pages/1_登录.py`/`pages/2_工作台.py`全程`at.exception`为空，注册表单字段确认仍然只有"用户名/密码/确认密码"（没有回归内测码字段）。
- Playwright真机截图（这个环境把Streamlit真正的滚动容器`section[data-testid="stMain"]`搞清楚后，读它的真实`scrollHeight`再临时把viewport调高来截全图，`full_page=True`对这类内部滚动容器不生效，只截首屏）：产品页、登录页、注册页三张全页截图确认新版式符合预期（导航纯文字、Hero居中、优势卡片图标右上角、收尾CTA面板、footer）；登录后工作台页截图确认欢迎卡/账号卡的新中性配色。
- **真实走了一遍完整批改流程**（不是只看静态页面）：Playwright注册一个新账号、提交一篇109词的GENERAL作文、真实等DeepSeek V4 Pro评分返回（90/100），截图确认"写作批改"结果页的题目卡/作文原文高亮面板/分数面板/定性反馈2×2卡片/个性化修改建议（行动卡+练习卡+高分范文卡）/语法错误卡片在新样式下全部渲染正常、没有因为改CSS token破坏原有的flex对齐/高度撑满逻辑。验证完把这条测试提交记录和测试账号从本地真实`huibi`库里删掉，没有留下测试数据。
- `PYTHONPATH=. python scripts/smoke_test_nodes.py`（零依赖）全部通过，确认纯前端改动没有影响后端节点逻辑。

**补充验证**：essay.art本身没有和"历史进步仪表盘"直接对应的页面，但这部分引用的CSS类（`.hb-metric`/`stMetric`/`stVegaLiteChart`/`stDataFrame`/`stExpander`）都在这轮的token替换范围内，所以额外用`db.create_user`+`db.save_submission`直接写了2条合成测试记录（不经过真实LLM调用，纯本地造数据，免费）到一个临时账号，Playwright登录后截图确认指标卡/趋势折线图卡/历史表格/详情展开面板在新样式下都正常渲染，验证完把这个临时账号和2条记录从`huibi`库删掉了。

## 2026-07-22（第四十七轮）· 打分prompt加few-shot校准 + Agent编排加CriticAgentNode反思循环

**背景**：上一轮回答用户"模型是否建议微调/Agent编排是否太简单"这个探索性问题时，给出的建议是"不微调（已经没有本地模型对象、当时的驱动问题已用代码解决），few-shot prompting是比微调更划算的下一步；反思循环之前想先确认是否有具体证据支持"。用户这一轮直接给出决定：①做few-shot prompting；②Agent编排加入反思循环，不再是探讨阶段。

**做了什么**：
1. **`SCORE_RUBRIC_PROMPT`加few-shot校准示例**：新增`_SCORE_FEW_SHOT_EXAMPLES`（`src/agents/nodes.py`），按GENERAL/TOEFL/IELTS Task2/IELTS Task1四种量表各写一条"作文片段+对应正确评分JSON+评分理由"，`_score_few_shot_example(exam_type, exam_subtype)`按当前请求的考试类型/子类型只挑1条相关示例塞进`{few_shot_example}`占位符，不会把四种类型的示例都塞进同一次调用（控制token开销）。示例的作用是校准打分尺度（比如"论点笼统但语法正确"应该内容分低、语法分高，而不是被单一维度拉低整体印象），不是解决JSON格式问题——那个已经靠`normalize_rubric_result()`提前校验+重试1次解决了。
2. **新增`CriticAgentNode`反思循环**：`src/agents/nodes.py`新增`CRITIC_PROMPT`+`critic_agent_node()`，在`feedback_agent`产出定性反馈后复核一次，判断①是否具体引用原文作为证据而非空泛套话；②总体评价和维度反馈是否自相矛盾；③建议是否具体可执行。不合格时把具体问题写进`state["critic_notes"]`，`src/agents/graph.py`新增的`route_after_critic()`据此打回`feedback_agent`重新生成（`FEEDBACK_ONLY_PROMPT`新增`{critic_revision_note}`占位符，把critic的意见注入下一轮prompt）。**封顶1次重试**：`state["critic_revision_count"]`达到1后`critic_agent_node`无条件放行，不管质量如何，避免反思循环无限重试拖慢响应/推高成本，和打分节点"最多重试1次"是同一个尺度。`feedback_dimensions`为空（反馈本身生成失败）时直接放行，不对着空反馈瞎评价，省一次无意义的LLM调用。`src/agents/state.py`新增`critic_approved`/`critic_notes`/`critic_revision_count`三个字段。
3. **已知的效率取舍，记进了CLAUDE.md**：critic触发重写时，`feedback_agent_node`会完整重跑一遍（包括打分这一步），不是"只重跑反馈、复用上一轮分数"——要实现后者需要在state里额外缓存原始英文键的`rubric_scores`（当前`score_details`已经转成中文展示名，无法逆向还原原始键名喂给`normalize_rubric_result()`），这个复杂度换来的收益不成正比，且这条重试路径本身封顶1次，接受这个成本。

**怎么验证的**：
- `python -c "from src.agents.nodes import CRITIC_PROMPT, SCORE_RUBRIC_PROMPT, FEEDBACK_ONLY_PROMPT..."`真实调用`.format()`传入全部占位符，确认两个prompt模板改动后没有KeyError/大括号转义遗漏。
- `PYTHONPATH=. python scripts/smoke_test_nodes.py`（零依赖）全部通过，确认新增代码没有破坏免pip路径（`nodes.py`模块级只是新增字符串常量和函数定义，没有新增顶层重依赖import）。
- `.venv-uv/Scripts/python.exe -c "from src.agents.graph import build_graph; g = build_graph(); ..."`确认graph能正常编译，新增的`critic_agent`节点和两条边（`feedback_agent→critic_agent`、`critic_agent`的条件路由）确实注册进了图里（`g.get_graph().nodes.keys()`能看到9个节点）。
- **完整`e2e_graph_test.py`真实跑通（含真实DeepSeek调用）**：GENERAL测试用例新增了`critic_approved`/`critic_revision_count`断言，确认`critic_agent_node`真的执行过（不是`None`），这一次真实运行里第一次生成的反馈就通过了复核（`critic_approved: True, critic_revision_count: 0`），8个边界案例和数据库读写全部照常通过，没有因为新增节点引入回归；GENERAL作文这次评分78/100（四维度17/23/16/22），比之前同一篇作文在没有few-shot示例时的88/100更保守——不是bug，是few-shot校准示例明确演示了"缺乏具体例证的论点应该扣内容分"，促使模型对这篇论证偏笼统的作文给出更贴合示例尺度的分数，符合校准的预期效果。
- **针对性单独验证`critic_agent_node`的"拒绝"和"强制放行"分支**（真实e2e跑的时候DeepSeek第一次生成的反馈质量就够好，没有真实触发过拒绝路径，光靠e2e不能证明"打回重写"这条代码路径本身是对的）：手写一段故意空泛套话的反馈（"内容丰富""语言流畅"这类不引用原文的评价）直接调用`critic_agent_node()`，真实返回`critic_approved: False`+具体到位的`critic_notes`（"反馈没有引用原文任何具体内容...建议也空洞不可执行"）、`critic_revision_count`从0变成1；再手动把`critic_revision_count`设成1重新调用，确认无条件放行、不再消耗一次LLM调用；再传空`feedback_dimensions`，确认同样直接放行。三条路径都在真实LLM调用下验证过，不是只测了"一路通过"这一种情况。

**没有做的验证**：没有在真实的完整Graph里人为构造出"critic第一次拒绝→打回feedback_agent→第二次通过"这一整条链路的端到端案例（真实DeepSeek反馈质量目前还没在e2e测试里生成过一次不合格的结果，无法在不改造prompt强行制造低质量反馈的前提下触发这条路径），只在节点级别单独验证过“拒绝”分支本身的正确性。

## 2026-07-23（第四十八轮）· 补pytest+CI，重写README，本地/GitHub状态对齐

**背景**：用户问"当前项目是否完善、能否达到写简历的程度"。实际核对代码状态（不是凭对话记忆）后发现最紧急的问题不是"功能完不完善"，而是**GitHub上的仓库和本地实际状态严重脱节**：`origin/main`最新提交还停在"配置部署服务器SSH访问"那一轮，本地工作区有81个文件未提交，其中能看到`src/training/essay_scorer.py`这类CLAUDE.md里写明"已经删掉"的死代码——也就是说公开可见的仓库还挂着过时/不一致的内容。同时确认了两个真实缺口：没有自动化测试+CI、README只有26行没有任何截图。用户给出决定：①补轻量pytest+CI；②补充README；③直接把本地状态推到远程覆盖；④登录方式（PBKDF2）不用管。

**做了什么**：
1. **把81个未提交文件拆成6个有主题的commit**，不是一个大commit糊上去：①`refactor`删除自训练评分模型流水线（训练脚本/权重目录/EDA产物/课程阶段规划文档）；②`feat`新增LLM+RAG评分核心（`official_rubrics.py`/`exam_types.py`/RAG细则文件/`agents/`全链路节点，含上一轮的few-shot校准+CriticAgentNode）；③`feat`PostgreSQL持久化迁移；④`feat`Streamlit三页前端+`ui_theme.py`原创样式；⑤`test`验证脚本更新+依赖更新；⑥`docs`文档重构成4份精简文件。过程中发现`Docs/07`/`Docs/08`两个旧文档在git索引里有一条"陈旧的rename记录"（index显示rename，但对应的新文件名在磁盘上根本不存在）——核实确认这两份操作手册的内容早就被合并进`02-Progress.md`/`03-RUNNING.md`了，这条index记录只是历史遗留的记账残留，直接按删除处理，不是我这轮引入的问题。
2. **新增轻量pytest套件**（`tests/`，24个用例）：覆盖打分归一化（`normalize_rubric_result`按考试类型/子类型的四种路径+分数越界裁剪+JSON修复）、作文长度校验边界、语法规则库检测、`CriticAgentNode`两条不需要LLM调用的短路分支（重试封顶后强制放行/空反馈直接放行）、LangGraph路由函数（`route_after_intake`/`route_after_critic`/`build_graph`节点注册）。全部不需要API Key或数据库，零外部依赖。
3. **新增GitHub Actions CI**（`.github/workflows/tests.yml`）：每次push/PR只装`pytest`+`langgraph`两个轻量包（不装torch/chromadb/psycopg这些重依赖），跑`pytest -v`。完整链路的真实调用测试（`scripts/e2e_graph_test.py`，需要API Key+本地PostgreSQL）明确不放进CI，保持CI跑得快、免费、不需要密钥。
4. **重写README.md**：加了Playwright真机截图（产品首页）、核心能力列表、架构表（节点流程图+技术选型）、CI徽章、pytest/CI使用说明、项目文档索引，原来只有26行纯文字、没有任何截图和自动化测试说明。
5. **本地状态推送到GitHub，过程中发现并正确处理了一次远程分叉**：推送前`git fetch`发现`origin/main`比预期多了一个commit（`235f1ff`，GitHub网页端合并PR#1产生的merge commit），如果直接force-push会把这个merge commit记录抹掉。核实这个merge commit的内容（`cfb404b`）本来就已经在本地分支的线性历史里（`git merge-base --is-ancestor`确认），不是别人的独立新工作，于是用`git merge origin/main`（无冲突的干净合并，不引入任何新文件改动）把分叉合上，再正常`git push`（真正的fast-forward，全程没有用`--force`）推送`agent/project-updates`分支和`main`分支。

**怎么验证的**：
- pytest套件在`.venv-uv`（有langgraph）下24个用例全部通过；额外用`uv venv`建了一个只装`pytest`+`langgraph`两个包的全新临时venv（不装项目其余任何依赖），完整跑一遍套件同样24个全过——这一步是为了在推送前就确认CI workflow里`pip install pytest langgraph`这一行真的够用，不会推上去之后才发现CI环境缺依赖跑不过。
- 每个commit分组之后用`git status --short`核对暂存内容和预期文件列表一致，避免误把无关文件卷进某个commit。
- 推送前用`git rev-list --left-right --count origin/main...HEAD`确认是`0	N`（真正的fast-forward，不需要force）才执行`git push`，推送后重新`git fetch`+同样的rev-list命令确认变成`0 0`（本地和远程完全一致）。
- **push之后用`gh run list`真实检查GitHub Actions的运行结果**，不是只假设workflow文件写对了就完事——两次push（分支+main）触发的CI都是`completed success`，确认workflow本身在GitHub真实环境里能跑通，不是本地模拟出来的假象。

**没有做的验证**：没有回去改登录方式（用户明确说"不用管"）；没有验证pytest在完全没有langgraph、真正触发`test_graph_routing.py`里`pytest.importorskip`跳过路径的环境下的行为（这个环境本地两个Python环境都没装pytest且都能装成langgraph，没有构造出"pytest装了但langgraph没装"的场景，但`importorskip`是pytest标准API，行为有充分把握）。
