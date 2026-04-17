from pydantic import BaseModel, EmailStr

## 使用者列表回傳格式（前端顯示用）
class UserListResponse(BaseModel):

    id: int
    name: str
    email: EmailStr
    color: str  # 使用者顏色

    model_config = {
        "from_attributes": True  
    }