from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base

"""
使用者表（User）

功能：
- 儲存帳號資訊
- 支援登入驗證與專案關聯
"""
class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # 使用者名稱
    name = Column(String(100), nullable=False)

    # Email（唯一）
    email = Column(String(255), unique=True, nullable=False)

    # 密碼（加密後）
    password_hash = Column(String(255), nullable=False)

    # UI 顏色（用於頭像 / 任務標記）
    color = Column(String(20), nullable=False, default="#60a5fa")

    # 建立時間
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 更新時間
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )