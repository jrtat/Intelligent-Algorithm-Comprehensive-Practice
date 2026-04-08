# 岗位数据看板

## 项目简介
- Vite + React + TypeScript 前端项目
- 使用 React Router 进行页面路由管理
- 用途：展示清洗挖掘后的岗位数据，支持搜索、筛选、统计分析及地理位置分布展示

## 技术栈
- **框架**: React 19 + TypeScript
- **路由**: React Router 7
- **构建工具**: Vite 8
- **包管理器**: npm / bun
- **样式**: CSS Modules 风格 (组件化 CSS)

## 数据结构 (src/data/)
| 文件 | 内容 |
|------|------|
| `jobs.json` | 岗位详情（核心数据），按岗位ID索引，包含岗位名称、公司、地址、薪资、学历、技能、能力等级等 |
| `cities.json` | 城市信息（地址、岗位列表、坐标、城市等级） |
| `industries.json` | 行业公司分类（行业 $\to$ 公司列表） |
| `companies.json` | 公司信息列表 |
| `cleaned_data.json` | 原始完整数据（暂存） |

## 功能模块
- **岗位列表页 (`/`)**: 关键词搜索、多维度筛选（城市、学历、行业等）、岗位卡片展示。
- **岗位详情页 (`/:jobId`)**: 查看岗位的详细描述、技能要求、能力等级条等。
- **统计摘要页 (`/summary`)**: 岗位数据的统计汇总分析。
- **地理分布页 (`/map`)**: 基于地图的岗位空间分布展示。

## 文件结构
```
src/
├── components/           # 业务组件
│   ├── FilterBar/        # 筛选栏组件 (FilterBar, filter-bar.css)
│   ├── JobDetail/        # 岗位详情组件 (JobDetail, JobSummary, AbilityBar, job-template.css)
│   ├── JobList/          # 岗位列表组件 (JobList, JobCard, job-list.css)
│   ├── JobMap/           # 地图分布组件 (JobMap, job-map.css)
│   └── JobSummary/       # 统计摘要组件 (JobSummary, job-summary.css)
├── data/                 # JSON 静态数据文件
├── hooks/                # 自定义 Hook (如 useJobFilter)
├── types/                # TypeScript 类型定义 (job.ts)
├── assets/               # 静态资源 (图片、SVG)
├── App.tsx               # 路由配置与主入口
├── main.tsx              # React 渲染入口
├── index.css             # 全局样式
└── App.css               # 基础样式
```

## 下一步规划
- 性能优化：针对大规模数据引入虚拟滚动
- 数据可视化：引入 ECharts 或其他库增强统计图表
- 交互增强：地图交互功能优化
- 响应式适配：完善移动端浏览体验
