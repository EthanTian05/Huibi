# TODO 待办清单

> 现状速览：全部三轮的详细过程记录在`Progress.md`，浓缩版总结+复现步骤在
> `06-本轮成果与复现步骤.md`。这份`TODO.md`只保留"当前还要做什么/还要决策
> 什么"，不再堆积每一轮的过程性记录——历史过程去`Progress.md`翻。

## 需要你决策/补充的事项

- [ ] **GLM真实API Key**（可选）：`.env`里`GLM_API_KEY`还是占位值。DeepSeek单独工作正常，双供应商fallback目前实际只有一条腿在跑。
- [ ] **数据来源：是否要换回Kaggle官方渠道**：当前用的是HuggingFace上"llm-aes"组织发布的非gated镜像（内容与Kaggle官方一致，因为没有Kaggle账号无法走官方渠道），见`06-本轮成果与复现步骤.md`「数据来源说明」。如果不介意就不用管；如果答辩想强调"官方渠道"，操作步骤也写在那节里了。
- [ ] **训练服务器(`retinascope-server`)上`/data/wangchen/tiansukai/RAG/`的数据/模型要不要打包取回**：里面有完整训练数据(150MB+)、两个训练好的模型权重(266MB，未同步进git)、Chroma向量库，如果这台机器会被清理，需要提前处理。
- [ ] **本班选题查重**：`00-项目总览.md`假设"写作评估+学习陪伴"这一选题与同班其他组重复概率较低，但只是推测，需要团队实际确认本班已有/在做的选题列表，避免撞题（要求文档明确"整个班级不能出现重复的项目"）。**持续暂缓，不阻塞开发**。
- [ ] **项目文件夹是否改名**：当前根目录仍是占位名"7_速通小分队_项目名称"，`00-项目总览.md`给出了建议的正式命名。改名会影响IDE中已打开的路径引用，等团队确认后自行手动重命名。**持续暂缓**。

## 已确认的设计决策摘要（正式记录在`CLAUDE.md`"已确认、不要再改的设计决策"）

- **"225原则"**：训练循环的"2层循环(epoch/batch) + 2个遍历对象 + 5个核心步骤(梯度清零→正向传播→损失计算→反向传播→参数更新)"。两条评分模型的训练脚本已经按这个结构实现并跑出真实结果，见`03-模型训练与微调方案.md`。
- **LLM供应商**：主力DeepSeek V4 Flash，免费/兜底GLM-4.7-Flash。真实Key在本地`.env`（已gitignore），不出现在任何`Docs/*.md`里。
- **模型构建三条路径**：① DeepSeek/GLM负责生成类任务；② 微调DistilBERT（路径A，测试集QWK=0.693）；③ 从零构建的BiLSTM+Attention（路径B，测试集QWK=0.622）。已训练完成，非占位。
- **部署渠道**：SSH部署到自有服务器`121.41.238.92`（root/22/私钥登录）——**注意这台是Day4的最终部署服务器，和本轮用于训练的`retinascope-server`是两台不同的机器**，不要混淆。
- **Embedding模型**：`BAAI/bge-small-en-v1.5`（开源，已用于构建真实的120-chunk Chroma向量库）。
- **trait分项评分**：**降级为Day3/4待办**，不是已完成项——各essay_set的trait标注字段不统一，规范的多任务训练需要额外的掩码损失设计，本轮`EssayScorer`返回的`traits`是整体分的占位复制，不是单独训练的分项预测，见`03-模型训练与微调方案.md`顶部的诚实说明（之前版本把这条写成"已确认主线方案"是不准确的，已更正）。

## 安全提醒（历史教训，长期有效）

第二轮里DeepSeek的真实API Key曾被直接粘贴进`TODO.md`（会被当作交付材料提交、可能进版本库的文档），已经清理并补了`.gitignore`。**以后任何API Key/密码/私钥内容，一律只进`.env`，不要粘贴进任何`Docs/*.md`**，团队协作分发Key用口头/私聊，不要写进文档。仍建议评估是否需要重置那个曾经明文暴露过一次的DeepSeek Key。

