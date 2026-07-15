# TODO 待办清单

> 现状速览：全部过程记录在`Progress.md`，四人角色操作手册（含复现步骤）在
> `07`~`10`号文档，已确认的设计决策/环境信息/踩过的坑都在`CLAUDE.md`。
> 这份`TODO.md`只保留"需要你决策/补充的事项"、"Day4"、"上一轮完成情况汇报"三块，
> 不再堆积过程记录/已解决事项/安全提醒这些——那些内容一旦解决就归档进
> `CLAUDE.md`或`Progress.md`，不留在这里重复。

## 需要你决策/补充的事项

（当前无待决策事项——安全组端口已放通，部署链路全部验证通过）

## Day4（Day1~3全部完成，详细记录见`Progress.md`，不再在这里堆砌）—— **部署+外网访问已全部打通**
- [x] 全员：跑通端到端测试用例（正常/过短/边界值/语法密集/essay_set 8，共7个场景，详见`Progress.md`）
- [x] SSH访问`deploy-server`(`121.41.238.92`)已配置并测试连通；**已确认端口`8501`/`8502`/`80`/`8080`被这台机器上现有的生产容器/服务占用，我们的应用固定用`8503`**，见`CLAUDE.md`"不要重新踩的坑"
- [x] C：实际执行部署到`deploy-server`——代码在`/root/sukai/`，依赖装好（CPU版torch），RAG知识库已现场构建，Streamlit已启动。**外网访问已验证：`http://121.41.238.92:8503` 返回HTTP 200**（安全组端口已放通），`scripts/e2e_graph_test.py`在部署环境里单独跑过一遍完整通过（真实DeepSeek+真实评分+真实RAG，7个场景全过）。离线演示预案（截图/录屏）还没做
- [ ] D：定稿PPT与答辩话术；组织全员预演（掐时30分钟）
- [ ] A/B：准备好被深挖细节时的应答（两条模型路径的差异、LangGraph路由逻辑、essay_set 8表现差的原因——现在有真实诊断数据支撑，见Day3 D）
- [ ] 全员：录制完整演示视频保底

## 上一轮完成情况汇报

> 只保留最近一轮的浓缩汇报，更早的历史见`Progress.md`（每轮都有完整记录，不在这里累积）。

**第十四轮**：`retinascope-server`恢复连接后，把上面本地没有的数据文件（`data/raw`、`data/processed/{train,val,test,essays_clean}.csv`、`data/processed/chroma_kb`，共32MB压缩包）打包取回本地，核对模型权重字节数完全一致后，**精确删除了`/data/wangchen/tiansukai/RAG/`整个目录**（删除前逐层确认过路径，没有碰同目录下其他人的`data`/`effnet_b4_bce_retrain`/`yijun`），释放了这台共用服务器上的空间。`deploy-server`SSH恢复后排查发现之前断线是因为**这台服务器只有1.6G内存**，我起的`e2e_graph_test.py`和已经在跑的Streamlit同时各自加载一份DistilBERT模型，触发了系统OOM killer（真实`dmesg`日志证实），不是网络问题——已经把这个坑记进`CLAUDE.md`。改成"先停Streamlit→单独跑测试→再启动Streamlit"的顺序后，`e2e_graph_test.py`在部署环境里干净跑通全部7个场景。你确认"开放了8503"后，`curl http://121.41.238.92:8503`外网实测返回HTTP 200——**部署链路完整打通**。详见`Progress.md`第十四轮记录。

## 下一步


