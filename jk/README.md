后端FASTAPI依赖
```cmd
pip install fastapi uvicorn python-multipart
```
### 专业技能
具体细节：技能名称 
抽象评级：基于关键词加权计算技能深度评分（0-5）

### 证书要求
证书名称

### 学历要求
最低学历
专业方向（可空）

### 工作/实习经验
最低年限
工作领域

### 沟通能力
具体描述
评分（按照能力的大小）

### 抗压能力
具体描述
评分（抗压系数，直观）

### 学习能力
方向
评分
### 创新能力
方向
评分
### 团队协作能力



## 界面
### 基于AI的大学生职业规划智能体
#### 主界面

现在有一个招聘信息的xlsx文件，里面有许多列，其中两列分别为“岗位名称”、“省”。现在想使用ts和react-simple-maps设计一个Web前端界面，用户可选择岗位（从已有岗位中选择，一次只能选择一个），选择岗位并确认后会读取xlsx文件将所有这个岗位的省在GeoJSON地图(本地文件“china.json”放在public的map文件夹中)上标记出来，以方便用户直观的看到岗位在全国的分布情况。若“省”这一列为空则跳过，若存在省相同的情况，则以不同颜色的标记来直观感受数量多少（从绿到红渐变）且让数量更多的标记比数量更少的标记稍大，对数量占比大于10%的标记，添加一个脉动外圈，吸引用户注意力。鼠标悬停时标记会轻微放大（onMouseEnter 增加半径），提升交互感。给出完整可运行的.css和.tsx代码

现在想使用ts设计一个 “基于AI的大学生职业规划智能体” Web前端，用户可在输入栏中输入想给智能体发的消息。用户还可拖拽或者读取本地文件上传pdf简历，上传后会从这个pdf简历中提取结构化数据显示在右边供用户查看、添加与修改，对于右边的简历结构化信息栏用户可选则收起或者展开。点击发送后会将用户的消息和简历结构化信息通过后端接口传给数据处理模型，所以这部分只需要设计接口就行，模型我自己接入。给出完整可运行的.css和.tsx代码。
注意环境为：
{
  "name": "front_proj",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@types/d3-geo": "^3.1.0",
    "d3-geo": "^3.1.1",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-simple-maps": "^3.0.0",
    "xlsx": "^0.18.5"
  },
  "devDependencies": {
    "@eslint/js": "^9.39.4",
    "@types/node": "^24.12.2",
    "@types/react": "^18.3.18",
    "@types/react-dom": "^18.3.5",
    "@types/react-simple-maps": "^3.0.6",
    "@vitejs/plugin-react": "^6.0.1",
    "eslint": "^9.39.4",
    "eslint-plugin-react-hooks": "^7.0.1",
    "eslint-plugin-react-refresh": "^0.5.2",
    "globals": "^17.4.0",
    "typescript": "~6.0.2",
    "typescript-eslint": "^8.58.0",
    "vite": "^8.0.4"
  }
}

# 前端整合
1. 界面外观
2. 路由结构
3. 前后端数据接口（FASTAPI）
前端发送数据，等待（使用等待界面）后端处理并传回数据
> 岗位画像数据api
岗位画像数据用于在“职业探索”页面展示不同岗位的详细信息、技能要求以及职业发展路径。

### `JobProfile` 数据结构

```typescript
interface JobProfile {
  id: string;                      // 岗位唯一标识 (如: 'frontend', 'java')
  title: string;                   // 岗位名称 (如: "前端开发")
  description: string;             // 岗位职责描述
  education: string;               // 学历要求 (如: "本科及以上")
  major: string;                   // 专业要求 (如: "计算机相关专业优先")
  hard_skills: string[];           // 硬技能/专业技能列表 (如: ["HTML/CSS", "JavaScript", "Vue/React"])
  certifications: string[];        // 证书要求列表
  soft_skills: {                   // 软技能/综合能力评分 (1-100)
    innovation: number;            // 创新能力
    learning: number;              // 学习能力
    stress_tolerance: number;      // 抗压能力
    communication: number;         // 沟通能力
    teamwork: number;              // 团队合作
    internship: number;            // 实习能力
  };

  vertical_paths: string[];        // 垂直晋升路径列表 (如: ["高级前端开发", "前端架构师"])
  horizontal_paths: string[];      // 横向换岗路径列表 (如: ["Java开发工程师", "产品专员"])
  x: number;                       // 节点在画布上的 X 坐标
  y: number;                       // 节点在画布上的 Y 坐标
}
```
> 简历结构化信息api
简历结构化信息用于在“能力分析”页面存储从用户上传的简历（或手动输入的文本）中通过 LLM 解析提取出的结构化数据。

