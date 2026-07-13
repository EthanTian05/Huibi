# TODO 待办清单

## 本轮已确认的决策（摘要+落地方式见此处；正式记录已同步进`CLAUDE.md`"已确认、不要再改的设计决策"）

- **"225原则"**：指训练循环的"2层循环+2个遍历对象+5个核心步骤"——外层遍历epoch、内层遍历batch（2层/2个遍历对象），每个batch内执行"梯度清零→正向传播→损失计算→反向传播→参数更新"5个核心步骤。这是训练循环的**最基本写法**，团队可以在此基础上叠加更好的方案（如学习率调度、梯度裁剪、混合精度、早停等），不是"用了225就不能加别的"。已更新`03-模型训练与微调方案.md`。
- **LLM API供应商**：主力用DeepSeek V4 Flash，免费/兜底用GLM-4.7-Flash（双供应商，其一不可用时可切换）。**真实API Key已存入本地`.env`（已加入`.gitignore`，不会被提交），不会出现在任何`Docs/*.md`里**，团队协作分发Key时也不要再粘贴进文档，见下方"安全提醒"。
- **自定义构建模型**：确认要做——在"微调预训练模型"之外，再加一条"完全从零构建、不依赖预训练权重"的模型路径，作为第三条模型路径，同时覆盖要求文档第6条里"预训练模型-微调"和"自定义构建模型"两个选项。已更新`03-模型训练与微调方案.md`。
- **部署渠道**：确定为自有/学校服务器，通过SSH部署（Host `121.41.238.92`，用户`root`，端口22，私钥登录）。已更新`RUNNING.md`"部署"一节；注意私钥文件本身留在各自本机，不要拷贝进仓库。
- **Embedding模型**：确定采用开源模型（不锁定具体型号，Day1按实际下载速度/效果二选一，默认建议见`00-项目总览.md`技术栈表）。
- **trait分项评分**：确认要做多头输出（不再是"时间不够就降级"的条件项），已更新`03-模型训练与微调方案.md`为主线方案。

## 安全提醒（本轮触发，请团队注意）

上一轮里，DeepSeek的真实API Key被直接粘贴进了这份`TODO.md`（一个会被当作项目交付材料、以后大概率会进版本库/提交给老师的文档）。本轮已经：

1. 把真实Key移到了本地`.env`文件里，并新增了`.gitignore`把`.env`排除在版本控制之外；
2. 把本文档里出现过的原始Key做了脱敏处理，本文档不再保留含真实Key的原始记录。

**建议团队评估是否需要重置/更换这个Key**——它已经在这轮对话和这份文档的历史版本里明文出现过一次，如果这个仓库以后会被push到GitHub或者分享给他人，存在泄露风险。以后任何API Key、密码、私钥内容，都不要直接粘贴进`Docs/`下的Markdown文档，一律写进`.env`（已被`.gitignore`排除）。

## 暂缓的决策事项（用户已明确"先不管，先开始Day1任务"）

- [ ] **本班选题查重**：`00-项目总览.md`假设"写作评估+学习陪伴"这一选题与同班其他组重复概率较低，但这只是推测，团队需要实际确认本班已有/在做的选题列表，避免撞题（要求文档明确"整个班级不能出现重复的项目"）。**暂缓，不阻塞Day1开发**。
- [ ] **项目文件夹是否改名**：当前根目录仍是占位名"7_速通小分队_项目名称"，`00-项目总览.md`给出了建议的正式命名。**暂缓，不阻塞Day1开发**，改名会影响IDE中已打开的路径引用，等团队确认后自行手动重命名。

## GitHub仓库与代码现状（本轮新增）

- 仓库地址：`https://github.com/BCXiaoxue/RAG_Writing.git`，当前是私有仓库，以后会转public——**任何时候`git push`前都要再确认一遍`.env`没有被追踪**（`.gitignore`已处理，但改动.gitignore或手动`git add -f`时要小心）。
- 本轮已完成：`git init` + 关联该远程仓库 + 合并了远程已有的`LICENSE`文件 + 首次push（commit `Day1: 项目规划文档 + LangGraph多智能体骨架 + Streamlit UI`），远程`main`分支现在就是最新代码。
- 本轮已经把Day1范围内"能由我直接实现的部分"写成了真代码（不再只是文档），具体见下面Day1小节的勾选状态，以及`Docs/Progress.md`当轮记录里的完整清单。
- **当前开发环境的`pip install`被网络环境挡住**（能`curl`/`urllib`访问pypi，但pip的HTTP客户端连接被重置，报`SSLEOFError`），所以`src/agents/graph.py`、`app.py`这些依赖`langgraph`/`langchain-openai`/`streamlit`的代码**在本轮里没能实际跑起来验证**，只做了语法检查（`py_compile`通过）。不依赖这些包的部分（`intake_validator_node`、`scoring_tool_node`占位逻辑、SQLite读写）已经用`scripts/smoke_test_nodes.py`跑通验证过。DeepSeek的真实Key也已经用纯标准库脚本`scripts/check_llm_key.py`验证调通。
- **你需要做的**：在一个`pip install`能正常工作的环境里（大概率不会有这个sandbox特有的网络问题），执行：
  1. `pip install -r requirements.txt`
  2. `python scripts/check_llm_key.py`（应该已经能跑通，只是再确认一遍）
  3. `streamlit run app.py`，在"提交批改"页粘贴一篇英语作文提交，看看能不能走完整个流程、"反馈详情"页的定性反馈是不是真的由DeepSeek生成的（不是空的或报错）
  4. 如果第3步报错，大概率是langgraph/langchain-openai的API随版本变化了签名（本轮没能实测，接口是按现在的公开文档写的），把报错贴回来我再改。

