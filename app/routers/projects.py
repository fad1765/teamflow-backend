from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.project_invitation import ProjectInvitation
from app.models.task import Task
from app.models.user import User
from app.schemas.project import (
    InvitationCreate,
    InvitationResponse,
    ProjectCreate,
    ProjectMemberResponse,
    ProjectResponse,
)
from app.schemas.task import TaskCreate, TaskResponse
from app.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/projects", tags=["projects"])

ALLOWED_PROJECT_TYPES = {"personal", "team"}
ALLOWED_STATUSES = {"todo", "doing", "done"}
ALLOWED_CATEGORIES = {"SA", "Frontend", "Backend", "Testing", "UIUX"}

"""
驗證使用者是否為專案成員

用途：
- 保護專案資料（資料隔離）
"""
def ensure_project_member(project_id: int, user_id: int, db: Session) -> Project:

    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    membership = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        )

    return project


"""
驗證是否為 Owner / PM

用於：
- 邀請成員
- 管理專案
"""
def ensure_project_owner_or_pm(project_id: int, user_id: int, db: Session) -> Project:

    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    membership = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )

    if not membership or membership.role not in {"owner", "pm"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage this project",
        )

    return project


#將 Project ORM 轉為 response
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

def build_project_response(project: Project, db: Session):
    member_count = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project.id)
        .count()
    )

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "type": project.type,
        "owner_id": project.owner_id,
        "created_at": project.created_at,
        "member_count": member_count,
    }


"""
建立專案

流程：
- 驗證 type
- 建立 Project
- 自動加入 owner 成員
"""
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.type not in ALLOWED_PROJECT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project type",
        )

    name = payload.name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project name cannot be empty",
        )

    new_project = Project(
    name=name,
    description=payload.description.strip() if payload.description else None,
    type=payload.type,
    owner_id=current_user.id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    owner_member = ProjectMember(
        project_id=new_project.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(owner_member)
    db.commit()

    return build_project_response(new_project, db)


"""
取得目前使用者所有專案

邏輯：
- 先找 ProjectMember
- 再查 Project
"""
@router.get("", response_model=list[ProjectResponse])
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memberships = (
        db.query(ProjectMember)
        .filter(ProjectMember.user_id == current_user.id)
        .all()
    )

    project_ids = [member.project_id for member in memberships]

    if not project_ids:
        return []

    projects = (
        db.query(Project)
        .filter(Project.id.in_(project_ids))
        .order_by(Project.created_at.desc())
        .all()
    )

    return [build_project_response(project, db) for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_detail(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ensure_project_member(project_id, current_user.id, db)
    return build_project_response(project, db)


@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_project_member(project_id, current_user.id, db)

    memberships = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id)
        .all()
    )

    result = []
    for membership in memberships:
        user = db.query(User).filter(User.id == membership.user_id).first()
        if user:
            result.append({
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "color": user.color,
                "role": membership.role,
            })

    return result


"""
發送邀請

限制：
- 只能 team project
- 不能邀請自己
- 不能重複邀請
- 不能邀請已是成員的人
"""
@router.post(
    "/{project_id}/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_invitation(
    project_id: int,
    payload: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ensure_project_owner_or_pm(project_id, current_user.id, db)

    if project.type != "team":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only team projects can invite members",
        )

    invited_user = db.query(User).filter(User.id == payload.user_id).first()
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if invited_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot invite yourself",
        )

    existing_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == invited_user.id,
        )
        .first()
    )
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a project member",
        )

    existing_pending = (
        db.query(ProjectInvitation)
        .filter(
            ProjectInvitation.project_id == project_id,
            ProjectInvitation.email == invited_user.email,
            ProjectInvitation.status == "pending",
        )
        .first()
    )
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pending invitation already exists",
        )

    invitation = ProjectInvitation(
        project_id=project_id,
        email=invited_user.email,
        invited_by=current_user.id,
        status="pending",
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation


"""
取得專案內所有任務，依 status + position 排序（Kanban）
"""
@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_project_member(project_id, current_user.id, db)

    tasks = (
        db.query(Task)
        .filter(Task.project_id == project_id)
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


"""
建立任務（project scope）

驗證：
- status / category
- assignee 必須是專案成員
"""
@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_project_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_project_member(project_id, current_user.id, db)

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

        assignee_is_member = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == task_data.assignee_id,
            )
            .first()
        )
        if not assignee_is_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee is not a member of this project",
            )

    existing_tasks = (
        db.query(Task)
        .filter(Task.project_id == project_id, Task.status == task_data.status)
        .all()
    )
    next_position = len(existing_tasks) + 1

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
        completed_at=None,
        project_id=project_id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return build_task_response(new_task, assignee)


"""
刪除專案

限制：
- 只有 owner 可以刪除
"""
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can delete this project",
        )

    db.delete(project)
    db.commit()