第三轮里在训练服务器上执行`pkill -f 'streamlit run app.py'`误杀了同一台机器上正在跑的RetinaScope生产容器（命令行模式匹配到了同样的字符串），已自动恢复，用户已知情并确认继续。**以后在共用服务器上停止进程只能用精确PID（先`ps aux | grep`看清楚再`kill <PID>`），绝不能用`pkill -f`之类的模式匹配**，见`RUNNING.md`「0.5」。

## GitHub仓库现状

- 仓库地址：`https://github.com/BCXiaoxue/RAG_Writing.git`，分支`main`，当前私有，以后转public——**任何时候`git push`前都要用`git status --short --ignored`确认`.env`/`.venv/`/模型权重大文件没有被追踪**。
- 当前代码状态：不再是骨架/占位。数据管道、两条评分模型训练、RAG知识库、LangGraph全链路（含真实DeepSeek调用）、Streamlit UI都已经在训练服务器上实际跑通验证过，细节见`06-本轮成果与复现步骤.md`。这个本地开发环境本身`pip install`跑不了（网络层SSLEOFError，见`CLAUDE.md`"不要重新踩的坑"），所以验证工作是在`retinascope-server`上做的，不是在这台机器上。

## 4天开发Checklist（对照`04-四天开发计划与分工.md`）

### Day 1 —— 全部完成
- [ ] 全员对齐`00`~`03`号文档理解（这条必须团队成员自己读，没法代劳）
- [x] A：数据清洗 + EDA——已在真实ASAP-AES全量数据(12879条清洗后)上跑通，图表在`data/processed/eda/`
- [x] B：LangGraph骨架——`intake_validator`/`feedback_agent`/`coach_agent`/`retrieval_agent`/`scoring_tool`/`progress_tracker`全部真实实现并端到端验证通过
- [x] C：Streamlit四页面——已headless模式实测能正常serve(HTTP 200)
- [x] D：git仓库 + rubric/语法卡片——8个essay_set的真实rubric已从数据集提取生成，语法卡片仍只有3条手写示例（可以持续补充，不阻塞主链路）
- [x] 全员：`.env`可用——DeepSeek已验证调通，GLM待团队补充真实Key

### Day 2 —— 全部完成（本轮在训练服务器上提前跑完，见`06`号文档）
- [x] A：微调评分模型（DistilBERT）训练完成，测试集QWK=0.693
- [x] A：自定义构建模型（BiLSTM从零训练）训练完成，测试集QWK=0.622
- [x] A：`EssayScorer.predict()`统一封装（融合两条路径）
- [x] B：Chroma知识库建好（120个chunk），`retrieval_agent_node`/`feedback_agent_node`真实调用验证通过
- [x] C：SQLite表结构 + 提交页联通，已在`e2e_graph_test.py`验证读写
- [ ] D：知识库素材持续补充（rubric目前是原始英文，语法卡片只有3条）；`05`号答辩文档已经按真实QWK数字更新了话术，但还没做全员预演

### Day 3 —— 部分完成
- [x] 全员：评分模型→Graph→Streamlit端到端打通（已用真实模型+真实RAG验证）
- [ ] B：`grammar_check_node`补齐（还没接`language_tool_python`或规则库；`coach_agent_node`已经是真实实现，不用再补）；视时间决定是否做`CriticAgentNode`（stretch goal）
- [ ] C：历史进步仪表盘页面——目前只有评分趋势折线图，多头trait分项雷达图还没做（因为trait_scores本身还是占位值，做雷达图前最好先决定是否要补真实的多头训练，见上面"已确认的设计决策摘要"）
- [ ] A：两条模型路径的横向对比素材已经有了（真实QWK表，见`03`号文档），"微调前(零样本) vs 微调后"的对比还没做，如果时间允许可以补一个`--zero_shot`评估模式
- [ ] D：持续联调记录问题；更新`Progress.md`

### Day 4 —— 尚未开始
- [ ] 全员：修复联调问题，跑3~5个端到端测试用例（不同题材/不同水平的作文）
- [ ] C：SSH部署到`121.41.238.92`（用户`root`，端口22，私钥登录，**注意不是训练服务器`retinascope-server`**）+ 离线演示预案（截图/录屏）
- [ ] D：定稿PPT与答辩话术；组织全员预演（掐时30分钟）
- [ ] A/B：准备好被深挖细节时的应答（两条模型路径的差异、LangGraph路由逻辑、essay_set 8表现差的原因）
- [ ] 全员：录制完整演示视频保底
