from fastapi import APIRouter, HTTPException
from routes.resume import get_tasks

router = APIRouter()
tasks = get_tasks()

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]