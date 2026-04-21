from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base

"""
專案成員表（Project Member）

功能：
- 記錄使用者與專案的關聯
- 控制專案內角色（owner / member / pm）
"""
class ProjectMember(Base):

    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)

    # 所屬專案
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    # 成員 user
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # 角色
    role = Column(
        String(20),
        nullable=False,
        default="member"  # owner / member / pm
    )

    # 加入時間
    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # 限制：同一使用者不能重複加入同一專案
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="unique_project_member"),
    )