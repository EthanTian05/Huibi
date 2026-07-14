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
