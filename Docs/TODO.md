# TODO 待办清单

> 现状速览：全部过程记录在`02-Progress.md`，已确认的设计决策/环境信息/踩过的坑都在`CLAUDE.md`。
> 这份`TODO.md`只保留"需要你决策/补充的事项"、"上一轮完成情况汇报"两块，“下一步”（仅保留标题）
> `CLAUDE.md`或`Progress.md`，不留在这里重复。


## 需要你决策

- **反思循环触发重写时会连带重新打一次分（多一次DeepSeek调用），这是刻意接受的效率取舍，不是bug**：`critic_agent_node`只复核定性反馈质量，不复核数值评分，但`feedback_agent_node`没有拆出"只重跑反馈、复用上一轮分数"的路径——要做到这一点需要在state里额外缓存原始英文键的`rubric_scores`（现在`score_details`已经转成中文展示名，逆向还原不回去）。这条重试路径本身封顶1次（不是每次提交都会触发，只有critic判定不合格时才会），我判断这个复杂度不值得现在做，如果以后发现重写触发得很频繁、多打一次分的成本变得明显，再回来做"只重跑反馈"这个优化。

## 上一轮完成情况汇报

> 只保留最近一轮的浓缩汇报，更早的历史见`Progress.md`（每轮都有完整记录，不在这里累积）。

**第四十七轮**：你对上一轮"模型是否建议微调/Agent编排是否太简单"的探讨给出了明确决定——①做few-shot prompting；②Agent编排加入反思循环。完成情况：①`src/agents/nodes.py`新增`_SCORE_FEW_SHOT_EXAMPLES`（GENERAL/TOEFL/IELTS Task2/IELTS Task1各一条"作文片段+正确评分+评分理由"），`SCORE_RUBRIC_PROMPT`按当前请求的考试类型只塞1条相关示例，用来校准打分尺度（不是解决JSON格式问题，那个已经有别的机制处理）。②新增`critic_agent_node`+`CRITIC_PROMPT`：`feedback_agent`产出反馈后复核一次（是否空泛套话/自相矛盾/建议不可执行），不合格打回`feedback_agent`重新生成（`FEEDBACK_ONLY_PROMPT`新增`{critic_revision_note}`把critic意见注入下一轮），封顶1次重试；`src/agents/graph.py`新增`route_after_critic()`路由，`src/agents/state.py`新增`critic_approved`/`critic_notes`/`critic_revision_count`三个字段。

**怎么验证的**：`smoke_test_nodes.py`（零依赖）确认新增代码没有引入重依赖；`.venv-uv`环境下`build_graph()`确认9个节点+两条critic相关的边正确注册；完整`e2e_graph_test.py`真实跑通（含真实DeepSeek调用），新增了`critic_approved`/`critic_revision_count`断言确认这个节点真的执行过（这次真实运行第一次生成的反馈就通过了复核，没有触发重写）；**额外针对性单独测试了`critic_agent_node`的"拒绝"和"强制放行"分支**（e2e跑的时候DeepSeek质量够好没有真实触发过拒绝路径，光测"一路通过"不能证明"打回重写"这条代码是对的）——手写明显空泛套话的反馈直接调用这个节点，真实返回`critic_approved: False`+具体到位的`notes`；把`revision_count`设成1后重新调用，确认无条件放行不再消耗LLM调用；传空`feedback_dimensions`确认同样直接放行。三条分支都在真实LLM调用下验证过。

**没有做的验证**：没有在完整Graph里跑出一次真实的"critic第一次拒绝→打回feedback_agent→第二次通过"端到端案例（DeepSeek反馈质量目前还没在e2e测试里生成过真的不合格的结果），只在节点级别单独验证过拒绝分支本身。

## 下一步
（暂无）