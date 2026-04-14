// 简单的 Mock API 服务器，用于测试前端 API 调用
const http = require('http');
const crypto = require('crypto');

const PORT = 8000;

// 单个岗位数据模板
const createJobData = (id, jobName, companyName, location, salaryMin, salaryMax, matchScore, benchmarkScore) => ({
  job_id: `mock_job_${id}`,
  job_name: jobName,
  location: location,
  salary_range: `${salaryMin / 1000}k-${salaryMax / 1000}k`,
  salary_min: salaryMin,
  company_name: companyName,
  industry: "互联网",
  company_size: "500-1000人",
  company_type: "民营企业",
  update_date: "2026-04-14",
  source_url: `https://example.com/job/${id}`,
  job_details: "岗位职责：负责公司前端业务开发...",
  company_details: "公司简介：一家专注于AI技术的互联网公司...",
  match_score: matchScore,
  benchmark_total_score: benchmarkScore,
  dimension_analysis: {
    professional_skill: { score: 82, benchmark_score: 85, matched_reason: "熟练掌握 React/Vue 等主流框架", missing_reason: "缺乏大型前端架构设计经验" },
    innovation_ability: { score: 78, benchmark_score: 75, matched_reason: "有多个创新项目经验", missing_reason: "无" },
    learning_ability: { score: 88, benchmark_score: 80, matched_reason: "学习能力强，快速掌握新技术", missing_reason: "无" },
    stress_resistance: { score: 75, benchmark_score: 78, matched_reason: "能适应一定的工作压力", missing_reason: "高压环境经验可以更多" },
    communication_ability: { score: 80, benchmark_score: 78, matched_reason: "沟通表达清晰流畅", missing_reason: "跨团队协作经验可以加强" },
    internship_experience: { score: 70, benchmark_score: 75, matched_reason: "有相关实习经历", missing_reason: "实习时间较短" },
    teamwork_ability: { score: 82, benchmark_score: 80, matched_reason: "团队协作能力良好", missing_reason: "无" }
  }
});

// 返回多个岗位数据
const mockJobDataList = [
  createJobData("001", "前端开发工程师", "测试科技有限公司", "北京·朝阳", 20000, 35000, 85.5, 80.0),
  createJobData("002", "React开发工程师", "字节跳动", "北京·海淀", 30000, 50000, 82.3, 85.0),
  createJobData("003", "Vue前端工程师", "阿里巴巴", "杭州", 25000, 45000, 78.9, 82.0),
  createJobData("004", "前端架构师", "腾讯", "深圳·南山", 40000, 70000, 75.2, 88.0),
  createJobData("005", "全栈开发工程师", "美团", "北京·朝阳", 28000, 48000, 80.6, 78.0),
];

// 存储任务状态
const tasks = new Map();

const server = http.createServer((req, res) => {
  // 设置 CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // 解析 URL
  const url = new URL(req.url, `http://localhost:${PORT}`);

  console.log(`${new Date().toISOString()} - ${req.method} ${url.pathname}`);

  // POST /api/resume/process - 提交简历
  if (req.method === 'POST' && url.pathname === '/api/resume/process') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      console.log('收到简历数据:', body.substring(0, 200) + '...');

      // 生成任务 ID
      const taskId = crypto.randomUUID();
      tasks.set(taskId, { status: 'pending', progress: 0 });

      // 模拟异步处理 - 2秒后完成
      setTimeout(() => {
        tasks.set(taskId, { status: 'processing', progress: 50 });
      }, 1000);

      setTimeout(() => {
        tasks.set(taskId, { status: 'completed', progress: 100, result: mockJobDataList });
      }, 3000);

      res.writeHead(202, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        taskId,
        status: 'pending',
        estimatedTime: 5
      }));
    });
    return;
  }

  // GET /api/task/{taskId} - 获取任务状态
  const taskMatch = url.pathname.match(/^\/api\/task\/(.+)$/);
  if (req.method === 'GET' && taskMatch) {
    const taskId = taskMatch[1];
    const task = tasks.get(taskId);

    if (!task) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Task not found' }));
      return;
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      taskId,
      status: task.status,
      progress: task.progress,
      result: task.result || undefined
    }));
    return;
  }

  // 其他路由返回 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

server.listen(PORT, () => {
  console.log(`
========================================
  Mock API Server 已启动
  - 端口: ${PORT}
  - 提交简历: POST http://localhost:${PORT}/api/resume/process
  - 查询任务: GET http://localhost:${PORT}/api/task/{taskId}
========================================
  `);
});
