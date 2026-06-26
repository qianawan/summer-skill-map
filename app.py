"""
准大学生暑假技能地图 — AI 生成个性化大学前暑假规划
"""
import streamlit as st
import json
import os
import requests

st.set_page_config(
    page_title="准大学生暑假技能地图",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Config ──────────────────────────────────────────
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

# Init session state for API key (env var → sidebar → demo fallback)
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("DEEPSEEK_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))


def get_api_key():
    """动态读取 API Key：侧边栏 > 环境变量 > 空"""
    return st.session_state.api_key or os.getenv("ANTHROPIC_API_KEY", "")

# ── Prompt template ─────────────────────────────────
def build_prompt(major, school, interests, goal, hobbies):
    return f"""你是一位资深的大学学业规划师和职业发展顾问。请为一位即将进入大学的新生生成一份详细的「大学前暑假规划 + 大学四年路线图」。

学生信息：
- 录取专业：{major}
- 录取学校：{school if school else '未知'}
- 个人兴趣：{interests if interests else '未填写'}
- 业余爱好：{hobbies if hobbies else '未填写'}
- 目标方向：{goal}

请用中文输出，按以下结构组织：

## ☀️ 暑假三个月规划（7月 / 8月 / 9月）
每个月列出 3-5 件具体可执行的事，分为「学习」「技能」「生活」三类。

## 🎯 大学四年路线图
大一到大四，每年列出核心任务和关键节点（保研/考研/留学/就业四条路径任选其一，以学生目标为主）。

## 🧰 本专业必备技能清单
列出 5-8 项硬技能 + 3-5 项软技能，每项一句话说明为什么重要。

## 📚 推荐资源
- 书籍 2-3 本
- 在线课程 2-3 个（Coursera/B站/网易公开课等）
- 值得关注的UP主/博主 1-2 个
- 实用的 AI 工具 2-3 个

## ⚠️ 避坑提醒
3 条本专业新生最容易踩的坑。

格式要求：用 Markdown，不要多余的开场白和结束语，直接输出内容。"""


def call_ai(prompt):
    """调用 DeepSeek API（OpenAI 兼容格式）"""
    api_key = get_api_key()
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "max_tokens": 3000,
        "temperature": 0.7,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=body, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            detail = resp.json().get("error", {}).get("message", resp.text)
            st.error(f"API 返回 {resp.status_code}: {detail[:500]}")
            return None
    except Exception as e:
        st.error(f"请求失败: {e}")
        return None


def generate_demo(major, school, goal):
    """生成演示版内容（未配置 API 时使用）"""
    return f"""## ☀️ 暑假三个月规划

### 📅 7月：放松 + 建立节奏
- **学习**：每天 30 分钟英语（四级听力 + 百词斩），保持语感不归零
- **技能**：学会 Office 三件套（Word 排版、PPT 制作、Excel 基础函数）—— 大学交作业必备
- **生活**：考驾照（科目一刷题走起）、来一次说走就走的毕业旅行

### 📅 8月：入门专业知识
- **学习**：在 B 站搜「{major} 导论」，花 10 小时建立专业基本认知框架
- **技能**：注册 Coursera / 中国大学 MOOC，选 1 门专业入门课试水
- **生活**：加学校新生群、专业群，提前认识学长学姐（信息差决定大学体验）

### 📅 9月：开学准备 + 心态建设
- **学习**：准备英文自我介绍（必用），了解专业培养方案和选课规则
- **技能**：学会用 AI 工具辅助学习（注册 Claude/ChatGPT，学会提问）
- **生活**：整理行李清单，准备 1 个才艺/兴趣点（社团面试加分项）

---

## 🎯 大学四年路线图

> 目标：**{goal}**

| 年级 | 核心任务 | 关键节点 |
|------|---------|---------|
| 大一上 | 适应节奏 + 稳住 GPA + 过四级 | 加入 1-2 个有价值的社团/实验室 |
| 大一下 | 通过六级 + 探索专业方向 | 暑假找第一份实习或科研入门 |
| 大二 | 专业核心课 + 竞赛/项目经历 | 确定{goal}路径，开始针对性准备 |
| 大三上 | {goal}核心准备期 | 语言考试 / 科研论文 / 实习经历 |
| 大三下 | 冲刺期 | 夏令营 / 申请季 / 秋招 |
| 大四 | 收尾 + 过渡 | 毕业设计 + 入职/入学准备 |

---

## 🧰 本专业必备技能清单

### 硬技能
1. **编程基础（Python）** —— 无论什么专业，会写脚本处理数据都是降维打击
2. **数据分析（Excel + SQL）** —— 从数据中提取结论，是所有岗位的通用能力
3. **AI 工具使用** —— Claude/ChatGPT 是你的 24h 助教，越早学会提问越好
4. **学术写作** —— 论文、报告、申请文书，写作能力决定你的天花板
5. **专业软件** —— 根据 {major} 方向，提前了解行业标准工具

### 软技能
1. **信息检索能力** —— 知道怎么找答案比知道答案更重要
2. **公开表达** —— 课堂展示、竞赛路演、面试，都要开口讲
3. **时间管理** —— 大学没人管你，自律就是竞争力

---

## 📚 推荐资源

| 类型 | 推荐 |
|------|------|
| 📖 书籍 | 《把时间当作朋友》李笑来、《如何阅读一本书》、《认知觉醒》 |
| 🎓 课程 | B站「{major}导论」、Coursera「Learning How to Learn」、中国大学MOOC |
| 📺 UP主 | 取景框看世界（大学规划）、壹课（Office教程） |
| 🤖 AI工具 | Claude（深度思考）、ChatGPT（日常问答）、Notion AI（笔记整理） |

---

## ⚠️ 避坑提醒

1. **别信"大学就是玩"** —— GPA 从大一第一学期就开始累计，挂科影响保研/留学/就业
2. **别只闷头学专业课** —— 实习经历、项目作品、竞赛拿奖比高分更值钱
3. **别在宿舍里社交** —— 走出宿舍，社团/实验室/比赛才是遇贵人的地方

---

> ⚡ 以上由 AI 生成，仅供参考。**适合你的才是最好的。**

📢 觉得有用？分享给你的同学或在社交媒体上 @我，就是最好的支持。
"""


# ── UI ─────────────────────────────────────────────
st.title("🗺️ 准大学生暑假技能地图")
st.caption("高考结束了，接下来三个月做什么？输入你的专业，AI 帮你定制专属规划。")

# ── Input form ──────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    major = st.text_input("📚 录取专业", placeholder="例如：计算机科学、电子信息工程、新闻传播...")
    school = st.text_input("🏫 录取学校（选填）", placeholder="例如：浙江大学")
    interests = st.text_input("💡 个人兴趣方向", placeholder="例如：人工智能、短视频创作、游戏开发...")
with col2:
    hobbies = st.text_input("🎨 业余爱好", placeholder="例如：摄影、打篮球、写小说...")
    goal = st.selectbox("🎯 大学目标", ["还不确定", "保研", "考研", "留学", "直接就业"])

st.divider()

# ── Generate button ────────────────────────────────
if st.button("🚀 生成我的专属规划", type="primary", use_container_width=True):
    if not major:
        st.warning("至少填写专业名称哦～")
    else:
        with st.spinner("AI 正在为你定制规划..."):
            prompt = build_prompt(major, school, interests, goal, hobbies)

            if get_api_key():
                result = call_ai(prompt)
                if result:
                    st.success("✅ AI 定制版已生成！")
                    st.markdown(result)
                else:
                    st.info("AI 暂时无法连接，以下是基于模板的演示版本 ↓")
                    st.markdown(generate_demo(major, school, goal))
            else:
                st.info("💡 未配置 AI API Key，显示演示版本。配置后可获得 AI 深度定制规划。")
                st.markdown(generate_demo(major, school, goal))

# ── Footer ────────────────────────────────────────────
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 14px;">
    📱 小红书 <b>@lunairestudio</b> · 🐙 GitHub <b>oliviawann</b>
    </div>
    """, unsafe_allow_html=True)

# ── Sidebar info ────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 配置 AI API Key")
    st.caption("使用 DeepSeek / Claude / OpenAI 等 API")
    api_key_input = st.text_input("API Key", type="password",
                                   placeholder="sk-...")
    if api_key_input:
        st.session_state.api_key = api_key_input
        os.environ["ANTHROPIC_API_KEY"] = api_key_input
        st.success("✅ 已配置")

    st.divider()
    st.markdown("### 🔗 找到我")
    st.markdown("""
    📱 小红书 **@lunairestudio**
    🐙 GitHub **oliviawann**
    """)
