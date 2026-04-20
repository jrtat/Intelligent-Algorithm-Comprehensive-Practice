from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import asyncio
from typing import List, Optional
from services.match import mock_job_list

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
    hobbies: List[str]  # 修正：与前端保持一致，使用数组
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

    async def simulate_task():
        await asyncio.sleep(1)
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 50

        await asyncio.sleep(2)
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["result"] = mock_job_list

    asyncio.create_task(simulate_task())

    return {
        "taskId": task_id,
        "status": "pending",
        "estimatedTime": 5
    }

# 把 tasks 暴露给 task.py 使用
def get_tasks():
    return tasks