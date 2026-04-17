from pydantic import BaseModel, EmailStr

## 註冊請求格式
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

## 登入請求格式
class UserLogin(BaseModel):
    email: EmailStr
    password: str

## 使用者回傳格式
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {
        "from_attributes": True  # 支援 SQLAlchemy model → Pydantic
    }

## 登入成功回傳格式
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse