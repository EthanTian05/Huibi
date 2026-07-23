# RUNNING · 环境搭建 / 运行 / 测试

> Day1骨架代码已经写好（`src/`、`app.py`），本文档是实际的运行步骤。如果你改了代码的运行方式，回来同步更新本文档，保持"文档=实际能跑的步骤"。

## 0. 已知问题：某些环境下`pip install`会失败

Day1脚手架阶段的开发环境里，`pip install`会报`SSLEOFError`（连接被重置），但`curl`/`python -m urllib.request`访问同一个pypi地址完全正常（HTTP 200）。排查过的点：
- 换`--index-url`（清华镜像/官方pypi.org）都一样失败，不是镜像的问题；
- 升级pip到最新版（26.x）、加`--trusted-host`都没用；
- 不是Key/项目本身的问题，是那个特定网络环境对pip的HTTP连接模式不友好。

如果你也遇到这个报错：换一个网络（比如手机热点/不同的校园网出口）通常能解决；如果换网络还不行，可以尝试`pip install --proxy ...`指定一个可用代理，或者用conda环境试试`conda install`。**这不代表整个项目有问题**，只是这一层网络环境的问题。

**已验证的绕开方案：用`uv`代替`pip`。** `uv venv --python 3.11 .venv-uv && uv pip install -r requirements.txt --python .venv-uv`在这个报`SSLEOFError`的环境里能完整装完全部依赖（含torch/transformers/streamlit/langgraph），`uv`会自己下载一份Python 3.11解释器，不依赖本机已有的Python版本。装完后用`.venv-uv/Scripts/python.exe`（Windows）代替系统`python`跑`e2e_graph_test.py`/`streamlit run app.py`。`.venv-uv/`已在`.gitignore`排除。

## 0.5 共用服务器操作规则（不管是训练机还是部署机都适用）

本轮已经彻底删除自训练评分模型和配套的数据处理流水线（见`CLAUDE.md`"已确认、不要再改的设计决策"），不再需要GPU训练环节；本节只保留在共用服务器上操作时通用的安全规则：

1. **停止自己启动的进程时，只能用精确PID，绝对不能用`pkill -f`之类的模式匹配**：曾经有一次教训——`pkill -f 'streamlit run app.py'`同时命中了同一台共用机器上另一个团队已经在跑的生产环境Docker容器（它的启动命令里也包含"streamlit run app.py"这几个字），导致生产服务被误杀（好在容器的`restart: unless-stopped`策略几十秒内自动拉起来了，没有造成数据损失）。以后一律先`ps aux | grep <关键词>`看清楚PID，只`kill <精确PID>`。
2. **任何要跑一段时间的命令都要`nohup ... > xxx.log 2>&1 &`真正后台化**：如果SSH连接本身不稳定，命令没有`nohup`+`&`，SSH会话一断命令就跟着死了。

## 1. 环境准备

