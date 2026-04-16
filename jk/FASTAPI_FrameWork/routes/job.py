from fastapi import APIRouter
from services.match import mock_job_list

router = APIRouter()

@router.get("/list")
async def get_job_list():
    return {"jobs": mock_job_list}