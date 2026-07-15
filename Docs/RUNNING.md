# RUNNING · 环境搭建 / 运行 / 测试

> Day1骨架代码已经写好（`src/`、`app.py`），本文档是实际的运行步骤。如果你改了代码的运行方式，回来同步更新本文档，保持"文档=实际能跑的步骤"。

## 0. 已知问题：某些环境下`pip install`会失败

Day1脚手架阶段的开发环境里，`pip install`会报`SSLEOFError`（连接被重置），但`curl`/`python -m urllib.request`访问同一个pypi地址完全正常（HTTP 200）。排查过的点：
- 换`--index-url`（清华镜像/官方pypi.org）都一样失败，不是镜像的问题；
- 升级pip到最新版（26.x）、加`--trusted-host`都没用；
- 不是Key/项目本身的问题，是那个特定网络环境对pip的HTTP连接模式不友好。

如果你也遇到这个报错：换一个网络（比如手机热点/不同的校园网出口）通常能解决；如果换网络还不行，可以尝试`pip install --proxy ...`指定一个可用代理，或者用conda环境试试`conda install`。**这不代表整个项目有问题**，只是这一层网络环境的问题。

## 0.5 本轮已经在训练服务器上把全部流程实际跑通了一遍——几条硬性规则

本轮用SSH连到田溯开提供的训练服务器（`ssh retinascope-server`，配置在`~/.ssh/config`，8×A100，此前RetinaScope项目也部署在这台机器上）完整跑通了数据下载→清洗→EDA→预处理→两条模型训练→建RAG知识库→端到端LangGraph+Streamlit验证。以下是过程中踩出来的、**下次操作这台服务器必须遵守**的规则：

1. **只在`/data/wangchen/tiansukai/RAG/`下操作，不要碰`/root/`**：这台服务器的根分区(`/`)已经100%满（`df -h /`显示0可用），是被很多人共用的机器（`/root/`下有其他同学的家目录）。`/data`分区还有1.4TB可用，本项目的代码、venv、pip缓存、HuggingFace缓存、训练数据、模型权重全部放在`/data/wangchen/tiansukai/RAG/`下，用`TMPDIR`/`PIP_CACHE_DIR`/`HF_HOME`环境变量把临时文件和缓存也指过去，不要用默认路径（默认会写到`/root/.cache`，那里没有空间）。
2. **停止自己启动的进程时，只能用精确PID，绝对不能用`pkill -f`之类的模式匹配**：本轮有一次教训——`pkill -f 'streamlit run app.py'`同时命中了这台机器上已经在跑的、田溯开的RetinaScope生产环境Docker容器（它的启动命令里也包含"streamlit run app.py"这几个字），导致生产服务被误杀（好在Docker的`restart: unless-stopped`策略几十秒内自动拉起来了，没有造成数据损失）。以后一律先`ps aux | grep <关键词>`看清楚PID，只`kill <精确PID>`。
3. **HuggingFace Hub的国内访问要绕两层**：`huggingface.co`本身连不通，要设`HF_ENDPOINT=https://hf-mirror.com`走镜像；但镜像只代理了API/resolve请求，模型的大文件（如`model.safetensors`）走的是HF新的"Xet"存储后端(`xethub.hf.co`)，这个域名镜像不了、会卡住卡死（现象：下载进度长期停在0字节，反复打印"Trying to resume download..."但毫无进展）。**必须加一个环境变量`HF_HUB_DISABLE_XET=1`**强制退回普通HTTP下载路径，才能正常下载。
4. **这台机器的Python所链接的OpenSSL证书目录是空的**：`curl`/`openssl`用系统正常的证书链没问题，但Python的`ssl.get_default_verify_paths()`指向一个自定义、几乎是空的OpenSSL目录，会报`certificate verify failed: self-signed certificate in certificate chain`。用`requests`/`httpx`/`openai`/`langchain_openai`这些库不受影响（它们默认走`certifi`包的证书），但如果自己写`urllib.request`之类的裸调用，要么设`SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")`，要么显式传`ssl.create_default_context(cafile=certifi.where())`。
5. **训练前用`nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv`看一眼**，这台机器是共用的，挑一块显存/利用率都接近0的卡，用`CUDA_VISIBLE_DEVICES=<index>`指定，不要不看就抢占别人正在用的卡。
6. **任何要跑一段时间的命令都要`nohup ... > xxx.log 2>&1 &`真正后台化**：这条SSH连接本身不稳定（大概每隔几次调用就会"Connection closed by ... port 22"，重试一般就好），如果命令没有`nohup`+`&`，SSH会话一断命令就跟着死了（拿"构建RAG知识库"那一步练过一次，第一次没加`nohup`直接被连接中断打断，第二次补上才成功）。

