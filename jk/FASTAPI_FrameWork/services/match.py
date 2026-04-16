# 岗位匹配核心逻辑 + 模拟数据
def create_job_data(id, job_name, company_name, location, salary_min, salary_max, match_score, benchmark_score):
    return {
        "job_id": f"mock_job_{id}",
        "job_name": job_name,
        "location": location,
        "salary_range": f"{salary_min//1000}k-{salary_max//1000}k",
        "salary_min": salary_min,
        "company_name": company_name,
        "industry": "互联网",
        "company_size": "500-1000人",
        "company_type": "民营企业",
        "update_date": "2026-04-14",
        "source_url": f"https://example.com/job/{id}",
        "job_details": "岗位职责：负责公司前端业务开发...",
        "company_details": "公司简介：一家专注于AI技术的互联网公司...",
        "match_score": match_score,
        "benchmark_total_score": benchmark_score,
        "dimension_analysis": {
            "professional_skill": {"score": 82, "benchmark_score": 85, "matched_reason": "熟练掌握 React/Vue 等主流框架", "missing_reason": "缺乏大型前端架构设计经验"},
            "innovation_ability": {"score": 78, "benchmark_score": 75, "matched_reason": "有多个创新项目经验", "missing_reason": "无"},
            "learning_ability": {"score": 88, "benchmark_score": 80, "matched_reason": "学习能力强，快速掌握新技术", "missing_reason": "无"},
            "stress_resistance": {"score": 75, "benchmark_score": 78, "matched_reason": "能适应一定的工作压力", "missing_reason": "高压环境经验可以更多"},
            "communication_ability": {"score": 80, "benchmark_score": 78, "matched_reason": "沟通表达清晰流畅", "missing_reason": "跨团队协作经验可以加强"},
            "internship_experience": {"score": 70, "benchmark_score": 75, "matched_reason": "有相关实习经历", "missing_reason": "实习时间较短"},
            "teamwork_ability": {"score": 82, "benchmark_score": 80, "matched_reason": "团队协作能力良好", "missing_reason": "无"}
        }
    }

# 岗位数据
mock_job_list = [
    create_job_data("001", "原神启动", "HOYOMIX", "上海·浦东", 20000, 35000, 85.5, 80.0),
    create_job_data("002", "崩坏星穹铁道工程师", "HOYOMIX", "北京·海淀", 30000, 50000, 82.3, 85.0),
    create_job_data("003", "绝区零前端工程师", "阿里巴巴", "杭州", 25000, 45000, 78.9, 82.0),
    create_job_data("004", "fufu架构师", "腾讯", "深圳·南山", 40000, 70000, 75.2, 88.0),
    create_job_data("005", "嘿嘿开发工程师", "美团", "北京·朝阳", 28000, 48000, 80.6, 78.0),
]