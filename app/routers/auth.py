from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.utils.auth import create_access_token, hash_password, verify_password
from app.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/auth", tags=["auth"])

USER_COLORS = [
    "#60a5fa",
    "#f87171",
    "#34d399",
    "#fbbf24",
    "#a78bfa",
    "#fb7185",
    "#22c55e",
    "#38bdf8",
    "#f97316",
    "#14b8a6",
]

def pick_user_color(db: Session) -> str:
    color_counts = (
        db.query(User.color, func.count(User.id))
        .group_by(User.color)
        .all()
    )

    usage_map = {color: count for color, count in color_counts}

    # 找使用最少的顏色
    selected_color = min(
        USER_COLORS,
        key=lambda c: usage_map.get(c, 0)
    )

    return selected_color

## 使用者註冊
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):

    # 檢查 email 是否重複
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 建立新使用者（密碼加密）
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        color=pick_user_color(db),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


## 使用者登入
@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):

    # 查詢使用者
    user = db.query(User).filter(User.email == user_data.email).first()

    # 驗證密碼
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # 建立 JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }

## 取得目前登入使用者資訊
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):

    return current_user