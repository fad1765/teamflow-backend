from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.database import Base

"""
專案主表（Project）

功能：
- 管理專案基本資訊
- 支援個人專案與團隊專案
"""
class Project(Base):

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    # 專案名稱
    name = Column(String(120), nullable=False)

    # 專案描述（可選）
    description = Column(Text, nullable=True)

    # 專案類型
    # personal：個人專案
    # team：團隊專案
    type = Column(String(20), nullable=False)

    # 建立者（owner）
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # 建立時間
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 更新時間（自動更新）
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )