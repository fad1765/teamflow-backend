from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

# 匯入 models，讓 create_all 知道有哪些資料表
from app.models.user import User
from app.models.task import Task
from app.models.comment import Comment
from app.models.comment_like import CommentLike
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.project_invitation import ProjectInvitation

# 匯入 routers
from app.routers.auth import router as auth_router
from app.routers.tasks import router as tasks_router
from app.routers.users import router as users_router
from app.routers.comments import router as comments_router
from app.routers.projects import router as projects_router
from app.routers.invitations import router as invitations_router

# 建立資料表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS 設定（讓前端可以呼叫 API）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 各模組 router
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(users_router)
app.include_router(comments_router)
app.include_router(projects_router)
app.include_router(invitations_router)

@app.get("/")
def read_root():
    return {"message": "TeamFlow backend is running"}