from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserListResponse
from app.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/users", tags=["users"])

## 取得所有使用者清單
@router.get("", response_model=list[UserListResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # 依照 ID 排序（確保順序一致）
    users = db.query(User).order_by(User.id.asc()).all()

    return users