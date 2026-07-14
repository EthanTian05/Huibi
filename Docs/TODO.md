# TODO 待办清单

> 现状速览：全部四轮的详细过程记录在`Progress.md`，浓缩版总结+复现步骤在
> `06-本轮成果与复现步骤.md`。这份`TODO.md`只保留"当前还要做什么/还要决策
> 什么"，不再堆积每一轮的过程性记录——历史过程去`Progress.md`翻。

## 需要你决策/补充的事项

- [ ] **Kaggle官方数据集下载还差最后一步，需要你手动点一下**：`KAGGLE_API_TOKEN`本身有效（已验证能访问API），也定位到了官方文件`training_set_rel3.tsv`，但Kaggle要求**先在网页上手动接受比赛规则**才允许下载，这一步无法用API/token代劳。请登录Kaggle后打开 `https://www.kaggle.com/competitions/asap-aes/rules`，点"I Understand and Accept"，然后告诉我一声，我再重新跑下载。在此之前继续用HuggingFace镜像数据（内容一致，不影响任何已有结果）。
- [ ] **项目文件夹是否改名**：当前根目录仍是占位名"7_速通小分队_项目名称"，`00-项目总览.md`给出了建议的正式命名。改名会影响IDE中已打开的路径引用，等团队确认后自行手动重命名。**持续暂缓**。
- [ ] **121.41.238.92部署服务器的SSH访问信息**：你提到"代码最好在本地服务器上搞，因为后续要部署到121.41.238.92"，但你确认这只是Day4部署时的提醒，不是现在就要做。等实际要部署时需要你提供这台机器的host/user/密钥路径（格式参考`~/.ssh/config`里`retinascope-server`那一条），我再配置访问。

## 本轮（第四轮）已解决

- [x] **GLM真实API Key**：已拿到并验证调通（`scripts/check_llm_key.py`两个供应商都返回"调通成功"），存在本地`.env`，双供应商fallback现在真的有两条腿了。
- [x] **训练服务器上的模型权重要不要取回**：已经取回。两条模型的权重+分词器/词表/配置文件都拉回本地，并且发布到了GitHub Release（见下方"模型权重分发"），不需要再靠训练服务器活着才能拿到这些文件。
- [x] **本班选题查重**：已确认过，不再是待办。
- [x] **训练服务器(`retinascope-server`)上数据/模型要不要打包取回**：同上，已取回并发布到Release，训练服务器上的原始数据/模型可以按需清理，不再是唯一副本。

## 模型权重分发（本轮新增）

微调模型的`pytorch_model.bin`约265MB，超过GitHub单文件100MB的硬性限制，不能直接`git add`（Git LFS和"完全不进git"两个方案里，用户选择了第三个更好的方案：**发布为GitHub Release资产**）。已经做完：

