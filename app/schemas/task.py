from datetime import datetime
from typing import Optional

from pydantic import BaseModel

## 建立任務用的請求格式
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    category: str = "Frontend"
    assignee_id: Optional[int] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_days: Optional[int] = None

## 更新任務
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    assignee_id: Optional[int] = None
    position: Optional[int] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_days: Optional[int] = None
    completed_at: Optional[datetime] = None

## 任務回傳格式
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    category: str
    position: int
    assignee_id: Optional[int] = None
    created_by: int
    created_at: datetime
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_days: Optional[int] = None
    completed_at: Optional[datetime] = None
    assignee_name: Optional[str] = None
    assignee_color: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

## 單一任務排序資料
class TaskReorderItem(BaseModel):
    id: int
    status: str
    position: int

## 批次排序請求(拖拉用)
class TaskReorderRequest(BaseModel):
    tasks: list[TaskReorderItem]