```bash
# 建议使用虚拟环境（Day1已建好.venv，别的机器上需要重新建）
python -m venv .venv
.venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

如果`pip install`报`SSLEOFError`（见下方"0. 已知问题"），改用`uv`：

```bash
uv venv --python 3.11 .venv-uv
uv pip install -r requirements.txt --python .venv-uv
```

## 2. 环境变量

`01-源代码/.env`已经建好（内含真实DeepSeek Key），`.env.example`是给团队其他成员复制用的模板。**`.env`已加入`.gitignore`，不要提交进版本库，也不要把里面的真实Key再粘贴回任何`Docs/*.md`文档**：

```
DEEPSEEK_API_KEY=...        # 主力LLM，负责定性反馈/辅导建议/知识库问答
DEEPSEEK_MODEL_NAME=deepseek-v4-pro
GLM_API_KEY=...             # 免费兜底LLM
GLM_MODEL_NAME=glm-4.7-flash
LLM_PROVIDER=deepseek
LLM_FALLBACK_PROVIDER=glm

GLM_VISION_MODEL_NAME=glm-4v-flash           # 雅思Task 1图片理解专用，复用上面的GLM_API_KEY

POSTGRES_HOST=localhost                       # 用户历史/进步追踪的数据库
POSTGRES_PORT=5432
POSTGRES_DB=huibi
POSTGRES_USER=postgres
POSTGRES_PASSWORD=
```

打分（`get_scoring_chat_model()`）和定性反馈/辅导建议/知识库问答统一固定走`LLM_PROVIDER`指定的模型（DeepSeek V4 Pro），调用失败/超限时自动切换到`LLM_FALLBACK_PROVIDER`（GLM-4.7-Flash）。雅思Task 1图片理解固定用`GLM_VISION_MODEL_NAME`（不做fallback，失败会明确报错提示重新上传），**不要改成`glm-4.6v-flash`，实测限流严重（HTTP 429），`glm-4v-flash`才是实测能正常调用的**。

## 2.5 数据库（PostgreSQL）

用户历史/进步追踪存在本地PostgreSQL（`src/storage/db.py`，已从SQLite迁移，见`Docs/02-Progress.md`第四十一轮）。本机是`scoop install postgresql`装的18.4版：

```bash
scoop install postgresql          # 装好后默认trust本地认证，超级用户postgres、空密码
pg_ctl start                      # 启动服务（scoop装的服务不会自动开机启动，每次用之前要手动启动）
createdb huibi                    # 生产库
createdb huibi_test               # scripts/e2e_graph_test.py测试专用，跑之前会自动TRUNCATE，不影响huibi
```

建表不需要手动执行SQL——`db.get_connection()`每次连接时会自动跑一遍`CREATE TABLE IF NOT EXISTS`，首次连接就会自动建好`users`/`submissions`两张表。JSON类字段（`score_details`/`feedback_dimensions`/`coach_plan`等）用PostgreSQL原生`JSONB`类型，`psycopg`v3自动做Python dict与JSONB的双向转换。

## 3. 构建RAG知识库

```bash
python -m src.rag.build_kb            # 把data/kb/下所有.md切分、embedding后写入Chroma
# embedding模型用的是 BAAI/bge-small-en-v1.5（开源，走HF镜像下载）
```

`data/processed/chroma_kb/`（向量库本身）在`.gitignore`里排除了，重新跑一遍
`build_kb.py`（几十秒）就能重新生成，不需要额外同步。**诚实提醒**：`data/kb/`下GENERAL/IELTS/TOEFL的专属评分细则文件（`exam_rubrics/{general,ielts,toefl}.md`）目前不存在，需要先补充这些素材，`build_kb.py`才能索引到有意义的内容，见`Docs/TODO.md`。

## 4. 启动应用

```bash
streamlit run app.py
```

浏览器访问`http://localhost:8501`，现在是两个独立页面（左侧导航栏切换）：
- **app（产品介绍页）**：项目介绍 + 登录/注册。注册一个账号后，输入正确用户名密码直接登录成功。
- **工作台**（`pages/2_工作台.py`）：登录后才能访问，三个功能页面（写作批改/历史进步仪表盘/写作知识库问答），未登录直接访问这个页面会被拦截并提示先登录。

## 5. 测试

- **不需要`pip install`的两个免安装验证脚本**：

```bash
python scripts/check_llm_key.py              # 验证.env里的DeepSeek/GLM Key能不能真的调通
PYTHONPATH=. python scripts/smoke_test_nodes.py   # 验证intake校验/评分逻辑（不含数据库，db.py需要psycopg，见下）
```

- **完整链路测试（需要能pip install的环境——本机用`.venv-uv`，见"0. 已知问题"——且本地PostgreSQL已启动`pg_ctl start`，含真实DeepSeek调用+真实RAG检索+真实数据库读写）**：

```bash
PYTHONPATH=. .venv-uv/Scripts/python.exe scripts/e2e_graph_test.py
```

这个脚本会：先验证PostgreSQL读写往返（`test_db_roundtrip`/`test_auth_roundtrip`，连的是`huibi_test`库，不影响生产库`huibi`）；再提交GENERAL/IELTS/TOEFL的示例作文分别走完整个Graph（intake→image_analysis→retrieval→grammar→feedback→coach→progress），断言反馈/建议/量化评分非空、PostgreSQL正确写入；再提交一篇过短作文验证被正确短路拒绝；额外覆盖雅思Task 1带真实生成的图表图片走图片理解+Task Achievement量表场景。**如果`data/processed/chroma_kb`不存在，`retrieval_agent_node`会自动降级回占位结果**（不会报错崩溃），跑完之后对照日志确认是不是拿到了真实检索结果还是降级结果。

- `streamlit run app.py` 手动跑一遍界面同样必要（脚本测试不了UI交互本身），见第4节。
- **端到端手动测试清单**：
  - [ ] 提交一篇明显高分作文，检查评分、反馈是否合理。
  - [ ] 提交一篇有明显语法问题的作文，检查`GrammarCheckNode`是否能识别出对应错误并在反馈中体现（含LanguageTool检测到的、正则规则库覆盖不到的问题类型）。
  - [ ] 提交一篇过短/无意义文本，检查是否被`IntakeValidatorNode`正确拒绝并给出提示。
  - [ ] 同一账号连续提交2~3篇作文，检查"历史进步仪表盘"趋势图是否正确更新。
  - [ ] 断网/API Key失效场景下，检查前端是否有合理报错提示而不是直接崩溃。
  - [ ] 选雅思Task 1，上传一张真实的图表截图（柱状图/折线图/表格均可），确认能正常识图、评分卡显示Task Achievement维度、反馈里对图表数据的描述和图片实际内容一致；不上传图片直接提交应该被拦截。

## 6. 服务器部署（备用，当前不用）

**现在纯本地运行，不部署到服务器**——这一节是之前一版SSH部署方案的存档，以后要重新部署时参考，当前不需要执行。

- 目标服务器：`121.41.238.92`，用户`root`，端口22，私钥登录，本机SSH别名`deploy-server`（配置在`~/.ssh/config`，`IdentityFile ~/.ssh/id_rsa`，已测试连通）。**这是最终部署机，和`retinascope-server`（原本的GPU训练机，本轮自训练模型已删除后不再是必需依赖）是两台不同的机器，不要混淆**。
- **这台机器不是空的，是共用服务器，部署前必须知道这些**（已实测确认）：
  - 根分区`40G`总容量，部署前只剩`9.3G`可用、装完全部Python依赖后剩约`6.2G`——够用但不宽裕，注意不要在这台机器上跑模型训练或存大量数据。
  - **内存只有1.6G，比磁盘更容易踩坑**：曾经在还跑着自训练评分模型时因为同时起了两个模型加载进程触发过OOM killer（`dmesg`能看到`Out of memory: Killed process`记录，且内存打满时`sshd`会响应迟缓、表现成SSH连接长时间"banner exchange超时"，容易误判成网络问题）。自训练模型已删除后这个具体诱因不再存在，但这台机器内存依然紧张，跑任何本地验证脚本前还是先确认没有其他进程在抢内存。
  - **端口`80`、`8080`、`8501`、`8502`已经被占用**，其中`8501`是一个叫`ophthalmic-ai`的Docker容器（`docker ps`显示"Up 2 months (healthy)"，看内容像是田溯开另一个已上线的医疗项目），**绝对不要碰这个容器**（参考`RUNNING.md`「0.5」和`CLAUDE.md`里记录的pkill误杀生产容器的教训，这台机器上必须更谨慎）。我们的应用要用别的端口，见下方命令里已经改成了`8503`（当前实测空闲，正式部署前建议再用`ss -tlnp`确认一遍没被占用）。
  - **云安全组默认没放通8503**：即使服务器本机`curl localhost:8503`返回200，外网也访问不了，这一步和服务器本机的`iptables`/`ufw`无关，是阿里云ECS控制台的安全组规则没放行，只能登录控制台加一条TCP 8503入站规则，SSH改不了。**本轮已经放通并验证过外网可访问**。
  - Docker本身是装好的（29.4.1），如果想用容器化部署也可以，但没有现成的nginx。
- 部署方式（**已实际执行过，代码在`/root/sukai/`，不是之前草稿写的`/root/huibi/`**）：

```bash
# 1. 把代码同步到服务器（本地开发机没有rsync，用tar+scp代替，排除.git/.venv/__pycache__/.env）
tar --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='.env' -czf huibi_deploy.tar.gz .
scp huibi_deploy.tar.gz deploy-server:/root/huibi_deploy.tar.gz
ssh deploy-server "mkdir -p /root/sukai && cd /root/sukai && tar xzf /root/huibi_deploy.tar.gz && rm /root/huibi_deploy.tar.gz"

# 2. 登录服务器，安装依赖（deploy-server无GPU，torch要装CPU-only版本——torch/transformers/
#    sentence-transformers现在只服务RAG的embedding模型，不再涉及评分模型推理，否则pip默认拉CUDA版体积大很多）
ssh deploy-server
cd /root/sukai && python3 -m venv .venv && source .venv/bin/activate
pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
pip install --no-cache-dir -r requirements.txt
# 磁盘只剩8.7G左右，装完全部依赖后建议 df -h / 确认还有空间，pip加--no-cache-dir避免缓存占地方

# 3. 服务器上单独准备.env（不要通过tar/rsync同步含真实Key的.env，用scp单独传一次）
scp .env deploy-server:/root/sukai/.env

# 4. 构建RAG知识库（chroma_kb目录本身gitignore了，没有跟着代码包一起过来，需要在服务器上重新生成）
ssh deploy-server "cd /root/sukai && source .venv/bin/activate && export HF_ENDPOINT=https://hf-mirror.com HF_HUB_DISABLE_XET=1 && python -m src.rag.build_kb"

# 5. 后台常驻运行，端口用8503，不要用被占用的8501/8502/80/8080
#   推荐用 scripts/deploy_start.ps1 / scripts/deploy_stop.ps1（本地跑，SSH远程管理，只用精确PID
#   停止进程，不用pkill -f模式匹配，见两个脚本文件开头的注释）：
powershell -File scripts/deploy_start.ps1   # 启动+验证HTTP 200
powershell -File scripts/deploy_stop.ps1    # 停止

#   或者手动：
nohup streamlit run app.py --server.port 8503 --server.address 0.0.0.0 > streamlit.log 2>&1 & echo $! > streamlit.pid
kill $(cat streamlit.pid)   # 停止时只用这个精确PID，不要用pkill -f

# 6. 确认服务器防火墙/安全组放通8503端口（已完成，见上方"云安全组默认没放通8503"）
```

- **部署状态**：此前的部署（自训练模型仍在时）已外网实测通过（`curl http://121.41.238.92:8503`返回200）。本轮删除自训练模型、简化Graph结构后，**还没有在部署环境重新跑过`scripts/e2e_graph_test.py`和手工UI验证**，见`Docs/TODO.md`，重新部署/验证之前不要假设线上环境已经是最新代码。
- 仍然建议：答辩前从答辩现场实际网络再实测一次`http://121.41.238.92:8503`（校园网/外网限制、防火墙规则可能和开发者所在网络不一样）。
- 安全提醒：服务器用`root`直接部署仅为4天工期图快，如果这个项目之后要长期运行/给更多人用，建议改成非root部署用户；私钥文件本身任何时候都不要提交进仓库或粘贴进文档。
