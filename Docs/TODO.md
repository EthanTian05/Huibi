# TODO 待办清单

> 现状速览：全部过程记录在`02-Progress.md`，已确认的设计决策/环境信息/踩过的坑都在`CLAUDE.md`。
> 这份`TODO.md`只保留"需要你决策/补充的事项"、"上一轮完成情况汇报"两块，“下一步”（仅保留标题）
> `CLAUDE.md`或`Progress.md`，不留在这里重复。


## 需要你决策

- **反思循环触发重写时会连带重新打一次分（多一次DeepSeek调用），这是刻意接受的效率取舍，不是bug**：`critic_agent_node`只复核定性反馈质量，不复核数值评分，但`feedback_agent_node`没有拆出"只重跑反馈、复用上一轮分数"的路径——要做到这一点需要在state里额外缓存原始英文键的`rubric_scores`（现在`score_details`已经转成中文展示名，逆向还原不回去）。这条重试路径本身封顶1次（不是每次提交都会触发，只有critic判定不合格时才会），我判断这个复杂度不值得现在做，如果以后发现重写触发得很频繁、多打一次分的成本变得明显，再回来做"只重跑反馈"这个优化。

## 上一轮完成情况汇报

> 只保留最近一轮的浓缩汇报，更早的历史见`Progress.md`（每轮都有完整记录，不在这里累积）。

**第四十九轮**：你截图反馈GitHub的Contributors列表里出现了"claude"，要求不要有这种情况。根因是上一轮11个commit都带了`Co-Authored-By: Claude Sonnet 5`这行trailer，GitHub据此把Claude算成了独立贡献者。这几个commit已经推到远程，去掉trailer必须重写历史+force-push——**先用`AskUserQuestion`确认要不要现在执行**（改写已公开历史是有风险的操作），用户选择"重写并force-push两个分支"后才动手：`git filter-branch --msg-filter`删trailer（只改提交信息，不改任何文件树内容，用`git diff`确认过内容零差异），`git push --force-with-lease`（不是裸`--force`）推送`main`和`agent/project-updates`。**这轮开始的commit已经不再带Co-Authored-By trailer**，避免同样的问题再发生。

**怎么验证的**：`git diff refs/original/refs/heads/agent/project-updates agent/project-updates --stat`确认重写前后文件树内容完全一致；`git log --grep="Co-Authored-By: Claude"`确认真正的分支引用下（不是filter-branch自动生成的备份引用）已经查不到这行；`gh run list`确认force-push之后GitHub Actions两个分支仍然是`completed success`。

**没有做的验证**：没有验证`test_graph_routing.py`里`pytest.importorskip`在"pytest装了但langgraph没装"这种场景下的真实跳过行为（本地两个Python环境要么都没装pytest要么都能装成langgraph，没有构造出这个中间状态，但`importorskip`是pytest标准API，行为有充分把握）。

## 下一步
（暂无）