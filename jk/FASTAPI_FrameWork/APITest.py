from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import job, resume, task

app = FastAPI(title="简历匹配 API")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载所有子路由
app.include_router(resume.router, prefix="/api/resume")
app.include_router(task.router, prefix="/api/task")
app.include_router(job.router, prefix="/api/job")

# 启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)