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