### `ResumeData` 数据结构

```typescript
interface ResumeData {
  name: string;                    // 姓名
  age: string;                     // 年龄
  education: string;               // 学历
  major: string;                   // 就读专业
  skills: string[];                // 掌握的专业技能列表
  certificates: string[];          // 证书列表
  projectExperience: string[];     // 项目经历列表
  internshipExperience: string[];  // 实习经历列表
  practicalExperience: string[];   // 实践活动经历列表
  hobbies: string;                 // 兴趣爱好
  summary: string;                 // 个人总结
  other: string;                   // 其他提取出的杂项信息
  targetRole: string;              // 主攻路径/目标岗位 (根据简历推断)
  completeness: number;            // 简历完整度评分 (1-100)
  scores: {                        // 五维能力评分 (1-100)
    adaptability: number;          // 适应能力
    technicalDepth: number;        // 技术深度
    communication: number;         // 沟通表达能力
    stressTolerance: number;       // 抗压能力
    innovation: number;            // 创新能力
  };

  scoreExplanations?: {            // 各项评分的解释性说明
    completeness: string;          // 简历完整度说明
    technicalDepth: string;        // 技术深度说明
    adaptability: string;          // 适应能力说明
    communication: string;         // 沟通表达能力说明
    stressTolerance: string;       // 抗压能力说明
    innovation: string;            // 创新能力说明
    competitiveness: string;       // 就业竞争力综合评价说明
  };
}
```
> 职位匹配信息api
得传个JobData[]，数组回前端
匹配职位信息用于在“岗位匹配”页面展示系统为用户推荐的岗位列表，以及针对某个岗位的深度匹配分析报告。

### `JobData` 数据结构

```typescript
interface JobData {
  job_id: string;                  // 数据库原始ID，用于详情跳转
  job_name: string;                // 岗位名称
  location: string;                // 工作地点
  salary_range: string;            // 薪资范围展示文本 (如: "25k-40k")
  salary_min: number;              // 最低薪资，用于前端滑动条筛选和排序
  company_name: string;            // 公司名称
  industry: string;                // 所属行业
  company_size: string;            // 公司规模 (如: "10000人以上")
  company_type: string;            // 公司性质 (如: "民营企业")
  update_date: string;             // 更新日期 (如: "2026-04-09")
  source_url: string;              // 来源链接 (点击岗位名称跳转的超链接)
  job_details: string;             // 岗位职责详细描述
  company_details: string;         // 公司简介详细描述
  match_score: number;             // 综合匹配得分 (1-100)
  benchmark_total_score: number;   // 综合基准得分 (1-100)
  dimension_analysis: {            // 七大维度深度解析
    professional_skill: DimensionScore;    // 专业技能
    innovation_ability: DimensionScore;    // 创新能力
    learning_ability: DimensionScore;      // 学习能力
    stress_resistance: DimensionScore;     // 抗压能力
    communication_ability: DimensionScore; // 沟通表达
    internship_experience: DimensionScore; // 核心实习经历
    teamwork_ability: DimensionScore;      // 团队协作
  };
}

// 维度得分详情
interface DimensionScore {
  score: number;                   // 个人在该维度的得分 (1-100)
  benchmark_score: number;         // 该岗位在该维度的基准要求得分 (1-100)
  matched_reason: string;          // 匹配理由 (现状分析)
  missing_reason: string;          // 缺失理由 (提升建议/核心缺失)
}
```

api接口prompt :
现在请帮我在frontend/src/api里面写一个基于ts和axios的user数据接口，这个接口会将ResumeData数据传给后端进行处理，后端会将处理后的JobData数据传回。前端提交 ResumeData，后端立即返回 `taskId`（202 Accepted）， 然后前端每 2-5 秒轮询 `/api/task/{taskId}` 获取处理进度。

