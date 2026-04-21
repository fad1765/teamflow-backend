from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base

"""
專案邀請表（Project Invitation）

功能：
- 記錄邀請使用者加入專案
- 透過 email 邀請
- 控制邀請狀態（pending / accepted / declined）
"""
class ProjectInvitation(Base):

    __tablename__ = "project_invitations"

    id = Column(Integer, primary_key=True, index=True)

    # 被邀請的專案
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    # 被邀請者 Email
    email = Column(String(255), nullable=False)

    # 邀請人（發送邀請的 user）
    invited_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # 邀請狀態
    # pending：待回應
    # accepted：已接受
    # declined：已拒絕
    status = Column(String(20), nullable=False, default="pending")

    # 發送時間
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 回應時間（接受或拒絕）
    responded_at = Column(DateTime(timezone=True), nullable=True)

    # 限制：同一專案不能重複邀請同一 email
    __table_args__ = (
        UniqueConstraint("project_id", "email", name="unique_project_invitation"),
    )