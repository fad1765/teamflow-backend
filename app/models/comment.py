from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

"""
任務留言表（Task Comment）

功能：
- 記錄任務下的留言內容
- 支援編輯與時間追蹤
"""
class Comment(Base):

    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)

    # 所屬任務 ID
    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False
    )

    # 留言使用者 ID
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # 留言內容
    content = Column(Text, nullable=False)

    # 建立時間
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # 更新時間（編輯留言時更新）
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now()
    )