ResumeData数据传输的HTTP方法为POST，URL为'POST /api/resume/process'，请求体为frontend/src/types/job.ts中的ResumeData接口，响应体为frontend/src/types/job.ts中的TaskAcceptedResponse和ErrorResponse，其中ErrorResponse为错误响应。

轮询使用GET，响应体为frontend/src/types/job.ts中的TaskStatusResponse

前端轮询策略
间隔：2~5 秒（可动态调整，例如初始 2 秒，随后递增到 5 秒）

停止条件：收到 status === "completed" 或 "failed"，或达到最大轮询次数（如 120 次，对应最长 10 分钟）

超时处理：超过 10 分钟未完成，前端主动停止轮询并提示超时

# 前端界面
整体关系：
一、核心业务逻辑梳理（先定「用户路径」，再定菜单结构）
你的网站核心是 「AI 职业规划全链路」，完整用户旅程是：首页（入口） → 岗位认知（看板/画像/地图） → 能力测评 → 岗位匹配 → 报告生成所有页面都围绕这条主线设计，菜单分层必须贴合用户使用习惯，减少认知成本。
二、菜单栏分层规划（专业可落地版）
🔹 一级导航栏（全局主导航，固定在网站顶部）
核心原则：只放「最高频、最核心、用户一眼能懂」的入口，不堆砌功能，保持简洁。
表格
一级菜单	对应页面	定位说明
首页	首页	全站入口，所有页面均可跳转回首页
岗位洞察	岗位看板、岗位画像、岗位地图	把 3 个「岗位认知类」页面合并为一个一级菜单，避免菜单过长
能力测评	能力测评	核心业务入口，独立一级菜单，突出重点
匹配与报告	岗位匹配、报告生成	把 2 个「结果类」页面合并为一个一级菜单，逻辑闭环
一级导航栏最终结构（对应你之前的主导航）
AI职业规划（Logo） → 首页 → 岗位洞察 → 能力测评 → 匹配与报告 → 立即测评（CTA按钮）
🔹 二级下拉菜单（对应一级菜单的子页面）
1. 「岗位洞察」下拉菜单（3 个岗位认知页）
岗位看板
岗位画像
岗位地图
逻辑：用户先通过「看板」看整体市场，再用「画像」看单个岗位细节，最后用「地图」看地域 / 行业分布，完全符合认知顺序。
2. 「匹配与报告」下拉菜单（2 个结果页）
岗位匹配
报告生成
逻辑：用户完成测评后，先看「岗位匹配结果」，再生成「专属报告」，是业务流程的自然收尾。
3. 「首页」「能力测评」
无二级菜单，点击直接进入对应页面（「能力测评」是核心操作入口，独立一级更突出）
三、页面间跳转关系规划（全链路打通，无死角）
🔹 全局可跳转（所有页面都支持）
首页：所有页面的右上角 / 导航栏，都保留「首页」入口，一键返回
能力测评：所有页面可通过顶部「立即测评」按钮，直接跳转到能力测评页（核心转化入口）
🔹 业务流程内跳转（按用户使用顺序，双向打通）
1. 岗位认知模块（岗位洞察下的 3 个页面）
相互跳转：岗位看板 ↔ 岗位画像 ↔ 岗位地图
看板页：每个岗位卡片点击，跳转到对应「岗位画像」页
画像页：添加「查看同行业岗位地图」按钮，跳转到「岗位地图」页
地图页：点击地域 / 岗位，跳转到对应「岗位画像」页
向上跳转：3 个页面均可跳转到「首页」
向下跳转：3 个页面均可跳转到「能力测评」页（引导用户完成测评）
2. 能力测评模块
向上跳转：可跳转到「首页」、「岗位洞察」下的任意页面（用户可随时回去看岗位信息）
向下跳转：测评完成后，自动 / 手动跳转到「岗位匹配」页
直接跳转：可直接跳转到「报告生成」页（仅当用户有历史测评数据时可用）
3. 匹配与报告模块（岗位匹配、报告生成）
相互跳转：岗位匹配 ↔ 报告生成
匹配页：添加「生成专属报告」按钮，跳转到「报告生成」页
报告页：添加「重新匹配岗位」按钮，跳转到「岗位匹配」页
向上跳转：可跳转到「能力测评」页（重新测评）、「岗位洞察」下的任意页面（查看岗位详情）、「首页」
无向下跳转：报告生成是业务终点，无需再跳转其他功能页
四、跳转关系可视化（流程图，一眼看懂）
plaintext
【首页（全站入口）】
    ↓ ↑（双向）
