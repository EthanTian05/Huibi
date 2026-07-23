"""慧笔三页应用共享的原创视觉样式与顶部导航。"""
from __future__ import annotations

import html

import streamlit as st


# 色系参考essay.art（雅思/托福写作批改同类产品）的品牌蓝#1165A4重新校准，
# 原来的#165DFF偏鲜艳靛蓝，改成更沉稳、更贴近教育/考试类产品调性的深蓝，
# 具体数值来自essay.art官网CSS里`--tw-bg-opacity`的`essayPrimary`色值，不是
# 凭印象取色；PRIMARY_LIGHT是它的10%不透明度叠加在白底上的计算结果。
PRIMARY = "#1165A4"
PRIMARY_DARK = "#0D4C7B"
PRIMARY_LIGHT = "#E7F0F6"
BG = "#F5F7FA"
TEXT = "#1D2129"
TEXT_SECONDARY = "#86909C"

# 卡片边框/阴影原来是带品牌蓝色调的（`#E7EEF9`边框、`rgba(17,65,148,x)`阴影），
# 这轮参照essay.art实测的中性灰阴影（`box-shadow:0 1px 10px rgba(0,0,0,.1),
# 0 2px 15px rgba(0,0,0,.05)`）和中性灰边框改掉，阴影层次也从单层大范围
# 模糊改成essay.art那种"贴近卡片的窄阴影+更远的浅阴影"两层叠加，视觉上更扁平、
# 不那么"发光"。BORDER/CARD_SHADOW是共享token，新增卡片一律引用这两个变量，
# 不要再写字面量色值，否则以后再调色系又要满文件找。
BORDER = "#E5E7EB"
CARD_SHADOW = "0 1px 2px rgba(15, 23, 42, 0.04), 0 4px 16px rgba(15, 23, 42, 0.06)"

PAGE_MAX_WIDTH = "1200px"

