# CLAUDE.md
> Use advisor and dynamic workflow globally
> 本文件是项目工作说明，**每次在这个仓库里开始任务前必须先读一遍**。
> 进度记录见 `Docs/02-Progress.md`；待办清单见 `Docs/TODO.md`；怎么跑起来/测试见 `Docs/03-RUNNING.md`。
> 更新md文件要精炼，避免冗余。

## 工作方式

- **多用 `advisor` 工具**：开始实质性改动前、以及完成一轮工作后都确认一次，不要闷头写完再汇报。
- **动态迭代**：需求是滚动式的（反馈→改→再反馈），不要预先规划完"整个项目"再一次性执行。收到反馈用 `TodoWrite` 拆成小项逐个做；有歧义的地方按合理判断处理，但要在汇报里说明是自己的理解。
- 每轮做完后把改了什么写进 `Docs/02-Progress.md`（小标题+根因+改法+验证方式，不要"改好了"这种空话）。不是字面唯一解的取舍，除了汇报里说明，也要在 `Docs/TODO.md`"需要你决策"里留一条。

## 项目是什么

**慧笔（HuiBi）——基于LangChain+LangGraph的英语写作智能批改与个性化学习伴学智能体**

面向中国英语学习者（通用英语写作/雅思/托福场景）的多智能体写作辅导工具。提交一篇英语作文，系统给出：

1. 量化评分——LLM结合对应考试的公开评分量表给出结构化对照分（雅思Band Descriptors/托福ETS单题评分指南/GENERAL四维度标准，见`src/official_rubrics.py`）。打分固定走DeepSeek V4 Pro（见`src/agents/llm.py`的`get_scoring_chat_model()`），和定性反馈共用同一个主模型；
2. 结构化定性反馈——多个LLM Agent协作生成（语法纠错、结构建议、用词建议，中英双语）。grammar维度接了LanguageTool公共API（比本地正则规则库更准），language维度可以自主调用词典API核实具体用词；
3. 雅思Task 1图表/图片描述题——上传图片后先用GLM-4V-Flash（云端免费视觉模型）做客观描述，再用这份描述核对作文数据是否准确、按Task Achievement量表打分；
4. 个性化学习闭环——结合历史提交记录，给出学习趋势图和针对性练习推荐。

项目起源于"绍兴大学-大模型实训"课程的4人4天小组项目，**实训已结束，现在是按自己节奏维护的独立项目，不再受课程要求/加分项/答辩时限约束**。架构设计见 `Docs/01-系统架构与Agent设计.md`。

当前进度：

- **运行方式：纯本地，不部署到服务器**——之前有一版SSH部署到自有服务器的方案，现在不需要了，相关信息挪到下方"服务器部署（备用，当前不用）"存档，以后要用再捡回来。
- **技术路线调整**：量化评分不再用自训练模型，产品收窄为GENERAL/IELTS/TOEFL三种考试类型，打分固定用DeepSeek V4 Pro（曾经默认走本地Ollama，用户实测判断后确认取消，见`Docs/02-Progress.md`最新记录）。
- **全部真实跑通、不是占位**：LangGraph全链路（intake→image_analysis→retrieval→grammar→feedback→critic→coach→progress）→ PostgreSQL持久化，反馈/评分都是真实LLM生成，不是mock；已经用能pip install的`.venv-uv`环境+本地真实Postgres/DeepSeek/GLM视觉API跑通过一整轮真实端到端验证，不是只做过语法检查。
- **`CriticAgentNode`反思循环已实现**：`feedback_agent`产出定性反馈后，`critic_agent`复核一次（空泛套话/自相矛盾/建议不可执行则打回`feedback_agent`重写，封顶1次重试），见下方"已确认的设计决策"。
- **本地环境限制**：本仓库开发环境`pip install`用不了（SSLEOFError，见"环境信息"），完整验证需要在能pip install的环境上做。

代码推送到`https://github.com/EthanTian05/Huibi.git`（`main`分支）。

## 目录结构

