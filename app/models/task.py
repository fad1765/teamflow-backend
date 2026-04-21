from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.database import Base

"""
任務表（Task）

功能：
- 儲存任務資訊
- 支援 Kanban（Todo / Doing / Done）
- 支援排序、指派、時間管理
"""
class Task(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    # 任務標題
    title = Column(String(255), nullable=False)

    # 任務描述
    description = Column(Text, nullable=True)

    # 任務狀態（Kanban）
    status = Column(String(20), nullable=False, default="todo")

    # 任務分類（例如 Frontend / Backend）
    category = Column(String(50), nullable=False, default="Frontend")

    # 排序用（Kanban 順序）
    position = Column(Integer, nullable=False, default=0)

    # 指派人
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 建立者
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 所屬專案（關鍵：資料隔離）
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
    )

    # 建立時間
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 更新時間
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 截止時間
    deadline = Column(DateTime(timezone=True), nullable=True)

    # 預估天數
    estimated_days = Column(Integer, nullable=True)

    # 完成時間（移到 done 自動填）
    completed_at = Column(DateTime(timezone=True), nullable=True)