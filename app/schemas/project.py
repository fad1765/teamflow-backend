from datetime import datetime
from pydantic import BaseModel, EmailStr

## 建立專案
class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    type: str

## 專案回傳格式
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    type: str
    owner_id: int
    created_at: datetime
    member_count: int = 0

    model_config = {
        "from_attributes": True
    }

## 專案成員回傳格式
class ProjectMemberResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    color: str
    role: str

## 發送邀請
class InvitationCreate(BaseModel):
    user_id: int

## 邀請回傳格式
class InvitationResponse(BaseModel):
    id: int
    project_id: int
    project_name: str
    email: EmailStr
    invited_by: int
    inviter_name: str | None = None
    inviter_email: EmailStr | None = None
    status: str
    created_at: datetime
    responded_at: datetime | None

    model_config = {
        "from_attributes": True
    }