```
01-源代码/
├── CLAUDE.md
├── .streamlit/config.toml     强制固定浅色主题（base="light"），和src/ui_theme.py保持一致
├── .env                       真实密钥（gitignore）；.env.example为占位模板
├── data/kb/                   RAG知识库源Markdown，含exam_rubrics/（GENERAL/IELTS/TOEFL专属细则，IELTS/TOEFL基于官方公开量表原文）
├── src/
│   ├── agents/                 state.py/llm.py/nodes.py/graph.py，LangGraph全链路
│   │   ├── tools.py             LLM自主调用的工具（dictionary_lookup，依赖langchain_core）
│   │   └── grammar_tools.py     语法检查确定性工具（languagetool_check，零依赖，供免pip的smoke test用）
│   ├── official_rubrics.py     GENERAL/IELTS(Task1+Task2)/TOEFL的公开评分量表定义+LLM结果解析
│   ├── rag/                    build_kb.py，把data/kb/下Markdown embedding进本地Chroma
│   ├── storage/                db.py，PostgreSQL读写+登录注册（PBKDF2密码哈希）
│   ├── ui_theme.py             Streamlit样式注入
│   └── exam_types.py           考试类型 -> 专属rubric文件映射，含IELTS_SUBTYPES（Task1/Task2）
├── pages/2_工作台.py           登录后功能页（提交批改/反馈详情/历史仪表盘/知识库问答）
├── scripts/
│   ├── check_llm_key.py       免pip，验证.env里的LLM Key
│   ├── smoke_test_nodes.py    免pip，验证节点逻辑（不含数据库，db.py需要psycopg）
│   └── e2e_graph_test.py      完整端到端验证（含数据库读写），需要pip环境+本地PostgreSQL在跑
├── app.py                      入口=产品介绍页+登录注册
├── README.md / requirements.txt / .env.example
```

`Docs/`：`01-系统架构与Agent设计.md`（架构/Agent/RAG设计）、`02-Progress.md`（工作记录）、`03-RUNNING.md`（环境/运行/测试）、`TODO.md`（待办+待决策）。

## 怎么跑起来 / 怎么测试

严格按 `Docs/03-RUNNING.md` 执行；运行方式变了要同步改这份文档。

不需要`pip install`：

```bash
python scripts/check_llm_key.py
PYTHONPATH=. python scripts/smoke_test_nodes.py
```

需要`pip install -r requirements.txt`（本地这个开发环境`pip`本身用不了，见"环境信息"，改用`uv pip install -r requirements.txt --python .venv-uv`）；跑之前确认：本地PostgreSQL已启动（`pg_ctl start`，见"环境信息"）：

```bash
PYTHONPATH=. .venv-uv/Scripts/python.exe scripts/e2e_graph_test.py
.venv-uv/Scripts/python.exe -m streamlit run app.py
```

## 不要重新踩的坑