## 1. 环境准备

```bash
# 建议使用虚拟环境（Day1已建好.venv，别的机器上需要重新建）
python -m venv .venv
.venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

## 2. 环境变量

`01-源代码/.env`已经建好（内含真实DeepSeek Key），`.env.example`是给团队其他成员复制用的模板。**`.env`已加入`.gitignore`，不要提交进版本库，也不要把里面的真实Key再粘贴回任何`Docs/*.md`文档**：

```
DEEPSEEK_API_KEY=...        # 主力LLM
DEEPSEEK_MODEL_NAME=deepseek-v4-flash
GLM_API_KEY=...             # 免费兜底LLM
GLM_MODEL_NAME=glm-4.7-flash
LLM_PROVIDER=deepseek
LLM_FALLBACK_PROVIDER=glm
```

代码里对接LLM时建议做一层provider抽象：优先调用`LLM_PROVIDER`指定的模型，调用失败/超限时自动切换到`LLM_FALLBACK_PROVIDER`，这样答辩现场如果DeepSeek临时不可用，还能用GLM兜底演示。

## 3. 数据准备（已跑通，命令原样可复现）

Kaggle官方数据集需要账号/协议，无法自动化下载；本轮改用HuggingFace上非gated的镜像
（`llm-aes`组织发布，覆盖全部8个essay_set，共12976条，来源见`Docs/00-项目总览.md`
「参考资料」），不需要任何账号：

```bash
export HF_ENDPOINT=https://hf-mirror.com   # 国内访问HF要走镜像
export HF_HUB_DISABLE_XET=1                # 见0.5节，否则大文件下载会卡死
export HF_HOME=<你自己的缓存目录>           # 避免写到空间不够的默认路径

python -m src.data_pipeline.download    # 下载并合并为 data/raw/asap_aes_merged.parquet
python -m src.data_pipeline.clean       # 清洗：12976 -> 12879条
python -m src.data_pipeline.eda         # EDA图表输出到 data/processed/eda/（已生成，见该目录）
python -m src.data_pipeline.preprocess  # 归一化 + 8:1:1分层划分，同时生成 data/processed/score_ranges.json
python -m src.rag.build_rubric_docs     # 从原始数据里提取每个essay_set真实的prompt/rubrics，生成data/kb/rubric_essay_set_*.md
```

如果你确实想用Kaggle官方文件（比如答辩被问起数据来源想展示更"官方"的出处），把
`training_set_rel3.tsv`放到`data/raw/`下，`clean.py`会自动优先用它，不需要跑
`download.py`。

## 4. 训练两条评分模型（已跑通，真实结果见`Docs/03-模型训练与微调方案.md`）

```bash
# 挑一块空闲GPU（见0.5节第5条），下面假设用0号卡
export CUDA_VISIBLE_DEVICES=0

# 路径A：微调（基于预训练权重，实际用的是distilbert-base-uncased）
python -m src.training.train_finetuned \
    --model_name distilbert-base-uncased \
    --epochs 4 --batch_size 32 \
    --output_dir models/essay-scorer-finetuned/v1
# 实际结果：4轮跑完，测试集QWK(宏平均)=0.693

# 路径B：自定义构建（从零训练，不加载任何预训练权重），可以用另一块空闲GPU并行跑
python -m src.training.train_custom \
    --epochs 12 --batch_size 32 \
    --output_dir models/essay-scorer-custom/v1
# 实际结果：验证集QWK连续3轮不提升，第6轮早停，测试集QWK(宏平均)=0.622
```

两个脚本训练完会自动在测试集上评估并把QWK写进各自`training_log.json`，不需要单独跑
evaluate脚本。`models/essay-scorer-finetuned/v1/pytorch_model.bin`（约254MB）和
`models/essay-scorer-custom/v1/pytorch_model.bin`（约12MB）体积较大，`.gitignore`
里排除了，仓库里只保留了`training_log.json`（训练过程/最终指标）——**权重文件本身
需要重新训练获得，或者找有权限的人从`retinascope-server:/data/wangchen/tiansukai/RAG/models/`
scp过来**。

## 5. 构建RAG知识库（已跑通）

```bash
python -m src.rag.build_rubric_docs   # 见第3节，先生成8个essay_set的真实rubric文档
python -m src.rag.build_kb            # 把data/kb/下所有.md切分、embedding后写入Chroma
# 实际结果：120个chunk，embedding模型用的是 BAAI/bge-small-en-v1.5（开源，走HF镜像下载）
```

`data/processed/chroma_kb/`（向量库本身，约1.1MB）在`.gitignore`里排除了，重新跑一遍
`build_kb.py`（几十秒）就能重新生成，不需要额外同步。

## 6. 启动应用

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501`，四个页面：提交批改 / 反馈详情 / 历史进步仪表盘 / 写作知识库问答。

## 7. 测试

- **Day1已有的两个免安装验证脚本**（不需要`pip install`，Day1在受限网络环境里就是靠这两个验证的）：

```bash
python scripts/check_llm_key.py              # 验证.env里的DeepSeek/GLM Key能不能真的调通
PYTHONPATH=. python scripts/smoke_test_nodes.py   # 验证intake校验/评分占位逻辑/SQLite读写
```

- **完整链路测试（已在训练服务器上跑通，含真实DeepSeek调用+真实评分模型+真实RAG检索）**：

```bash
PYTHONPATH=. python scripts/e2e_graph_test.py
```

这个脚本会：提交一篇正常长度的示例作文走完整个Graph（intake→retrieval→scoring→grammar→feedback→coach→progress），断言反馈/建议非空、SQLite正确写入；再提交一篇过短作文验证被正确短路拒绝。**如果`models/essay-scorer-*/v1`或`data/processed/chroma_kb`不存在，`scoring_tool_node`/`retrieval_agent_node`会自动降级回启发式占位逻辑**（不会报错崩溃），所以这个脚本在只装了依赖、还没训练模型的机器上也能跑，只是评分部分是占位值，跑完之后对照日志确认是不是拿到了真实模型的结果还是降级结果。

- `streamlit run app.py` 手动跑一遍界面同样必要（脚本测试不了UI交互本身），见第6节。
- **端到端手动测试清单**（Day3~4联调时逐项过）：
  - [ ] 提交一篇明显高分作文，检查评分、反馈、雷达图是否合理。
  - [ ] 提交一篇有明显语法问题的作文，检查`GrammarCheckNode`是否能识别出对应错误并在反馈中体现。
  - [ ] 提交一篇过短/无意义文本，检查是否被`IntakeValidatorNode`正确拒绝并给出提示。
  - [ ] 同一账号连续提交2~3篇作文，检查"历史进步仪表盘"趋势图是否正确更新。
  - [ ] 断网/API Key失效场景下，检查前端是否有合理报错提示而不是直接崩溃（决定是否需要为答辩现场加一层fallback）。

## 8. 部署（已确认：SSH部署至自有服务器）

- 目标服务器：`121.41.238.92`，用户`root`，端口22，私钥登录，本机SSH别名`deploy-server`（配置在`~/.ssh/config`，`IdentityFile ~/.ssh/id_rsa`，已测试连通）。**这是Day4的最终部署机，和用于训练的`retinascope-server`是两台不同的机器，不要混淆**。
- **这台机器不是空的，是共用服务器，部署前必须知道这些**（已实测确认）：
  - 根分区`40G`总容量，部署前只剩`9.3G`可用、装完全部Python依赖后剩约`6.2G`——够用但不宽裕，注意不要在这台机器上跑模型训练或存大量数据。
  - **内存只有1.6G，比磁盘更容易踩坑**：加载一次微调DistilBERT模型要占约800MB常驻内存，Streamlit常驻服务已经占了一份，这时候如果再起一个进程跑验证脚本会触发OOM killer（本轮部署时真实发生过，`dmesg`能看到`Out of memory: Killed process`记录，且内存打满时`sshd`会响应迟缓、表现成SSH连接长时间"banner exchange超时"，容易误判成网络问题）。**要跑加载模型的验证脚本，必须先精确PID停掉Streamlit，跑完再重启**。
  - **端口`80`、`8080`、`8501`、`8502`已经被占用**，其中`8501`是一个叫`ophthalmic-ai`的Docker容器（`docker ps`显示"Up 2 months (healthy)"，看内容像是田溯开另一个已上线的医疗项目），**绝对不要碰这个容器**（参考`RUNNING.md`「0.5」和`CLAUDE.md`里记录的pkill误杀生产容器的教训，这台机器上必须更谨慎）。我们的应用要用别的端口，见下方命令里已经改成了`8503`（当前实测空闲，正式部署前建议再用`ss -tlnp`确认一遍没被占用）。
  - **云安全组默认没放通8503**：即使服务器本机`curl localhost:8503`返回200，外网也访问不了，这一步和服务器本机的`iptables`/`ufw`无关，是阿里云ECS控制台的安全组规则没放行，只能登录控制台加一条TCP 8503入站规则，SSH改不了。**本轮已经放通并验证过外网可访问**。
  - Docker本身是装好的（29.4.1），如果想用容器化部署也可以，但没有现成的nginx。
- 部署方式（**已实际执行过，代码在`/root/sukai/`，不是之前草稿写的`/root/huibi/`**）：

```bash
# 1. 把代码同步到服务器（本地开发机没有rsync，用tar+scp代替，排除.git/.venv/__pycache__/.env）
tar --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='.env' -czf huibi_deploy.tar.gz .
scp huibi_deploy.tar.gz deploy-server:/root/huibi_deploy.tar.gz
ssh deploy-server "mkdir -p /root/sukai && cd /root/sukai && tar xzf /root/huibi_deploy.tar.gz && rm /root/huibi_deploy.tar.gz"
# 注意：这个tar包会带上models/下的真实权重文件（.gitignore排除了它们，但部署必须要真实权重才能
# 不降级成占位启发式评分，所以特意不用--exclude-from=.gitignore整个排除，只排除.git/.venv这些）

# 2. 登录服务器，安装依赖（deploy-server无GPU，torch要装CPU-only版本，否则pip默认拉CUDA版体积大很多）
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

- **部署状态：已完成，外网实测通过**（`curl http://121.41.238.92:8503`返回200，`scripts/e2e_graph_test.py`在部署环境里单独跑过一遍完整通过）。
- 仍然建议：答辩前从答辩现场实际网络再实测一次`http://121.41.238.92:8503`（校园网/外网限制、防火墙规则可能和开发者所在网络不一样），并准备好`RUNNING.md`第7节提到的离线演示预案兜底。
- 安全提醒：服务器用`root`直接部署仅为4天工期图快，如果这个项目之后要长期运行/给更多人用，建议改成非root部署用户；私钥文件本身任何时候都不要提交进仓库或粘贴进文档。