THEME_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, .stApp {{
        font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto,
            'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
    }}

    /* 主题基色由.streamlit/config.toml的[theme]固定成浅色（base="light"），
       不再依赖这里的CSS去覆盖背景色——之前只用CSS强制浅色背景、没固定
       Streamlit自己的主题基色，深色模式的系统/浏览器下会出现"浅色背景+
       浅色文字"看不清的问题，见CLAUDE.md本轮记录。这里只做卡片/按钮这些
       自定义组件的样式，不再覆盖Streamlit原生组件的背景色。 */

    /* 三个页面都用layout="wide"（避免Streamlit默认"centered"约730px太窄，
       多列卡片布局会挤在一起），但宽屏显示器上"wide"会让内容铺满整个浏览器
       宽度，行长得离谱、很不美观（用户实测反馈）。这里改成居中定宽容器，
       比默认"centered"宽（能放下反馈卡片的多列布局），比铺满窄，视觉上接近
       主流SaaS产品的做法。 */
    .block-container {{
        max-width: {PAGE_MAX_WIDTH};
        margin: 0 auto;
        padding-top: 2rem;
    }}

    /* Hero改成essay.art那种"纯页面背景+居中大标题"，不再用色块/渐变卡片——
       essay.art首页从上到下都是同一个浅色背景，标题靠字号/字重本身撑住
       视觉重量，不靠色块。h1里的品牌名前缀用`.hb-hero-accent`套一层品牌蓝，
       呼应essay.art"Essay.Art:雅思/托福/GRE写作批改专家"这种"品牌名高亮+
       其余黑字"的标题写法。 */
    .hb-hero {{
        text-align: center;
        padding: 48px 20px 8px;
        margin: 0 auto;
        max-width: 760px;
    }}
    .hb-hero h1 {{
        font-size: 2.6rem;
        font-weight: 800;
        line-height: 1.3;
        margin-bottom: 14px;
        color: {TEXT} !important;
    }}
    .hb-hero-accent {{ color: {PRIMARY} !important; }}
    .hb-hero p {{
        font-size: 1.08rem;
        color: {TEXT_SECONDARY} !important;
        max-width: 640px;
        margin: 0 auto;
    }}
    /* "核心优势"这类功能卡片，仿essay.art实际的卡片布局——左对齐标题+正文，
       一个小图标徽章放在卡片右上角（essay.art用的是具体产品logo图标，这里
       用emoji代替，不抓取对方素材），不是essay.art改版前HuiBi自己用的
       "数字编号（01/02/03/04）+居中"那一版设计。 */
    .hb-card {{
        position: relative;
        background: #FFFFFF;
        border-radius: 16px;
        padding: 28px 26px;
        box-shadow: {CARD_SHADOW};
        height: 100%;
        border: 1px solid {BORDER};
    }}
    .hb-card h4 {{
        color: {TEXT} !important;
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0 0 10px;
        padding-right: 36px;
    }}
    .hb-card p {{
        color: {TEXT_SECONDARY} !important;
        font-size: 0.92rem;
        line-height: 1.7;
        margin: 0;
    }}
    .hb-badge {{
        position: absolute;
        top: 24px;
        right: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: {PRIMARY_LIGHT};
        color: {PRIMARY} !important;
        border-radius: 9px;
        font-size: 1rem;
    }}
    /* 主按钮的"平面硬阴影"效果仿essay.art的CTA按钮观感（官网CSS里能查到
       box-shadow: 5px 5px #1165a4这种无模糊、纯色偏移的阴影写法）——按压时
       阴影收窄、按钮位移到贴住阴影，比默认Streamlit按钮的扁平样式更有
       "可点击"的实体感，颜色沿用上面校准过的品牌蓝。 */
    div.stButton > button[kind^="primary"], div[data-testid="stFormSubmitButton"] > button[kind^="primary"] {{
        background-color: {PRIMARY};
        border-color: {PRIMARY};
        border-radius: 8px;
        box-shadow: 4px 4px 0 {PRIMARY_DARK};
        transition: transform .12s ease, box-shadow .12s ease, background-color .15s ease;
    }}
    div.stButton > button[kind^="primary"], div[data-testid="stFormSubmitButton"] > button[kind^="primary"]:hover {{
        background-color: {PRIMARY_DARK};
        border-color: {PRIMARY_DARK};
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0 {PRIMARY_DARK};
    }}
    div.stButton > button[kind^="primary"], div[data-testid="stFormSubmitButton"] > button[kind^="primary"]:active {{
        transform: translate(0, 0);
        box-shadow: 2px 2px 0 {PRIMARY_DARK};
    }}
    div.stButton > button {{
        border-radius: 8px;
    }}
    section[data-testid="stSidebar"] {{
        border-right: 1px solid #F0F1F3;
    }}
    /* 输入框/标签/tabs显式给对比色，双重保险——万一某些浏览器扩展
       （比如Dark Reader之类的强制深色插件）在config.toml之外又做了一层
       颜色反转，这里的!important规则能保住最基本的可读性。 */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {{
        background-color: white !important;
        color: {TEXT} !important;
    }}
    .stTextInput label, .stTextArea label, .stNumberInput label,
    .stRadio label, .stSlider label {{
        color: {TEXT} !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {TEXT} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {TEXT} !important;
    }}
    .hb-nav-brand {{
        font-size: 1.25rem;
        font-weight: 800;
        color: {PRIMARY_DARK};
        letter-spacing: -0.02em;
        padding-top: 8px;
    }}
    /* 首页Hero下方的"benefit checklist"，仿essay.art"十年留学从业经验积累"
       这几条——浅灰底圆角横条+绿色勾选图标，不是简单的markdown项目符号。 */
    .hb-check-pill {{
        display: flex;
        align-items: center;
        gap: 10px;
        background: #F7F8FA;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
        font-weight: 600;
        color: {TEXT} !important;
    }}
    .hb-check-pill-icon {{
        color: #16A34A !important;
        font-weight: 800;
        flex-shrink: 0;
    }}
    /* 章节标题居中，仿essay.art"核心优势"这类章节标题的排版——大字号、
       粗体、居中，副标题也居中且和标题之间留出明显的呼吸空间。 */
    .hb-section-title {{
        font-size: 2rem;
        font-weight: 800;
        color: {TEXT} !important;
        text-align: center;
        margin: 56px 0 10px;
    }}
    .hb-section-subtitle {{
        color: {TEXT_SECONDARY} !important;
        text-align: center;
        margin-bottom: 32px;
    }}
    .hb-metric {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 16px 18px;
    }}
    .hb-metric b {{ color: {PRIMARY} !important; font-size: 1.45rem; }}
    /* 工作台顶部欢迎条/账号卡原来是暖色调渐变卡片，这轮统一改成和其它卡片
       一致的中性白底+灰边框+浅阴影，不再单独用一套暖色语言——essay.art
       全站没有出现过这种"欢迎横幅"式的彩色大色块。 */
    .hb-workbench-hero {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 24px 28px;
        margin: 8px 0 20px;
        box-shadow: {CARD_SHADOW};
    }}
    .hb-account-card {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 26px 22px 16px;
        min-height: 144px;
        text-align: center;
        color: {TEXT_SECONDARY} !important;
        box-shadow: {CARD_SHADOW};
    }}
    .hb-account-card b {{
        color: {TEXT} !important;
        font-size: 1.05rem;
    }}
    .hb-workbench-hero h1 {{
        color: {TEXT} !important;
        font-size: 1.7rem;
        margin: 0 0 8px;
    }}
    .hb-workbench-hero p {{
        color: {TEXT_SECONDARY} !important;
        margin: 0;
    }}
    .hb-learning-note {{
        background: #FFF9EE;
        border-left: 4px solid #FFB45C;
        border-radius: 8px;
        color: #6D5434 !important;
        padding: 10px 14px;
        margin: 8px 0 16px;
    }}
    /* 产品页收尾的"准备好了吗"CTA区，仿essay.art"联系我们"那块浅色调大圆角
       面板——essay.art用浅蓝灰底把收尾区和上面的白底卡片区分开，这里同样
       用一块比页面背景更深一点的浅灰底，不用essay.art那种蓝紫色调。 */
    .hb-closing-panel {{
        background: #F7F8FA;
        border-radius: 20px;
        padding: 40px 32px;
        margin: 48px 0 24px;
        text-align: center;
    }}
    .hb-closing-panel h2 {{
        color: {TEXT} !important;
        font-size: 1.5rem;
        margin: 0 0 8px;
    }}
    .hb-closing-panel p {{
        color: {TEXT_SECONDARY} !important;
        margin: 0;
    }}
    div[data-testid="stMetric"] {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: {CARD_SHADOW};
    }}
    div[data-testid="stRadio"] [role="radiogroup"] {{
        background: #F7F8FA;
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 6px 12px;
        gap: 10px;
        width: 100%;
    }}
    div[data-testid="stRadio"] {{ width: 100% !important; }}
    div[data-testid="stRadio"] label {{
        padding: 6px 10px;
        border-radius: 9px;
        flex: 1 1 0;
        justify-content: center;
        white-space: nowrap;
    }}
    div[data-testid="stDataFrame"] {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid {BORDER};
    }}
    div[data-testid="stVegaLiteChart"] {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: {CARD_SHADOW};
    }}
    details[data-testid="stExpander"] {{
        background: #FFFFFF;
        border: 1px solid {BORDER} !important;
        border-radius: 16px !important;
        box-shadow: {CARD_SHADOW};
    }}
    div[data-testid="stForm"] {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 18px;
    }}
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stTextArea"] > div,
    div[data-testid="stTextInput"] > div {{
        border-radius: 12px;
    }}
    /* 导航按钮（🏠产品页/👤用户名/📝工作台）之前在窄一点的容器里会被截断——
       Streamlit给`stPageLink`的默认样式在某些版本里带`overflow`/文字省略号
       行为，图标+中文文字放在偏窄的列里会显示不全。这里强制不换行、不裁切，
       宁可让按钮宽度撑开也不截断文字，同时给足内边距。 */
    div[data-testid="stPageLink"] {{
        overflow: visible !important;
    }}
    /* 页内CTA用的page_link（比如产品页"开始使用慧笔"）保持essay.art那种
       实心蓝色圆角按钮观感——essay.art首页"立即批改雅思/托福/GRE"就是这个
       样式。顶部导航（下面`.st-key-hb-topnav`那组规则）会覆盖成纯文字链接，
       两者共用`stPageLink`这个组件、靠外层容器的key区分，不是同一套样式。 */
    div[data-testid="stPageLink"] a {{
        background: {PRIMARY};
        border: 1px solid {PRIMARY};
        border-radius: 9px;
        padding: 0.5rem 1.1rem;
        justify-content: center;
        color: white !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
        min-width: -moz-fit-content;
        min-width: fit-content;
        transition: background-color .15s ease, transform .15s ease;
    }}
    div[data-testid="stPageLink"] a p,
    div[data-testid="stPageLink"] a span {{
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }}
    div[data-testid="stPageLink"] a:hover {{
        background: {PRIMARY_DARK};
        border-color: {PRIMARY_DARK};
        color: white !important;
        transform: translateY(-1px);
    }}
    div[data-testid="stPageLink"] a * {{
        color: white !important;
    }}
    /* 顶部导航改成essay.art那种纯文字链接（无背景色块），当前页用加粗+
       品牌蓝表示"active"，非当前页hover时也只变色不变背景——`render_top_nav()`
       用`st.container(key="hb-topnav")`包住整行，Streamlit据此生成
       `st-key-hb-topnav`这个类名，靠它把导航区和页内其它CTA按钮的page_link
       区分开，不用改`render_top_nav()`本身的按钮逻辑。 */
    .st-key-hb-topnav div[data-testid="stPageLink"] a {{
        background: transparent;
        border: none;
        color: {TEXT} !important;
        font-weight: 500;
        padding: 0.4rem 0.3rem;
        box-shadow: none;
    }}
    .st-key-hb-topnav div[data-testid="stPageLink"] a * {{
        color: {TEXT} !important;
    }}
    .st-key-hb-topnav div[data-testid="stPageLink"] a:hover {{
        background: transparent;
        color: {PRIMARY} !important;
        transform: none;
    }}
    .st-key-hb-topnav div[data-testid="stPageLink"] a:hover * {{
        color: {PRIMARY} !important;
    }}
    .st-key-hb-topnav div[data-testid="stPageLink"] a[aria-disabled="true"],
    .st-key-hb-topnav div[data-testid="stPageLink"] a[aria-disabled="true"] * {{
        color: {PRIMARY} !important;
        font-weight: 700;
    }}
    /* 定性反馈卡片（render_feedback_dimensions）：每个评分维度一张卡，
       优势点/建议改进的方面用虚线分隔的小节，"关于如何改进"的具体小贴士
       用浅蓝底的mini卡片，视觉上和上面的.hb-card保持同一套语言。 */
    .hb-dim-card {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow: {CARD_SHADOW};
        margin-bottom: 18px;
        /* 同一行左右两张卡内容长度常常不一样，靠height:100%让卡片撑满
           Streamlit那一行stHorizontalBlock（默认flex+stretch）分给它的
           整个高度，用空白把矮的卡片"垫"到和另一张一样高，而不是内容对齐。 */
        height: calc(100% - 18px);
    }}
    /* 同一条规则同时覆盖"定性反馈"两两一行的卡片和"作文原文+分数"左右两栏——
       两处都是靠子元素height:100%撑满Streamlit那一行stHorizontalBlock分到的
       高度实现对齐，但Streamlit的列(stColumn)默认不是flex容器，height:100%
       在非flex的auto高度父级里不生效，必须先把列强制成flex（默认row方向，
       交叉轴是纵向，子元素才会按align-items:stretch的默认值纵向撑满）。 */
    div[data-testid="stHorizontalBlock"]:has(.hb-dim-card) > div[data-testid="stColumn"],
    div[data-testid="stHorizontalBlock"]:has(.hb-essay-panel) > div[data-testid="stColumn"] {{
        display: flex;
    }}
    div[data-testid="stHorizontalBlock"]:has(.hb-dim-card) [data-testid="stMarkdownContainer"],
    div[data-testid="stHorizontalBlock"]:has(.hb-dim-card) div[data-testid="stMarkdown"],
    div[data-testid="stHorizontalBlock"]:has(.hb-essay-panel) [data-testid="stMarkdownContainer"] {{
        width: 100%;
    }}
    /* 分数列比反馈卡片列复杂一点：列里除了`.hb-score-panel`这块markdown，
       后面还接着一个真正的Streamlit`st.button`（"写一篇新作文"），两者要
       纵向堆叠、且整列要撑满到和左边作文原文面板一样高，按钮贴在最底部——
       所以这一列的stVerticalBlock要用flex-direction:column，让
       `.hb-score-panel`用flex:1把按钮之外的高度全部占满。 */
    div[data-testid="stHorizontalBlock"]:has(.hb-essay-panel) > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {{
        width: 100%;
        display: flex;
        flex-direction: column;
    }}
    .hb-dim-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.08rem;
        font-weight: 700;
        color: {TEXT} !important;
        margin-bottom: 14px;
    }}
    .hb-dim-icon {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: {PRIMARY};
        color: white !important;
        font-size: 0.8rem;
        flex-shrink: 0;
    }}
    .hb-dim-block {{
        padding: 8px 0 12px;
        border-bottom: 1px dashed {BORDER};
    }}
    .hb-dim-block:last-of-type {{ border-bottom: none; }}
    .hb-dim-block-label {{
        color: {PRIMARY} !important;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 4px;
    }}
    .hb-dim-block-text {{
        color: {TEXT} !important;
        font-size: 0.92rem;
        line-height: 1.6;
        margin: 0;
    }}
    .hb-dim-improve-title {{
        display: flex;
        align-items: center;
        gap: 8px;
        color: {PRIMARY_DARK} !important;
        font-weight: 700;
        margin: 16px 0 10px;
    }}
    .hb-dim-tip {{
        background: {PRIMARY_LIGHT};
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }}
    .hb-dim-tip:last-child {{ margin-bottom: 0; }}
    .hb-dim-tip-title {{
        color: {PRIMARY_DARK} !important;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 4px;
    }}
    .hb-dim-tip-comment, .hb-dim-tip-example {{
        color: {TEXT} !important;
        font-size: 0.88rem;
        margin: 2px 0;
    }}
    .hb-dim-tip-example b {{ color: {TEXT_SECONDARY} !important; }}

    /* 个性化修改建议与练习推荐（render_coach_plan）：故意用和上面反馈卡片
       （蓝色系.hb-dim-card）不一样的视觉语言——暖色调+左侧色条+编号/图标
       徽标，让"评价类卡片"和"行动类卡片"一眼能区分开。 */
    .hb-action-card, .hb-exercise-card {{
        display: flex;
        gap: 14px;
        align-items: flex-start;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }}
    .hb-action-card {{
        background: linear-gradient(180deg, #FFFDF8 0%, #FFF9EF 100%);
        border: 1px solid #F3E3C7;
        border-left: 4px solid #FFB45C;
    }}
    .hb-exercise-card {{
        background: linear-gradient(180deg, #F7FFFC 0%, #EFFAF5 100%);
        border: 1px solid #CDEEE0;
        border-left: 4px solid #2FBF8F;
    }}
    .hb-plan-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 28px;
        height: 28px;
        border-radius: 50%;
        color: white !important;
        font-weight: 700;
        font-size: 0.85rem;
        flex-shrink: 0;
    }}
    .hb-action-card .hb-plan-badge {{ background: #FFB45C; }}
    .hb-exercise-card .hb-plan-badge {{ background: #2FBF8F; }}
    .hb-plan-title {{
        font-weight: 700;
        margin-bottom: 3px;
    }}
    .hb-action-card .hb-plan-title {{ color: #6D5434 !important; }}
    .hb-exercise-card .hb-plan-title {{ color: #1F6E56 !important; }}
    .hb-plan-detail {{
        color: {TEXT} !important;
        font-size: 0.92rem;
        line-height: 1.6;
        margin: 0;
    }}

    /* 高分范文卡（AI现场创作，不是真实考生作文，样式做成"阅读卡片"的观感，
       和上面两类卡片再拉开一层区分度）。 */
    .hb-essay-card {{
        background: linear-gradient(160deg, #FCFAF4 0%, #F7F2E7 100%);
        border: 1px solid #E9DFC4;
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 12px;
        box-shadow: 0 8px 26px rgba(140, 110, 40, 0.08);
    }}
    .hb-essay-badge {{
        display: inline-block;
        background: #B8873A;
        color: white !important;
        border-radius: 999px;
        padding: 2px 12px;
        font-size: 0.76rem;
        font-weight: 600;
        margin-bottom: 10px;
    }}
    .hb-essay-title {{
        font-size: 1.15rem;
        font-weight: 700;
        color: #4A3B1F !important;
        margin-bottom: 12px;
    }}
    .hb-essay-text {{
        color: #3A3020 !important;
        font-size: 0.95rem;
        line-height: 1.85;
        white-space: pre-wrap;
        margin-bottom: 14px;
    }}
    .hb-essay-highlight-title {{
        color: #8C6E28 !important;
        font-weight: 700;
        font-size: 0.9rem;
        margin: 10px 0 6px;
    }}
    .hb-essay-highlight {{
        color: #4A3B1F !important;
        font-size: 0.88rem;
        line-height: 1.6;
        margin: 2px 0;
    }}

    /* "写作批改"合并页（原"提交批改"+"反馈详情"两个tab）：题目卡+作文原文/
       分数左右两栏，视觉上参照essay.art风格重新设计，不是抓取/复制对方代码，
       颜色/圆角沿用本项目已有的PRIMARY蓝+卡片语言，只是布局思路借鉴。 */
    .hb-topic-card {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 22px 26px;
        margin-bottom: 18px;
        box-shadow: {CARD_SHADOW};
    }}
    .hb-topic-header {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.05rem;
        font-weight: 700;
        color: {TEXT} !important;
        margin-bottom: 10px;
    }}
    .hb-topic-badge {{
        display: inline-block;
        background: #FFF1E0;
        color: #B8622C !important;
        border-radius: 999px;
        padding: 2px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 10px;
    }}
    .hb-topic-text {{
        color: {TEXT} !important;
        font-size: 0.95rem;
        line-height: 1.7;
        white-space: pre-wrap;
        margin: 0;
    }}
    .hb-essay-panel {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 22px 26px;
        box-shadow: {CARD_SHADOW};
        height: 100%;
    }}
    .hb-essay-panel-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
    }}
    .hb-essay-panel-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {TEXT} !important;
    }}
    .hb-word-count-badge {{
        background: #F4F7FC;
        color: {TEXT_SECONDARY} !important;
        border-radius: 999px;
        padding: 2px 12px;
        font-size: 0.8rem;
    }}
    .hb-essay-body {{
        color: {TEXT} !important;
        font-size: 0.95rem;
        line-height: 2;
        white-space: pre-wrap;
    }}
    .hb-highlight {{
        background: transparent;
        border-bottom: 2px solid #FFB45C;
        text-decoration: none;
        cursor: help;
        padding-bottom: 1px;
    }}
    .hb-score-panel {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 28px 24px;
        text-align: center;
        box-shadow: {CARD_SHADOW};
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        /* flex:1（而不是height:100%）：这个面板和"写一篇新作文"按钮共享
           同一个纵向flex列，面板要负责把按钮之外的剩余高度全部撑满，让
           按钮的底边正好落在和左边作文原文面板一样的Y坐标，见下面
           `:has(.hb-essay-panel)`那组选择器。 */
        flex: 1;
    }}
    .hb-score-panel-body {{
        display: flex;
        flex-direction: column;
    }}
    .hb-score-note {{
        color: {TEXT_SECONDARY} !important;
        font-size: 0.78rem;
        line-height: 1.5;
        text-align: left;
        margin: 10px 0 0;
        padding-top: 10px;
        border-top: 1px dashed {BORDER};
    }}
    .hb-score-number {{
        font-size: 3rem;
        font-weight: 800;
        color: {PRIMARY} !important;
        line-height: 1;
    }}
    .hb-score-max {{
        font-size: 1.3rem;
        font-weight: 600;
        color: {TEXT_SECONDARY} !important;
    }}
    .hb-score-label {{
        color: {TEXT_SECONDARY} !important;
        font-size: 0.95rem;
        margin: 6px 0 18px;
    }}
    .hb-score-secondary {{
        color: {TEXT_SECONDARY} !important;
        font-size: 0.85rem;
        margin-bottom: 12px;
    }}
    .hb-score-summary {{
        color: {TEXT} !important;
        font-size: 0.9rem;
        line-height: 1.7;
        text-align: left;
        margin: 0;
    }}
    .hb-grammar-card {{
        display: flex;
        gap: 10px;
        align-items: flex-start;
        background: #FFF7F5;
        border: 1px solid #FBDCD3;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }}
    .hb-grammar-icon {{
        color: #E5484D !important;
        font-weight: 700;
        flex-shrink: 0;
    }}
    .hb-grammar-context {{
        color: {TEXT} !important;
        font-size: 0.86rem;
        line-height: 1.5;
        margin: 0 0 4px;
    }}
    .hb-grammar-message {{
        color: #C4432B !important;
        font-size: 0.82rem;
        margin: 0;
    }}
    .hb-grammar-suggestion {{
        color: {TEXT_SECONDARY} !important;
        font-size: 0.82rem;
        margin-top: 2px;
    }}
    .hb-footer {{
        text-align: center;
        color: {TEXT_SECONDARY} !important;
        font-size: 0.8rem;
        padding: 28px 0 12px;
        margin-top: 24px;
        border-top: 1px solid #EDF1F7;
    }}

</style>
"""


def inject_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_feedback_dimensions(feedback_dimensions: dict) -> None:
    """把结构化的按维度反馈渲染成卡片（优势点/建议改进的方面/关于如何改进的
    小贴士），"写作批改"页（原"反馈详情"）和历史记录详情复用同一份渲染逻辑。

    ``feedback_dimensions``里的文本内容最终来自LLM生成（间接受用户提交的
    作文正文影响），用`unsafe_allow_html=True`拼HTML前必须逐项`html.escape()`，
    否则如果LLM输出恰好包含尖括号之类的字符，会破坏卡片的HTML结构，
    严重时构成存储型XSS。维度名（label）来自`src/agents/nodes.py`/
    `src/official_rubrics.py`里固定的中文映射表，不是LLM可控内容，不需要转义，
    但为了这个函数本身不必假设调用方一定守规矩，也一并转义。
    """
    if not feedback_dimensions:
        return
    # 之前用一个`st.columns(2)`给全部4张卡复用（按index%2分左右列），
    # Streamlit的每一列是独立纵向堆叠的容器，左列第2张卡的起始高度取决于
    # 左列第1张卡多高，右列同理——内容长度不一样时，两列的卡片高度错开，
    # 视觉上第二排看起来"没对齐"。改成每两张卡单独开一行`st.columns(2)`，
    # 让每一行都是一次新的水平布局，行与行之间不再互相拖累；同一行内两张
    # 卡高度不同的部分靠`.hb-dim-card`的`height: 100%`（配合Streamlit列的
    # flex容器默认stretch行为）用留白撑平，而不是内容本身对齐。
    items = list(feedback_dimensions.items())
    for row_start in range(0, len(items), 2):
        row_items = items[row_start : row_start + 2]
        columns = st.columns(2)
        for column, (label, dim) in zip(columns, row_items):
            with column:
                parts = [
                    '<div class="hb-dim-card">',
                    f'<div class="hb-dim-header"><span class="hb-dim-icon">✓</span>{html.escape(label)}</div>',
                ]
                if dim.get("strengths"):
                    parts.append(
                        '<div class="hb-dim-block"><div class="hb-dim-block-label">优势点</div>'
                        f'<p class="hb-dim-block-text">{html.escape(dim["strengths"])}</p></div>'
                    )
                if dim.get("improvements"):
                    parts.append(
                        '<div class="hb-dim-block"><div class="hb-dim-block-label">建议改进的方面</div>'
                        f'<p class="hb-dim-block-text">{html.escape(dim["improvements"])}</p></div>'
                    )
                tips = dim.get("tips") or []
                if tips:
                    parts.append('<div class="hb-dim-improve-title">⬆ 关于如何改进</div>')
                    for tip in tips:
                        tip_html = (
                            '<div class="hb-dim-tip">'
                            f'<div class="hb-dim-tip-title">{html.escape(tip.get("title", ""))}</div>'
                        )
                        if tip.get("comment"):
                            tip_html += f'<p class="hb-dim-tip-comment">{html.escape(tip["comment"])}</p>'
                        if tip.get("example"):
                            tip_html += (
                                f'<p class="hb-dim-tip-example"><b>示例：</b>{html.escape(tip["example"])}</p>'
                            )
                        tip_html += "</div>"
                        parts.append(tip_html)
                parts.append("</div>")
                st.markdown("".join(parts), unsafe_allow_html=True)


def render_coach_plan(coach_plan: dict) -> None:
    """渲染"个性化修改建议与练习推荐"+"高分范文"，视觉上和
    `render_feedback_dimensions()`的评价类卡片区分开（暖色调行动卡+
    独立的范文阅读卡），对应`src/agents/nodes.py`的`coach_agent_node`/
    `build_coach_plan()`产出的结构。转义规则同`render_feedback_dimensions()`：
    所有文本内容间接来自LLM生成，拼HTML前必须`html.escape()`防XSS。
    """
    if not coach_plan:
        return

    action_items = coach_plan.get("action_items") or []
    if action_items:
        st.markdown("##### 优先修改清单")
        for index, item in enumerate(action_items, start=1):
            st.markdown(
                '<div class="hb-action-card">'
                f'<span class="hb-plan-badge">{index}</span>'
                '<div>'
                f'<div class="hb-plan-title">{html.escape(item.get("title", ""))}</div>'
                f'<p class="hb-plan-detail">{html.escape(item.get("detail", ""))}</p>'
                "</div></div>",
                unsafe_allow_html=True,
            )

    exercises = coach_plan.get("exercises") or []
    if exercises:
        st.markdown("##### 针对性练习")
        for index, item in enumerate(exercises, start=1):
            st.markdown(
                '<div class="hb-exercise-card">'
                f'<span class="hb-plan-badge">✎</span>'
                '<div>'
                f'<div class="hb-plan-title">{html.escape(item.get("title", ""))}</div>'
                f'<p class="hb-plan-detail">{html.escape(item.get("instruction", ""))}</p>'
                "</div></div>",
                unsafe_allow_html=True,
            )

    model_essay = coach_plan.get("model_essay") or {}
    if model_essay.get("text"):
        st.markdown("##### 高分范文")
        parts = [
            '<div class="hb-essay-card">',
            '<span class="hb-essay-badge">AI现场创作 · 仅供参考，非真实考生作文</span>',
        ]
        if model_essay.get("title"):
            parts.append(f'<div class="hb-essay-title">{html.escape(model_essay["title"])}</div>')
        parts.append(f'<div class="hb-essay-text">{html.escape(model_essay["text"])}</div>')
        highlights = model_essay.get("highlights") or []
        if highlights:
            parts.append('<div class="hb-essay-highlight-title">✦ 这篇范文值得学习的地方</div>')
            for highlight in highlights:
                parts.append(f'<p class="hb-essay-highlight">- {html.escape(highlight)}</p>')
        parts.append("</div>")
        st.markdown("".join(parts), unsafe_allow_html=True)


def render_topic_card(exam_type: str | None, essay_topic: str | None, exam_subtype: str | None = None) -> None:
    """"写作批改"合并页顶部的题目卡，仿essay.art的题目展示区。"""
    subtype_text = f" · {html.escape(exam_subtype)}" if exam_subtype else ""
    parts = ['<div class="hb-topic-card">', f'<div class="hb-topic-header">📋 题目{subtype_text}</div>']
    if exam_type:
        parts.append(f'<span class="hb-topic-badge">{html.escape(exam_type)}</span>')
    parts.append(f'<p class="hb-topic-text">{html.escape(essay_topic or "未填写")}</p></div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_essay_with_highlights(essay_text: str, grammar_errors: list[dict]) -> None:
    """作文原文面板：按`grammar_errors`的`position`区间给对应片段加下划线高亮，
    悬停可看到具体问题（用原生`title`属性做tooltip，不引入额外JS），仿
    essay.art的逐句批注效果。

    `position`来自`grammar_check_node`的正则匹配结果，理论上不重叠，但这里
    仍然做了防御性处理（越界/重叠区间直接跳过），避免一条脏数据拼出破损的
    HTML或让整个页面渲染失败。
    """
    word_count = len(essay_text.split())
    parts = [
        '<div class="hb-essay-panel">',
        '<div class="hb-essay-panel-header">'
        '<span class="hb-essay-panel-title">作文原文</span>'
        f'<span class="hb-word-count-badge">words: {word_count}</span></div>',
        '<div class="hb-essay-body">',
    ]

    text_len = len(essay_text)
    spans = []
    last_end = 0
    for error in sorted(grammar_errors or [], key=lambda e: (e.get("position") or [0, 0])[0]):
        position = error.get("position") or []
        if len(position) != 2:
            continue
        start, end = position
        if not (isinstance(start, int) and isinstance(end, int)):
            continue
        if start < last_end or start < 0 or end > text_len or end <= start:
            continue
        spans.append((start, end, error))
        last_end = end

    cursor = 0
    for start, end, error in spans:
        parts.append(html.escape(essay_text[cursor:start]))
        tooltip = html.escape(str(error.get("message", "")))
        if error.get("suggestion"):
            tooltip += f"  建议：{html.escape(str(error['suggestion']))}"
        parts.append(f'<mark class="hb-highlight" title="{tooltip}">{html.escape(essay_text[start:end])}</mark>')
        cursor = end
    parts.append(html.escape(essay_text[cursor:]))
    parts.append("</div></div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def _fmt_score(value) -> str:
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return "—"


def render_score_panel(result: dict, notes: list[str] | None = None) -> None:
    """右侧分数面板：主分数大字号+总体评价段落，仿essay.art的"Overall Score"卡。

    ``notes``（免责声明/权重说明这类小字footnote）本轮改成拼进卡片HTML内部，
    不再用独立的`st.caption()`调用——因为分数面板要靠CSS的flex拉伸和左边的
    作文原文面板顶部/底部对齐（见`render_top_nav`旁边的`:has()`选择器说明），
    如果`st.caption`留在卡片外面，拉伸只会拉伸卡片本身、caption仍然会拖出去
    一截，两边就对不齐了；把说明文字放进卡片内部，让卡片当唯一会撑高的
    容器，才能让"写一篇新作文"按钮之外的整块内容和作文面板顶/底对齐。
    """
    primary_score, primary_max = result.get("primary_score"), result.get("primary_max")
    parts = ['<div class="hb-score-panel">', '<div class="hb-score-panel-body">']
    if primary_score is not None and primary_max:
        parts.append(
            f'<div class="hb-score-number">{_fmt_score(primary_score)}'
            f'<span class="hb-score-max">/{_fmt_score(primary_max)}</span></div>'
        )
        parts.append(f'<div class="hb-score-label">{html.escape(result.get("primary_label") or "本次评分")}</div>')
    secondary_score, secondary_max = result.get("secondary_score"), result.get("secondary_max")
    if secondary_score is not None and secondary_max:
        parts.append(
            f'<div class="hb-score-secondary">{html.escape(result.get("secondary_label") or "辅助分")}：'
            f'{_fmt_score(secondary_score)}/{_fmt_score(secondary_max)}</div>'
        )
    overall_summary = result.get("overall_summary") or ""
    if overall_summary:
        parts.append(f'<p class="hb-score-summary">{html.escape(overall_summary)}</p>')
    parts.append("</div>")
    for note in notes or []:
        parts.append(f'<p class="hb-score-note">{html.escape(note)}</p>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_grammar_error_cards(grammar_errors: list[dict]) -> None:
    """语法/用词问题卡片网格，替代原来单一的`st.dataframe`表格，仿essay.art
    "词汇及语法错误批注"区域的小卡片观感。"""
    if not grammar_errors:
        st.caption("未检测到规则库覆盖范围内的问题")
        return
    columns = st.columns(3)
    for index, error in enumerate(grammar_errors):
        with columns[index % 3]:
            suggestion_html = ""
            if error.get("suggestion"):
                suggestion_html = f'<div class="hb-grammar-suggestion">建议：{html.escape(str(error["suggestion"]))}</div>'
            st.markdown(
                '<div class="hb-grammar-card">'
                '<span class="hb-grammar-icon">✗</span>'
                "<div>"
                f'<p class="hb-grammar-context">{html.escape(str(error.get("context", "")))}</p>'
                f'<p class="hb-grammar-message">{html.escape(str(error.get("message", "")))}</p>'
                f"{suggestion_html}"
                "</div></div>",
                unsafe_allow_html=True,
            )


def render_top_nav(active: str) -> None:
    """三页应用共用的顶部导航；不依赖被折叠的Streamlit侧边栏。

    上一轮`use_container_width=True`会把按钮强行拉伸到撑满整个列宽——在
    页面收窄到`1360px`之后，列本身仍然分到了不小的宽度，"拉伸到撑满列"
    反而让按钮变成了和文字内容完全不成比例的大色块（用户截图反馈的
    "按钮界面还是没有显示出来"，准确说是"按钮显示得不对/很怪"）。改成
    `use_container_width=False`让按钮按内容自身宽度渲染，列宽也相应收窄，
    避免大片空白被强制染色。
    """
    with st.container(key="hb-topnav"):
        brand, product, login, workspace = st.columns([1.7, 0.85, 0.95, 0.85])
        with brand:
            st.markdown('<div class="hb-nav-brand">✦ 慧笔 HuiBi</div>', unsafe_allow_html=True)
        with product:
            st.page_link("app.py", label="产品页", icon="🏠", disabled=active == "product", use_container_width=False)
        with login:
            if st.session_state.get("logged_in") and st.session_state.get("username"):
                st.page_link(
                    "pages/2_工作台.py",
                    label=st.session_state["username"],
                    icon="👤",
                    disabled=active == "workspace",
                    use_container_width=False,
                )
            else:
                st.page_link("pages/1_登录.py", label="登录", icon="🔐", disabled=active == "login", use_container_width=False)
        with workspace:
            st.page_link("pages/2_工作台.py", label="工作台", icon="📝", disabled=active == "workspace", use_container_width=False)
    st.divider()


def render_footer() -> None:
    """三页应用共用的页脚版权信息，放在每个页面内容的最下方。"""
    st.markdown(
        '<div class="hb-footer">Developed by S. K. Tian</div>',
        unsafe_allow_html=True,
    )