- 不要为了"看起来花哨"堆砌过多Agent节点/循环——核心链路（校验→检索→反馈→辅导→进步追踪）够用，加`CriticAgentNode`反思循环也是因为用户明确要求，不是自己主动加的花哨功能；加的时候同样管住范围，只加了1个节点+封顶1次重试的循环，没有连锁加更多层复核。
- **真实密钥一律只进`.env`，不进`Docs/*.md`**：之前发生过真实API Key被粘贴进`Docs/TODO.md`，已清理并补了`.gitignore`。协作分发Key走口头/私聊，不要写进Markdown或`git add .env`。
- **DeepSeek V4系列是推理模型，`max_tokens`给小了会拿到空字符串**：先输出`reasoning_content`再输出`content`，预算不够时`content`为空、`finish_reason="length"`，容易误判成Key错了。`src/agents/llm.py`的`DEFAULT_MAX_TOKENS=2048`，改之前先用`scripts/check_llm_key.py`验证。
- **这个开发环境`pip install`会失败（SSLEOFError）但curl/urllib正常**：是pip自己的HTTP连接被重置，不是网络/Key问题，见`Docs/03-RUNNING.md`排查记录。
- **`grammar_check_node`用纯Python正则规则库，没用`language_tool_python`**：后者要打包Java版LanguageTool（200MB+下载+需要装Java），改用零依赖正则库（`src/agents/nodes.py`）。
- **GLM的视觉模型不要默认选`glm-4.6v-flash`，实测限流严重**：真实调用连续返回`HTTP 429`（"该模型当前访问量过大"），换成`glm-4v-flash`（少个`.6`）同一个Key、同一张测试图立刻调通、识图也准确（真实读出了折线图的数值/趋势/交叉点）。`GLM_VISION_MODEL_NAME`默认值已经是`glm-4v-flash`，如果以后想换更新的视觉模型先小范围测一下别直接切默认值。
- **`src/agents/tools.py`顶部有`from langchain_core.tools import tool`，任何被免pip的`smoke_test_nodes.py`路径（比如`grammar_check_node`）间接import这个文件都会在没装langchain的环境里直接`ModuleNotFoundError`**：语法检查要用的`languagetool_check`因此单独放进了零依赖的`src/agents/grammar_tools.py`，不要图省事把新的确定性工具塞进`tools.py`，先想清楚这个工具会不会被"不需要pip install"的节点路径调用到。同样的道理，`src/storage/db.py`改用PostgreSQL后顶部有`import psycopg`，`nodes.py`不能在模块顶部`from src.storage import db`，改成懒加载在`progress_tracker_node()`函数体内import（这是目前唯一用到db的节点）。
- **`langchain_core`的`@tool`装饰器要求被装饰函数必须有docstring**：没写docstring会在真实调用（不是import）时抛`ValueError: Function must have a docstring if description not provided.`，纯代码审查发现不了，这个环境之前一直没装成langchain所以从来没真的跑到这行代码。`src/agents/tools.py`的`dictionary_lookup`已经补上文档字符串（写清楚这个工具是干什么用、什么时候该调用），新增LLM自主调用的工具时记得加。
- **`bind_tools()`同时配`response_format={"type":"json_object"}`时，每个工具的function schema必须`strict=True`**：不满足会在真实调用时抛`` ValueError: `xxx` is not strict. Only `strict` function tools can be auto-parsed ``（openai SDK的结构化输出auto-parse路径要求的），不写会静默走某个更早的代码路径、工具实际从没被真正调用过，报错本身反而是"终于发现问题"的信号。`feedback_agent_node`/`coach_agent_node`两处`bind_tools([...], strict=True)`都要保留这个参数。
- **打分LLM偶发漏掉rubric量表要求的某个JSON键**：曾经用本地`qwen2.5:7b`打分时实测到过（4次里3次正确返回`task_achievement`等四个键，1次漏了），会导致`normalize_rubric_result()`因缺字段抛`ValueError`、`score_error`非空、`primary_score`为`None`。`feedback_agent_node`的打分调用因此保留了最多重试1次的逻辑（同一个prompt重跑一次，命中"缺字段"就重试而不是直接判失败），换成DeepSeek V4 Pro后这个问题概率更低，但重试逻辑本身作为防御性代码没有删除。改这类重试逻辑时留意：`normalize_rubric_result()`本身可以当验证器用（拿到JSON后直接调一次，异常就重试，不用等到最终合并`feedback_payload`之后才发现缺字段、错过重试窗口）。
- **`src/ui_theme.py`的按钮颜色/阴影改了但真机不生效，根因是两处"看起来对但没生效"的坑，headless测试（AppTest/字符串断言）测不出来，必须真机截图+`getComputedStyle()`才发现**：①`.streamlit/config.toml`的`[theme] primaryColor`是Streamlit原生渲染`st.button`/`st.form_submit_button`这类控件的真实颜色来源，`src/ui_theme.py`里的自定义CSS只是覆盖层——两处颜色值必须手动保持同步，改`PRIMARY`常量时如果忘了同步改`primaryColor`，Streamlit原生颜色会读到旧值，且因为`ui_theme.py`的CSS选择器可能根本没匹配上（见下一条），旧颜色会"顶着新代码"继续显示，容易误判成"改动没生效/进程没重启"。②`st.form_submit_button(type="primary")`渲染出来的`kind`属性是`"primaryFormSubmit"`，不是`"primary"`——`div.stButton > button[kind="primary"]`这类精确匹配的选择器选不中表单按钮，登录/注册页的按钮因此从来没吃到过自定义样式。改按钮相关CSS时选择器要用`button[kind^="primary"]`（前缀匹配，同时覆盖`primary`和`primaryFormSubmit`），且表单按钮的直接父级是`div[data-testid="stFormSubmitButton"]`而不是`div.stButton`，两种父级选择器都要覆盖。
- **这个环境里Git-Bash的`lsof -ti:PORT | xargs kill`杀不干净Windows原生子进程（比如`streamlit run`），会让同一个端口下堆积多个"僵尸"进程**：`netstat`有时甚至会同时显示好几个PID都在`LISTENING`同一个端口（不同代际的进程堆叠），而Bash的`kill`对这类进程经常静默失败、不报错但也没真的杀掉，导致"重启服务生效"的验证前提本身是假的。可靠做法是用PowerShell：`Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {$_.CommandLine -match '关键词'}`列出真实PID，`Stop-Process -Id <PID> -Force`精确杀掉，`Get-NetTCPConnection -LocalPort <PORT>`确认端口上不再有多余的监听者，再重新启动验证。

