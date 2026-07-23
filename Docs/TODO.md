# TODO 待办清单

> 现状速览：全部过程记录在`02-Progress.md`，已确认的设计决策/环境信息/踩过的坑都在`CLAUDE.md`。
> 这份`TODO.md`只保留"需要你决策/补充的事项"、"上一轮完成情况汇报"两块，“下一步”（仅保留标题）
> `CLAUDE.md`或`Progress.md`，不留在这里重复。


## 需要你决策

- **反思循环触发重写时会连带重新打一次分（多一次DeepSeek调用），这是刻意接受的效率取舍，不是bug**：`critic_agent_node`只复核定性反馈质量，不复核数值评分，但`feedback_agent_node`没有拆出"只重跑反馈、复用上一轮分数"的路径——要做到这一点需要在state里额外缓存原始英文键的`rubric_scores`（现在`score_details`已经转成中文展示名，逆向还原不回去）。这条重试路径本身封顶1次（不是每次提交都会触发，只有critic判定不合格时才会），我判断这个复杂度不值得现在做，如果以后发现重写触发得很频繁、多打一次分的成本变得明显，再回来做"只重跑反馈"这个优化。

## 上一轮完成情况汇报

> 只保留最近一轮的浓缩汇报，更早的历史见`Progress.md`（每轮都有完整记录，不在这里累积）。

**第四十八轮**：你问"项目是否完善、能否达到写简历的程度"，实际核对后发现最紧急的问题是GitHub仓库和本地严重脱节（`origin/main`停在很早一轮，本地81个文件未提交，公开仓库还挂着已经删掉的自训练模型死代码）。你给出决定——①补轻量pytest+CI；②补README；③本地状态直接推送覆盖远程；④登录方式不用管。完成情况：①81个未提交文件拆成6个主题commit推送（删自训练模型流水线/LLM+RAG核心/PostgreSQL迁移/Streamlit前端/验证脚本/文档重构）；②新增`tests/`（24个零依赖用例，覆盖打分归一化/校验/语法规则库/CriticAgentNode短路分支/LangGraph路由）+`.github/workflows/tests.yml`（每次push跑，只装pytest+langgraph）；③README.md加了产品截图、核心能力、架构表、CI徽章、测试说明；④推送前发现`origin/main`比预期多一个GitHub网页合并PR产生的merge commit，确认其内容早就在本地历史里后用`git merge`（无冲突）而不是force-push合上分叉，全程fast-forward推送，没有用`--force`。

**怎么验证的**：pytest套件在`.venv-uv`和一个只装`pytest`+`langgraph`两个包的全新临时venv里都跑通（后者是为了在推送前确认CI里`pip install pytest langgraph`这行真的够用）；每个commit分组后用`git status`核对文件列表；推送前用`git rev-list --left-right --count`确认是真正的fast-forward才push；**push之后用`gh run list`真实检查GitHub Actions的运行结果**（不是只假设workflow文件写对了就完事），两次push触发的CI都是`completed success`。

**没有做的验证**：没有验证`test_graph_routing.py`里`pytest.importorskip`在"pytest装了但langgraph没装"这种场景下的真实跳过行为（本地两个Python环境要么都没装pytest要么都能装成langgraph，没有构造出这个中间状态，但`importorskip`是pytest标准API，行为有充分把握）。

## 下一步
（暂无）