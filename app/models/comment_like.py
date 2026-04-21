from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

"""
留言按讚表（Comment Like）

功能：
- 記錄哪個使用者對哪一則留言按讚
- 一個使用者對同一留言只能按讚一次（透過 UniqueConstraint 控制）
"""
class CommentLike(Base):

    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)

    comment_id = Column(
        Integer,
        ForeignKey("task_comments.id", ondelete="CASCADE"),
        nullable=False
    )

    # 按讚的使用者 ID
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # 建立時間（自動填入）
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # 限制：同一使用者不能對同一留言重複按讚
    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="unique_comment_like"),
    )