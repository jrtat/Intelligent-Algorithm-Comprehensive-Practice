from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import asyncio

from typing import List, Optional
from src.processor.tools.Matcher import Matcher  # type: ignore

router = APIRouter()

# 数据模型
class Scores(BaseModel):
    adaptability: float
    technicalDepth: float
    communication: float
    stressTolerance: float
    innovation: float

class ScoreExplanations(BaseModel):
    completeness: str
    technicalDepth: str
    adaptability: str
    communication: str
    stressTolerance: str
    innovation: str
    competitiveness: str

class ResumeData(BaseModel):
    name: str
    age: str
    education: str
    major: str
    skills: List[str]
    certificates: List[str]
    projectExperience: List[str]
    internshipExperience: List[str]
    practicalExperience: List[str]
    hobbies: List[str]
    summary: str
    other: str
    targetRole: str
    completeness: float
    scores: Scores
    scoreExplanations: Optional[ScoreExplanations] = None

# 全局任务存储
tasks = {}

# 提交简历处理
@router.post("/process", status_code=202)
async def process_resume(resume_data: ResumeData):
    print(f"✅ 收到简历：{resume_data.name} | 目标岗位：{resume_data.targetRole}")

    task_id = str(uuid4())
    tasks[task_id] = {"status": "pending", "progress": 0}

    async def run_matching():
        """执行简历匹配任务"""
        try:
            await asyncio.sleep(1)
            tasks[task_id]["status"] = "processing"
            tasks[task_id]["progress"] = 10

            # 准备简历信息（转换为 Matcher 需要的格式）
            resume_info = {
                "name": resume_data.name,
                "age": resume_data.age,
                "education": resume_data.education,
                "major": resume_data.major,
                "skills": resume_data.skills,
                "certificates": resume_data.certificates,
                "projectExperience": resume_data.projectExperience,
                "internshipExperience": resume_data.internshipExperience,
                "practicalExperience": resume_data.practicalExperience,
                "hobbies": resume_data.hobbies,
                "summary": resume_data.summary,
                "other": resume_data.other,
                "targetRole": resume_data.targetRole,
                "completeness": resume_data.completeness,
                "scores": {
                    "adaptability": resume_data.scores.adaptability,
                    "technicalDepth": resume_data.scores.technicalDepth,
                    "communication": resume_data.scores.communication,
                    "stressTolerance": resume_data.scores.stressTolerance,
                    "innovation": resume_data.scores.innovation,
                },
            }

            tasks[task_id]["progress"] = 30

            # 创建 Matcher 实例并获取匹配结果
            matcher = Matcher(resume_info)
            matching_results = matcher.get_result()

            tasks[task_id]["progress"] = 80

            # 转换结果格式为元组列表 [job_name, match_score, dimension_analysis]
            result = []
            for job_name, match_score, dimension_analysis in matching_results:
                result.append([job_name, match_score, dimension_analysis])

            tasks[task_id]["status"] = "completed"
            tasks[task_id]["progress"] = 100
            tasks[task_id]["result"] = result

            print(f"✅ 匹配完成，共找到 {len(result)} 个匹配岗位")

        except Exception as e:
            print(f"❌ 匹配失败：{str(e)}")
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = str(e)

    asyncio.create_task(run_matching())

    return {
        "taskId": task_id,
        "status": "pending",
        "estimatedTime": 30
    }

# 把 tasks 暴露给 task.py 使用
def get_tasks():
    return tasks