## Day1 建仓准备（可立即执行的操作类事项）

- [x] `git init`并确定协作方式（关联`https://github.com/BCXiaoxue/RAG_Writing.git`），已首次push到`main`分支；**已确认`.gitignore`生效、`.env`没有被追踪**（push前用`git status --short --ignored`核对过）。
- [x] 按`CLAUDE.md`"目录结构"一节建好`data/`、`models/`（尚为空，Day2训练后才有内容）、`src/`等骨架目录。
- [ ] 确认Python版本与本地/远程训练用的GPU资源（微调模型在本地或Colab跑，训练完再把权重同步到`121.41.238.92`部署服务器上，服务器本身不建议用来跑训练）——**这个还没定，Day2开工前需要团队确认**。
- [x] 把`.env.example`复制为`.env`，核对`DEEPSEEK_API_KEY`等值已就位；DeepSeek已用`scripts/check_llm_key.py`验证调通，GLM的Key还是`.env`里的占位值，团队如果拿到真实GLM Key再填进去即可，不填也不影响DeepSeek主链路。

## 4天开发Checklist（对照`Docs/04-四天开发计划与分工.md`）

### Day 1
- [ ] 全员对齐`00`~`03`号文档理解（这个必须是团队成员自己读，不能代劳）
- [ ] A：数据清洗 + EDA初版——**脚本已写好**（`src/data_pipeline/clean.py`/`eda.py`），但需要A先手动从Kaggle下载`training_set_rel3.tsv`放到`data/raw/`（Kaggle账号登录/协议这一步没法自动化），再跑脚本产出真实EDA图表
- [x] B：LangGraph骨架（占位节点跑通最小闭环）——`src/agents/`下的state/llm/nodes/graph已写好，`intake_validator`/`scoring_tool`(占位)/`grammar_check`(占位)/SQLite写入已用脚本验证；`retrieval_agent`(占位)/`feedback_agent`/`coach_agent`(真实调用DeepSeek)因pip装不上没能在本环境里跑通全图，需要B在自己环境里`pip install`后跑一遍确认
- [x] C：Streamlit四页面静态骨架——`app.py`已写好四个页面并接了后端Graph调用/SQLite历史，同样需要在能跑streamlit的环境里实测一遍
- [ ] D：git仓库/协作方式确定（已完成git部分）；rubric/语法卡片/范文标注第一版——**只写了每类1个占位示例**（`data/kb/rubric_essay_set_1.md`、`data/kb/grammar_cards.md`），D需要补齐其余7个essay_set的rubric和更多语法卡片/范文标注
- [x] 全员：确认`.env`可用（DeepSeek/GLM均已确定，Day1不需要再申请Key，只需要验证调通）——DeepSeek已验证，GLM待团队补充真实Key

### Day 2
- [ ] A：微调评分模型（BERT系）训练完成，产出QWK指标
- [ ] A：自定义构建模型（从零训练，不依赖预训练权重）训练完成，产出QWK指标，与微调模型做对比
- [ ] A：交付统一的`EssayScorer.predict()`封装（内部可选调用微调模型/自定义模型/两者融合）
- [ ] B：Chroma知识库建好（embedding模型选型落地）；`RetrievalAgentNode`、`FeedbackAgentNode`接通DeepSeek/GLM
- [ ] C：SQLite表结构 + 提交页基础联通
- [ ] D：知识库素材持续补充；`05`号答辩文档初稿

### Day 3
- [ ] 全员：评分模型→Graph→Streamlit端到端打通
- [ ] B：`GrammarCheckNode`、`CoachAgentNode`补齐；视时间决定是否做`CriticAgentNode`（stretch goal）
- [ ] C：历史进步仪表盘页面，含多头trait分项雷达图（创意加分核心）
- [ ] A：两条模型路径（微调 vs 自建）的训练前后/横向对比素材
- [ ] D：持续联调记录问题；更新`Progress.md`

### Day 4
- [ ] 全员：修复联调问题，跑3~5个端到端测试用例
- [ ] C：SSH部署到`121.41.238.92`（用户`root`，端口22，私钥登录）+ 离线演示预案（截图/录屏）
- [ ] D：定稿PPT与答辩话术；组织全员预演（掐时30分钟）
- [ ] A/B：准备好被深挖细节时的应答（两条模型路径的差异、LangGraph路由逻辑）
- [ ] 全员：录制完整演示视频保底

---

## 上一轮的指示与处理结果（已落地）

1. GitHub库`https://github.com/BCXiaoxue/RAG_Writing.git`——已关联为`origin`，合并了远程原有的`LICENSE`，已完成首次push，仓库现在是私有状态；转public前再检查一遍没有`.env`/大文件被误传即可。
2. 改名和查重按要求暂缓，已直接开始Day1任务——Day1范围内能由我直接实现的代码（LangGraph骨架、Streamlit UI、SQLite、数据处理脚本、RAG构建脚本、KB种子内容、LLM封装）已经写好并提交，具体完成度和"你需要手动做什么"见上面"GitHub仓库与代码现状"和各Day1条目里的标注。