【岗位洞察】→ 岗位看板 / 岗位画像 / 岗位地图（三者双向互通）
    ↓ ↑（双向）
【能力测评】
    ↓ ↑（双向）
【岗位匹配】
    ↓ ↑（双向）
【报告生成（业务终点）】

【全局跳转】：所有页面 ↔ 首页 / 能力测评
五、额外优化建议（提升用户体验）
1. 面包屑导航（所有页面添加）
示例（岗位画像页）：首页 → 岗位洞察 → 岗位画像
作用：让用户随时知道自己在哪个页面，一键返回上一级 / 首页
2. 「立即测评」按钮（全局固定）
除了顶部导航栏，在所有非测评页的右下角，添加悬浮「立即测评」按钮，引导用户进入核心流程
按钮可复用你之前的 bounce-top 动画，提升点击率
3. 历史数据联动
用户完成测评后，在「岗位洞察」「岗位匹配」「报告生成」页，都显示「我的测评数据」入口，一键查看历史结果
避免用户重复测评，提升体验
4. 移动端适配
一级导航栏在移动端自动折叠为「汉堡菜单」，点击展开二级菜单
保持桌面端的菜单结构，仅调整布局，不改变用户认知


# AI 精准测评，让职业选择更简单 √
AI 驱动的一站式职业测评平台。通过智能能力评估、岗位全景解析与精准匹配，帮你清晰定位竞争力，找到最适合的发展方向，生成专属职业成长报告。
# 全景洞察岗位，看清细节与发展关系 √
  ## 岗位看板 √

  ## 岗位画像 √

  ## 岗位地图 √

# 科学测评实力，找到最适配你的岗位 √
  ## 能力测评、竞争力分析 √
  能力测评

  ## 意愿匹配 √
  岗位匹配

# 定制你的专属报告，解锁清晰职业路径 √
  ## 职业报告生成 √
  分析报告


# 美化界面 
素材库：https://tailwindcss.com/docs/accent-color

# 首页
## 首页顶部导航栏 √
修改frontend里面的前端首页代码，按要求完成下面的两种导航栏丝滑切换。
一、两种导航栏的专业定义与描述
1. 全局主导航栏（Global Navbar / Header）
定位：网站首页的顶部导航组件，默认展示在首页最顶端。结构与功能：
左侧：品牌标识区（「AI 职业规划」Logo）
中间：导航菜单区（包含「首页」「岗位洞察」「能力测评」「专属报告」）
右侧：核心操作按钮区（「立即测评」主按钮，用户点击后跳转进入能力测试(CapabilityAnalysis)界面）
视觉特征：白色背景、极简风格、低视觉干扰，适配全页面展示，不抢占内容焦点。
2. 首页 CTA 引导栏（Homepage CTA Bar / Action Banner）
定位：仅在首页首屏展示的转化引导组件，默认隐藏，仅在特定滚动时机触发显示。结构与功能：
左侧：也包含「首页」「岗位洞察」「能力测评」「专属报告」
右侧：强引导主按钮区（「立即测评」按钮，用户点击后跳转进入能力测试(CapabilityAnalysis)界面）
视觉特征：CTA导航栏采用圆角卡片式设计，卡片为白底黑字，其中强引导主按钮区为高对比配色（如蓝底白字）、强视觉冲击力，用于强化用户行动意愿，仅服务于首页转化。

