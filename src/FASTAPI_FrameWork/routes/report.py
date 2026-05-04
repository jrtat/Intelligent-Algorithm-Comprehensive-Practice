from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import asyncio
import json
import os
from typing import List, Optional

router = APIRouter()

class ReportGenInput(BaseModel):
    resume: dict
    job: List

report_tasks = {}


def get_jobs_dict():
    """获取岗位数据字典"""
    jobs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'processor', 'data', 'jobs.json')
    if os.path.exists(jobs_path):
        with open(jobs_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@router.post("/generate", status_code=202)
async def generate_report(input: ReportGenInput):
    print(f"✅ 收到报告生成请求 | 候选人：{input.resume.get('name', 'Unknown')}")

    task_id = str(uuid4())
    report_tasks[task_id] = {"status": "pending", "progress": 0}

    async def generate_report_task():
        try:
            await asyncio.sleep(0.5)
            report_tasks[task_id]["status"] = "processing"
            report_tasks[task_id]["progress"] = 10

            # 获取岗位名称
            job_name = input.job[0] if input.job else "未知岗位"

            # 构建目标岗位信息
            jobs_dict = get_jobs_dict()
            job_info = None
            for job_id, job in jobs_dict.items():
                if job.get('岗位名称') == job_name:
                    job_info = job
                    break

            # 构造 resume_info
            resume_info = {
                "name": input.resume.get('name', '未知'),
                "education": input.resume.get('education', ''),
                "experience": input.resume.get('experience', []),
                "skills": input.resume.get('skills', []),
                "certifications": input.resume.get('certifications', []),
                **input.resume
            }

            # 导入并使用 Reporter
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from src.processor.tools.Reporter import Reporter

            report_tasks[task_id]["progress"] = 30

            # 调用 Reporter 生成报告
            reporter = Reporter(resume_info)

            report_tasks[task_id]["progress"] = 50

            # 使用 job_report_ex 获取更完整的报告
            if job_info:
                raw_result = reporter.job_report_ex(job_name, {
                    "job_description": job_info.get('岗位详情', ''),
                    "requirements": job_info
                })
            else:
                raw_result = reporter.job_report_ex(job_name, None)

            report_tasks[task_id]["progress"] = 80

            if raw_result:
                # raw_result 可能是 JSON 字符串或已经是字典
                if isinstance(raw_result, str):
                    try:
                        result = json.loads(raw_result)
                    except json.JSONDecodeError:
                        result = {"raw_response": raw_result}
                else:
                    result = raw_result

                report_tasks[task_id]["status"] = "completed"
                report_tasks[task_id]["progress"] = 100
                report_tasks[task_id]["result"] = result
                print(f"✅ 报告生成成功 | 候选人：{input.resume.get('name', 'Unknown')}")
            else:
                report_tasks[task_id]["status"] = "failed"
                report_tasks[task_id]["error"] = "报告生成失败"
                print(f"❌ 报告生成失败 | 候选人：{input.resume.get('name', 'Unknown')}")

        except Exception as e:
            print(f"❌ 报告生成异常: {e}")
            report_tasks[task_id]["status"] = "failed"
            report_tasks[task_id]["error"] = str(e)

    asyncio.create_task(generate_report_task())

    return {
        "taskId": task_id,
        "status": "pending",
        "estimatedTime": 30
    }


def get_report_tasks():
    return report_tasks


@router.get("/{task_id}")
async def get_report(task_id: str):
    if task_id not in report_tasks:
        raise HTTPException(status_code=404, detail="Report not found")

    task = report_tasks[task_id]
    if task["status"] == "pending" or task["status"] == "processing":
        raise HTTPException(status_code=400, detail="Report not ready")

    if task["status"] == "failed":
        raise HTTPException(status_code=500, detail=task.get("error", "Report generation failed"))

    return task.get("result", {})