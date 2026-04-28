from datetime import datetime
from pydantic import BaseModel

## 建立留言
class CommentCreate(BaseModel):
    content: str

## 更新留言
class CommentUpdate(BaseModel):
    content: str

## 留言回傳格式
class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    user_name: str
    content: str
    created_at: datetime
    updated_at: datetime | None
    likes_count: int
    is_liked: bool

    model_config = {
        "from_attributes": True
    }