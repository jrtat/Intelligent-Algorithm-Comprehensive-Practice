from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import asyncio
import json
import os
from datetime import datetime
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
    hobbies: str
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

    # 保存简历数据到 JSON 文件
    saved_path = save_resume_to_json(resume_data)

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

# 保存简历数据到 JSON 文件
def save_resume_to_json(resume_data: ResumeData, save_dir: str = None) -> str:
    """
    将简历数据结构化数据提取并保存为 JSON 文件到 jk 文件夹

    Args:
        resume_data: 简历数据对象
        save_dir: 保存目录路径，默认为 jk 文件夹

    Returns:
        保存的文件路径
    """
    if save_dir is None:
        # 获取项目根目录的 jk 文件夹
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        save_dir = os.path.join(project_root, "jk")

    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)

    # 生成文件名：resume_姓名_时间戳.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 清理姓名中的非法字符
    safe_name = "".join(c for c in resume_data.name if c.isalnum() or c in ('_', '-', ' ')).strip()
    if not safe_name:
        safe_name = "unknown"
    filename = f"resume_{safe_name}_{timestamp}.json"
    filepath = os.path.join(save_dir, filename)

    # 转换为字典并保存为 JSON
    resume_dict = {
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

    # 如果有评分说明，也保存
    if resume_data.scoreExplanations:
        resume_dict["scoreExplanations"] = {
            "completeness": resume_data.scoreExplanations.completeness,
            "technicalDepth": resume_data.scoreExplanations.technicalDepth,
            "adaptability": resume_data.scoreExplanations.adaptability,
            "communication": resume_data.scoreExplanations.communication,
            "stressTolerance": resume_data.scoreExplanations.stressTolerance,
            "innovation": resume_data.scoreExplanations.innovation,
            "competitiveness": resume_data.scoreExplanations.competitiveness,
        }

    # 保存到文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(resume_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ 简历数据已保存至: {filepath}")
    return filepath