## 已确认、不要再改的设计决策

- 项目题目：慧笔（HuiBi）。
- LLM推理后端：定性反馈/辅导建议/知识库问答走主力DeepSeek V4 Pro，免费兜底GLM-4.7-Flash（`get_chat_model_with_fallback()`）。**打分固定用DeepSeek V4 Pro**（`get_scoring_chat_model()`直接复用`get_primary_chat_model()`），曾经默认走本地Ollama（`qwen2.5:7b`）已确认取消，不再需要本地模型依赖。**起源课程要求里的"预训练模型-微调"/"自定义构建模型"两项目前没有对应代码了**，实训已结束不再需要维护。
- 前端部署框架：Streamlit，纯本地运行（`streamlit run app.py`），不部署到服务器——服务器部署信息存档见下方"服务器部署（备用，当前不用）"。
- Embedding模型：开源本地`BAAI/bge-small-en-v1.5`，见`src/rag/build_kb.py`。
- 产品差异化模块：学习进步仪表盘+自适应练习推荐的持续学习闭环。
- 前端结构：`app.py`（介绍页+登录注册）+`pages/2_工作台.py`（登录后功能页）。登录用`src/storage/db.py`的PBKDF2密码哈希（不是bcrypt/argon2，够用于当前阶段，非生产级）。视觉风格参考企业AI平台通用设计语言自行重新设计，非抓取复制，样式代码在`src/ui_theme.py`。
- "提交批改"页考试类型下拉框（GENERAL/IELTS/TOEFL）：`src/exam_types.py`映射到专属评分细则文件（`data/kb/exam_rubrics/{general,ielts,toefl}.md`）。量化评分统一来自LLM+公开量表，`st.caption`已提示这是模拟评阅、不代表官方成绩。
- "写作知识库问答"页调用`src/agents/nodes.py`的`answer_kb_question()`，不走完整`build_graph()`。
- **雅思Task 1图片理解和量化打分/定性反馈是两次独立调用**：`image_analysis_node`（新增的LangGraph节点，只在`essay_image_b64`非空时真正调用GLM-4V-Flash，否则原样透传state）先把图表内容转成一段客观文字描述，`SCORE_RUBRIC_PROMPT`/`FEEDBACK_ONLY_PROMPT`再把这段描述作为"图片内容描述"注入prompt——打分/反馈模型全程看不到原图，只能依据这段描述判断作文数据是否准确。这个设计的原因：DeepSeek的对外API目前（2026-07）不支持图片输入（只有网页版chat.deepseek.com支持），所以图片理解必须单独拆出来，不能和打分/反馈合并成一次多模态调用。
- **`feedback_agent_node`的定性反馈调用绑了`dictionary_lookup`工具**：和`coach_agent_node`同样的写法（`get_primary_chat_model().bind_tools(...)`，不和`get_chat_model_with_fallback()`的fallback链一起用，因为没实测过两者组合的行为），language维度写反馈时可以自主决定要不要查词；grammar维度改成读`grammar_check_node`产出的真实检测结果（本地正则+LanguageTool），不再让LLM自己重新通读一遍猜测有没有语法问题。
- **打分prompt加了few-shot校准示例**：`SCORE_RUBRIC_PROMPT`按`exam_type`/`exam_subtype`只塞1条相关示例（GENERAL/TOEFL/IELTS Task2/IELTS Task1各一条，见`src/agents/nodes.py`的`_SCORE_FEW_SHOT_EXAMPLES`），不会把四种类型的示例都塞进同一个prompt，控制token开销。示例的作用是校准打分尺度（避免笼统作文给太高分、或对语法小瑕疵扣分过重），不是解决JSON格式问题——那个已经靠`normalize_rubric_result()`提前校验+重试1次解决了。
- **`CriticAgentNode`反思循环**：`feedback_agent`产出定性反馈后，新增的`critic_agent`节点复核一次（判断是否空泛套话/总体评价和维度反馈自相矛盾/建议不可执行），不合格则由`graph.py`的`route_after_critic()`打回`feedback_agent`重新生成，**封顶1次重试**（`state["critic_revision_count"]`达到1后无条件放行，不是无限循环）。只复核定性反馈，不复核数值评分——打分已经有自己的"缺字段重试"机制，评分对错更适合靠公开量表本身的客观描述约束。**已知的效率取舍**：`feedback_agent_node`没有拆出"只重跑反馈、复用上一轮分数"的路径，critic触发重写时打分会跟着重新调用一次DeepSeek（多一次调用），因为要实现"只重跑反馈"需要在state里额外缓存原始英文键的`rubric_scores`（当前只保留转成中文展示名之后的`score_details`，无法逆向还原），复杂度换来的收益不成正比，且这条重试路径本身封顶1次，接受这个成本。反馈本身生成失败（`feedback_dimensions`为空）时`critic_agent_node`直接放行，不会对着空反馈瞎评价。
- **雅思Task 1图片持久化到本地文件系统，数据库只存路径**：`src/storage/db.py`的`save_submission()`收到`essay_image_b64`时会解码写入`data/uploads/<uuid>.<ext>`（`data/uploads/`已gitignore），`submissions`表新增`essay_image_path`/`image_analysis`两列只存路径和图片理解文字描述，不直接存base64大字段。`delete_submission()`删记录时连带删本地文件，避免孤儿文件累积。历史详情页（`pages/2_工作台.py`）读到路径后用`st.image()`直接从磁盘渲染。
- **`data/kb/exam_rubrics/{ielts,toefl}.md`收录的是IELTS/TOEFL官方评分量表的逐字原文**：IELTS用British Council公开版Writing Task 1&2 Band Descriptors（`takeielts.britishcouncil.org`），TOEFL用ETS官方Writing Scoring Guide（`ets.org/pdfs/toefl/`三份PDF：Write an Email、Writing for an Academic Discussion、Integrated Writing），都是通过WebFetch真实下载PDF后逐字转录，不是凭记忆转述或AI生成的近似内容。`general.md`没有对应的单一官方考试，基于已有的`src/official_rubrics.py`GENERAL四维度框架扩展成教学向内容（每维度的常见扣分点/提分建议），不冒充官方标准。
- **持久化用本地PostgreSQL，不是SQLite**：`src/storage/db.py`已从SQLite全部改写成`psycopg`v3连PostgreSQL（本机`scoop install postgresql`装的，trust本地认证）。原因：SQLite够用但"正规关系型数据库"是用户明确要求换的方向；顺带用上了PostgreSQL原生`JSONB`类型（`score_details`/`feedback_dimensions`/`coach_plan`等字段），`psycopg`v3会自动做Python dict↔JSONB双向转换，不用手动`json.dumps`/`json.loads`。表结构里已经删掉了`essay_prompt_id`/`quant_score`/`trait_scores`三个死列（只有已删除的自训练AB模型才写这几列）。生产库`huibi`、测试脚本专用`huibi_test`两个库分开，`e2e_graph_test.py`跑之前会`TRUNCATE`掉`huibi_test`，不影响`huibi`里的真实数据。