二、切换触发时机
1. 正向切换（主导航收起 → CTA 栏显示）
触发条件：当页面垂直滚动，首页首屏内容完全离开可视区域，滚动位置到达第二个板块顶部时（即滚动距离 ≥ 首屏高度，可通过 window.scrollY ≥ 首屏offsetTop 精准监听），触发切换动画。补充规则：若滚动速度极快，动画仍完整执行，不跳过过渡；若滚动中途停止，动画停留在当前进度，保证视觉连贯。
2. 反向切换（CTA 栏收起 → 主导航显示）
触发条件：当页面向上滚动，滚动位置回到首屏区域，第二个板块完全离开可视区域时（即滚动距离 < 首屏高度），触发反向切换动画，恢复初始状态。
三、切换过程详细动画描述
1. 正向切换动画（主导航 → CTA 栏）
动画总时长：300ms（0.3 秒），采用 ease-in-out 缓动函数，保证过渡自然丝滑。分阶段执行逻辑：
第 0-150ms（同步启动阶段）：
全局主导航栏：以 translateY(-100%) 为目标，向上平滑滑出屏幕，同时透明度从 100% 渐变至 0%，完成「缓缓向上收起」效果；
首页 CTA 引导栏：以 translateY(0) 为目标，从屏幕外（translateY(-100%) 初始位置）向下平滑滑入，同时透明度从 0% 渐变至 100%，完成「慢慢显示」效果。
第 150-300ms（同步收尾阶段）：
主导航栏：完全滑出屏幕，透明度归 0，设置为 visibility: hidden，避免遮挡页面内容；
CTA 引导栏：完全滑入屏幕，透明度归 100%，固定在页面顶部（position: sticky 吸顶），保持可见状态，直至用户反向滚动。
2. 反向切换动画（CTA 栏 → 主导航）
动画总时长：300ms（0.3 秒），缓动函数与正向一致，保证体验统一。分阶段执行逻辑：
第 0-150ms（同步启动阶段）：
首页 CTA 引导栏：以 translateY(-100%) 为目标，向上平滑滑出屏幕，透明度从 100% 渐变至 0%；
全局主导航栏：以 translateY(0) 为目标，从屏幕外向下平滑滑入，透明度从 0% 渐变至 100%。
第 150-300ms（同步收尾阶段）：
CTA 引导栏：完全滑出屏幕，透明度归 0，设置为 visibility: hidden；
主导航栏：完全滑入屏幕，透明度归 100%，恢复初始固定顶部状态，保持全页面可见。
四、补充交互规则（避免体验漏洞）
动画互斥：正向 / 反向动画执行期间，若用户反向滚动，立即终止当前动画，执行反向动画，避免动画冲突；
状态锁定：动画执行完成后，锁定当前导航栏状态，直至下一次滚动触发；
移动端适配：动画逻辑与桌面端完全一致，仅调整导航栏高度适配移动端屏幕；
性能优化：使用 will-change: transform, opacity 提前声明动画属性，保证动画 60fps 流畅运行，无卡顿。
五、前端可直接复用的专业术语（开发沟通用）
主导航栏：Global Navbar / Site Header
CTA 引导栏：Homepage CTA Bar / Sticky Action Banner
向上收起：slideOutUp / translateY(-100%)
向下显示：slideInDown / translateY(0)
滚动监听：scroll threshold / intersection observer（推荐用 IntersectionObserver 替代 scroll 事件，性能更优）
缓动函数：ease-in-out
动画时长：transition-duration: 300ms

## 首页大标题文字特效 √
.tracking-in-expand {
	-webkit-animation: tracking-in-expand 0.9s cubic-bezier(0.215, 0.610, 0.355, 1.000) both;
	        animation: tracking-in-expand 0.9s cubic-bezier(0.215, 0.610, 0.355, 1.000) both;
}
/* ----------------------------------------------
 * Generated by Animista on 2026-4-15 15:16:27
 * Licensed under FreeBSD License.
 * See http://animista.net/license for more info. 
 * w: http://animista.net, t: @cssanimista
 * ---------------------------------------------- */

/**
 * ----------------------------------------
 * animation tracking-in-expand
 * ----------------------------------------
 */
@-webkit-keyframes tracking-in-expand {
  0% {
    letter-spacing: -0.5em;
    opacity: 0;
  }
  40% {
    opacity: 0.6;
  }
  100% {
    opacity: 1;
  }
}
@keyframes tracking-in-expand {
  0% {
    letter-spacing: -0.5em;
    opacity: 0;
  }
  40% {
    opacity: 0.6;
  }
  100% {
    opacity: 1;
  }
}
## 为首页的测评流程找（生成）一张合适的图片

## 找一个好看的背景图片

# 每个子界面都弄一个返回主界面按钮

# 岗位看板
将JobList、JobDetail、FilterBar结合
分为三块，最上方一个板块为搜索框，搜索框下方分为左右两个板块，左边是各个岗位，点击左边的某个岗位后右边会显示这个岗位的详细信息，默认显示第一个岗位的信息。

# 岗位画像

# 岗位地图
直接显示地图

# 