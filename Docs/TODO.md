# TODO 待办清单

> 现状速览：全部过程记录在`Progress.md`，浓缩版总结+复现步骤在`06-本轮成果与
> 复现步骤.md`，已确认的设计决策/环境信息/踩过的坑都在`CLAUDE.md`。
> 这份`TODO.md`只保留"需要你决策/补充的事项"和"4天开发Checklist"两块，
> 不再堆积过程记录/已解决事项/安全提醒这些——那些内容一旦解决就归档进
> `CLAUDE.md`或`Progress.md`，不留在这里重复。

## 需要你决策/补充的事项

- [ ] **项目文件夹是否改名**：当前根目录仍是占位名"7_速通小分队_项目名称"，`00-项目总览.md`给出了建议的正式命名。改名会影响IDE中已打开的路径引用，等团队确认后自行手动重命名。**持续暂缓**。

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

### Day 4 —— SSH访问已就绪，部署本身还没做
- [ ] 全员：修复联调问题，跑3~5个端到端测试用例（不同题材/不同水平的作文）
- [x] SSH访问`deploy-server`(`121.41.238.92`)已配置并测试连通；**已确认端口`8501`/`8502`/`80`/`8080`被这台机器上现有的生产容器/服务占用，我们的应用固定用`8503`**，见`CLAUDE.md`"不要重新踩的坑"
- [ ] C：实际执行部署到`deploy-server`（`RUNNING.md`第8节的命令已经按`8503`更新好）+ 离线演示预案（截图/录屏）
- [ ] D：定稿PPT与答辩话术；组织全员预演（掐时30分钟）
- [ ] A/B：准备好被深挖细节时的应答（两条模型路径的差异、LangGraph路由逻辑、essay_set 8表现差的原因）
- [ ] 全员：录制完整演示视频保底