## 环境信息

- Windows 11；PowerShell为主；本地Python为Miniconda 3.9.1。
- git远程：`https://github.com/EthanTian05/Huibi.git`，分支`main`。`.env`/`.venv/`已确认未被追踪。
- **本地`pip install`用不了，但`uv`可以，绕过了这个环境限制**：`pip install -r requirements.txt`报`SSLEOFError`，怀疑是这个sandbox网络环境对pip的连接模式不友好；`uv venv --python 3.11 .venv-uv && uv pip install -r requirements.txt --python .venv-uv`实测能完整装完全部依赖（含torch/transformers/streamlit/langgraph），`uv`甚至能自己下载一份Python 3.11解释器，不依赖本机Miniconda 3.9.1。**`.venv-uv/`是这个环境专用的真实可用venv，之前"需要pip环境才能跑"的`scripts/e2e_graph_test.py`/`streamlit run app.py`现在可以直接用`.venv-uv/Scripts/python.exe`在本机跑了**，不用再假设"这台机器测不了"。`.venv-uv/`已在`.gitignore`排除（本地产物，不提交）。
- `.env`里有`DEEPSEEK_API_KEY`/`GLM_API_KEY`（已验证）、`POSTGRES_HOST`/`PORT`/`DB`/`USER`/`PASSWORD`（本地数据库连接）等。
- **本地PostgreSQL**：`scoop install postgresql`装的18.4版，trust本地认证，超级用户`postgres`空密码，用之前先`pg_ctl start`（scoop装的服务不会自动开机启动）。已建好`huibi`（生产）和`huibi_test`（`scripts/e2e_graph_test.py`测试专用，跑之前会自动`TRUNCATE`，不影响`huibi`）两个库，建表逻辑（`CREATE TABLE IF NOT EXISTS`）在`db.get_connection()`里，首次连接自动建表，不需要手动跑SQL。
- **含中文字符的`.ps1`必须存成带BOM的UTF-8**：不带BOM时Windows PowerShell 5.1会按系统ANSI代码页解析，把中文注释解码错、连带搞乱后续语法，报出看似无关的错误。用`[System.IO.File]::WriteAllText(path, content, (New-Object System.Text.UTF8Encoding $true))`重新保存即可。
- **Streamlit自定义CSS要同步固定主题基色，否则深色模式下"浅色背景+浅色文字"看不清**：只用CSS写死背景色不够，Streamlit原生组件仍走系统深色配色。修复：`.streamlit/config.toml`用`[theme] base="light"`强制浅色主题（只在启动时读取，改完要重启才生效）。
- **Streamlit多页应用里，页面顶部的模块级import不能依赖本地没装的重依赖**：曾经`pages/2_工作台.py`顶部直接`from src.agents.graph import build_graph`，导致页面一执行就因`ModuleNotFoundError`崩溃、登录校验形同虚设，且`curl`测HTTP 200测不出来（只拿静态HTML外壳）。修复：把这类import挪到真正用到的代码块里（懒加载），登录校验和普通tab切换不需要重依赖。
- **浏览器自动化工具：Playwright已装进`.venv-uv`（`uv pip install playwright --python .venv-uv`+`.venv-uv/Scripts/python.exe -m playwright install chromium`）**，用来真机验证Streamlit前端改动（截图、`getComputedStyle()`读实际渲染出的CSS值），不是产品运行依赖，**没有写进`requirements.txt`**。这个环境没有`chromium-cli`（那是特定托管环境才有的封装，本机是普通Windows开发机，`npm`/`pip`能装的公开工具才装得到），改用Playwright的Python sync API直接写脚本驱动。浏览器二进制缓存在`C:\Users\<user>\AppData\Local\ms-playwright\`，不受这个仓库`.gitignore`管，也不需要管（不在项目目录内）。

## 服务器部署（备用，当前不用）

现在纯本地运行，不部署到服务器；以下信息存档，以后要重新部署时参考，具体步骤见`Docs/03-RUNNING.md`"部署"节（同样标注为备用）。

- 目标服务器`121.41.238.92`（SSH别名`deploy-server`，阿里云ECS，Ubuntu 24.04，40G磁盘无GPU，内存仅1.6G），代码曾部署在`/root/sukai/`，端口固定用`8503`（`8501`/`80`/`8080`/`8502`被同机器其他服务占用，部署前务必先`docker ps`+`ss -tlnp`确认无冲突）。
- **共用服务器上停止进程只能用精确PID，绝不能`pkill -f`模式匹配**：曾经`pkill -f 'streamlit run app.py'`误杀了同机器上另一个团队的生产容器。一律`ps aux | grep <关键词>`看清PID，只`kill <精确PID>`。
- `retinascope-server`原是训练自训练模型用的GPU服务器，模型已删除，现在只在需要一个能`pip install`的环境跑`e2e_graph_test.py`时才可能用得到。