- 两条模型的权重+配套文件（tokenizer/vocab/config）都上传到了 [`models-v1.0.0`](https://github.com/BCXiaoxue/RAG_Writing/releases/tag/models-v1.0.0) 这个Release。
- 写了`scripts/download_models.py`（自动下载+SHA-256校验）和`README.md`「模型权重下载」一节（含手动下载表格、校验值、"文件缺失时会发生什么"的说明）。
- `.gitignore`里模型相关文件的排除规则已经从"排除大文件"细化成"排除全部模型产出物（权重/tokenizer/vocab/config），只保留体积小的`training_log.json`"，逻辑更一致。
- `src/agents/nodes.py`里`scoring_tool_node`/`retrieval_agent_node`降级到占位逻辑时，现在会打印`warnings.warn(...)`明确提示（之前是静默降级，容易让人误以为是真实结果）。

**注意**：仓库当前是私有的，`download_models.py`匿名下载会失败（GitHub不允许匿名访问私有仓库的Release资产），必须在`.env`里配置`GITHUB_TOKEN`才能下载，等仓库转public之后就不需要token了。用于发布Release的GitHub Token已经存在本地`.env`（`GITHUB_TOKEN`），**这个token有仓库写权限，比其他API Key更敏感，尤其注意不要泄露**。

## 安全提醒（历史教训，反复出现，请认真对待）

**这个问题已经连续两轮发生了**：真实的API Key/Token被直接粘贴进`TODO.md`——第二轮是DeepSeek Key，第四轮又发生了两次（Kaggle Token、GLM Key）。每次我都会把真实值移到`.env`并在文档里脱敏，但这只是事后补救，**真正要避免的是一开始就不要把真实密钥打进任何`Docs/*.md`文件**，哪怕是随手写的"下一步"笔记也不行，因为这些文档会被当作交付材料/进版本库。以后有新的Key/Token/密码，麻烦直接告诉我"我有一个新的XX Key"，由我来问你要具体值并存进`.env`，不要自己先粘贴到文档里再让我清理。

另外，第三轮里在训练服务器上执行`pkill -f 'streamlit run app.py'`误杀了同一台机器上正在跑的RetinaScope生产容器（命令行模式匹配到了同样的字符串），已自动恢复，用户已知情并确认继续。**以后在共用服务器上停止进程只能用精确PID（先`ps aux | grep`看清楚再`kill <PID>`），绝不能用`pkill -f`之类的模式匹配**，见`RUNNING.md`「0.5」。

## 已确认的设计决策摘要（正式记录在`CLAUDE.md`"已确认、不要再改的设计决策"）

- **"225原则"**：训练循环的"2层循环(epoch/batch) + 2个遍历对象 + 5个核心步骤(梯度清零→正向传播→损失计算→反向传播→参数更新)"。两条评分模型的训练脚本已经按这个结构实现并跑出真实结果，见`03-模型训练与微调方案.md`。
- **LLM供应商**：主力DeepSeek V4 Flash，免费/兜底GLM-4.7-Flash，**两个都已验证真实可用**。真实Key在本地`.env`（已gitignore），不出现在任何`Docs/*.md`里。
- **模型构建三条路径**：① DeepSeek/GLM负责生成类任务；② 微调DistilBERT（路径A，测试集QWK=0.693）；③ 从零构建的BiLSTM+Attention（路径B，测试集QWK=0.622）。已训练完成，权重已发布到GitHub Release。
- **部署渠道**：SSH部署到自有服务器`121.41.238.92`（root/22/私钥登录）——**这台是Day4的最终部署服务器，和本轮用于训练的`retinascope-server`是两台不同的机器**，不要混淆。当前还没有这台机器的SSH访问配置。
- **Embedding模型**：`BAAI/bge-small-en-v1.5`（开源，已用于构建真实的120-chunk Chroma向量库）。
- **trait分项评分**：仍是Day3/4待办，不是已完成项——见`03-模型训练与微调方案.md`顶部的诚实说明。
- **数据集渠道**：默认走HuggingFace非gated镜像（已跑通）；Kaggle官方渠道的token已就绪，卡在"需要手动接受比赛规则"这一步，见上方"需要你决策"。

## GitHub仓库现状

- 仓库地址：`https://github.com/BCXiaoxue/RAG_Writing.git`，分支`main`，当前私有，以后转public——**任何时候`git push`前都要用`git status --short --ignored`确认`.env`/`.venv/`/模型权重大文件没有被追踪**。
- 代码状态：数据管道、两条评分模型训练、RAG知识库、LangGraph全链路（含真实DeepSeek调用）、Streamlit UI都已经实际跑通验证过；模型权重通过GitHub Release分发（见上方"模型权重分发"），不进git历史。细节见`06-本轮成果与复现步骤.md`。
- 这个本地开发环境本身`pip install`跑不了（网络层SSLEOFError，见`CLAUDE.md`"不要重新踩的坑"），验证工作在`retinascope-server`上做的。

## 4天开发Checklist（对照`04-四天开发计划与分工.md`）

### Day 1 —— 全部完成
- [ ] 全员对齐`00`~`03`号文档理解（这条必须团队成员自己读，没法代劳）
- [x] A：数据清洗 + EDA——已在真实ASAP-AES全量数据(12879条清洗后)上跑通，图表在`data/processed/eda/`
- [x] B：LangGraph骨架——`intake_validator`/`feedback_agent`/`coach_agent`/`retrieval_agent`/`scoring_tool`/`progress_tracker`全部真实实现并端到端验证通过
- [x] C：Streamlit四页面——已headless模式实测能正常serve(HTTP 200)
- [x] D：git仓库 + rubric/语法卡片——8个essay_set的真实rubric已从数据集提取生成，语法卡片仍只有3条手写示例（可以持续补充，不阻塞主链路）
- [x] 全员：`.env`可用——DeepSeek/GLM均已验证调通

### Day 2 —— 全部完成（本轮在训练服务器上提前跑完，见`06`号文档）
- [x] A：微调评分模型（DistilBERT）训练完成，测试集QWK=0.693，权重已发布到GitHub Release
- [x] A：自定义构建模型（BiLSTM从零训练）训练完成，测试集QWK=0.622，权重已发布到GitHub Release
- [x] A：`EssayScorer.predict()`统一封装（`src/training/essay_scorer.py`，内部融合两条路径）
- [x] B：Chroma知识库建好（120个chunk），`retrieval_agent_node`/`feedback_agent_node`真实调用验证通过
- [x] C：SQLite表结构 + 提交页联通，已在`e2e_graph_test.py`验证读写
- [ ] D：知识库素材持续补充（rubric目前是原始英文，语法卡片只有3条）；`05`号答辩文档已经按真实QWK数字更新了话术，但还没做全员预演

### Day 3 —— 部分完成
- [x] 全员：评分模型→Graph→Streamlit端到端打通（已用真实模型+真实RAG验证）
- [ ] B：`grammar_check_node`补齐（还没接`language_tool_python`或规则库；`coach_agent_node`已经是真实实现，不用再补）；视时间决定是否做`CriticAgentNode`（stretch goal）
- [ ] C：历史进步仪表盘页面——目前只有评分趋势折线图，多头trait分项雷达图还没做（因为trait_scores本身还是占位值，做雷达图前最好先决定是否要补真实的多头训练）
- [ ] A：两条模型路径的横向对比素材已经有了（真实QWK表，见`03`号文档），"微调前(零样本) vs 微调后"的对比还没做，如果时间允许可以补一个`--zero_shot`评估模式
- [ ] D：持续联调记录问题；更新`Progress.md`

### Day 4 —— 尚未开始
- [ ] 全员：修复联调问题，跑3~5个端到端测试用例（不同题材/不同水平的作文）
- [ ] C：SSH部署到`121.41.238.92`（用户`root`，端口22，私钥登录，**注意不是训练服务器`retinascope-server`**，目前还没有这台机器的SSH访问配置，需要用户提供）+ 离线演示预案（截图/录屏）
- [ ] D：定稿PPT与答辩话术；组织全员预演（掐时30分钟）
- [ ] A/B：准备好被深挖细节时的应答（两条模型路径的差异、LangGraph路由逻辑、essay_set 8表现差的原因）
- [ ] 全员：录制完整演示视频保底
