from fastapi import APIRouter, HTTPException
from routes.resume import get_tasks
from routes.report import get_report_tasks

router = APIRouter()

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    tasks = get_tasks()
    report_tasks = get_report_tasks()

    if task_id in tasks:
        task = tasks[task_id].copy()
        task["taskId"] = task_id
        return task
    elif task_id in report_tasks:
        task = report_tasks[task_id].copy()
        task["taskId"] = task_id
        return task
    else:
        raise HTTPException(status_code=404, detail="Task not found")