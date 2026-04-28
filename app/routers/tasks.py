from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskReorderRequest,
    TaskResponse,
    TaskUpdate,
)
from app.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

ALLOWED_STATUSES = {"todo", "doing", "done"}
ALLOWED_CATEGORIES = {"SA", "Frontend", "Backend", "Testing", "UIUX"}

#Task → Response
def build_task_response(task: Task, assignee: User | None):

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "category": task.category,
        "position": task.position,
        "assignee_id": task.assignee_id,
        "created_by": task.created_by,
        "created_at": task.created_at,
        "deadline": task.deadline,
        "estimated_days": task.estimated_days,
        "completed_at": task.completed_at,
        "assignee_name": assignee.name if assignee else None,
        "assignee_color": assignee.color if assignee else None,
    }

#建立任務
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if task_data.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status",
        )

    if task_data.category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category",
        )

    assignee = None
    if task_data.assignee_id is not None:
        assignee = db.query(User).filter(User.id == task_data.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found",
            )

    max_position = (
        db.query(func.max(Task.position))
        .filter(Task.status == task_data.status)
        .scalar()
    )
    next_position = (max_position or 0) + 1

    completed_at = None
    if task_data.status == "done":
        completed_at = datetime.now(timezone.utc)

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        category=task_data.category,
        position=next_position,
        assignee_id=task_data.assignee_id,
        created_by=current_user.id,
        deadline=task_data.deadline,
        estimated_days=task_data.estimated_days,
        completed_at=completed_at,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return build_task_response(new_task, assignee)

@router.get("", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = (
        db.query(Task)
        .order_by(Task.status.asc(), Task.position.asc(), Task.created_at.asc())
        .all()
    )

    result = []
    for task in tasks:
        assignee = None
        if task.assignee_id:
            assignee = db.query(User).filter(User.id == task.assignee_id).first()
        result.append(build_task_response(task, assignee))

    return result

#拖拉排序 API
@router.put("/reorder", status_code=status.HTTP_200_OK)
def reorder_tasks(
    payload: TaskReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task_ids = [item.id for item in payload.tasks]

    db_tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
    task_map = {task.id: task for task in db_tasks}

    if len(task_map) != len(task_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more tasks not found",
        )

    for item in payload.tasks:
        if item.status not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status in reorder payload",
            )

        task = task_map[item.id]
        task.status = item.status
        task.position = item.position

        if task.status == "done" and task.completed_at is None:
            task.completed_at = datetime.now(timezone.utc)

        if task.status != "done":
            task.completed_at = None

    db.commit()

    return {"message": "Task order updated successfully"}

#更新任務
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task_data.status is not None and task_data.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status",
        )

    if task_data.category is not None and task_data.category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category",
        )

    assignee = None
    if task_data.assignee_id is not None:
        assignee = db.query(User).filter(User.id == task_data.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found",
            )

    previous_status = task.status
    update_data = task_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    if task.status == "done" and previous_status != "done" and task.completed_at is None:
        task.completed_at = datetime.now(timezone.utc)

    if task.status != "done":
        task.completed_at = None

    db.commit()
    db.refresh(task)

    if task.assignee_id and assignee is None:
        assignee = db.query(User).filter(User.id == task.assignee_id).first()

    return build_task_response(task, assignee)

#刪除任務
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()