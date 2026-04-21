from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_invitation import ProjectInvitation
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project import InvitationResponse
from app.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/invitations", tags=["invitations"])

#將 Invitation ORM 轉為前端顯示格式
def build_invitation_response(
    invitation: ProjectInvitation,
    project: Project | None,
    inviter: User | None,
):
    return {
        "id": invitation.id,
        "project_id": invitation.project_id,
        "project_name": project.name if project else f"Project #{invitation.project_id}",
        "email": invitation.email,
        "invited_by": invitation.invited_by,
        "inviter_name": inviter.name if inviter else None,
        "inviter_email": inviter.email if inviter else None,
        "status": invitation.status,
        "created_at": invitation.created_at,
        "responded_at": invitation.responded_at,
    }

"""
取得目前使用者的所有邀請

條件：
- email = current_user.email
- status = pending
"""
@router.get("/my", response_model=list[InvitationResponse])
def get_my_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invitations = (
        db.query(ProjectInvitation)
        .filter(
            ProjectInvitation.email == current_user.email,
            ProjectInvitation.status == "pending",
        )
        .order_by(ProjectInvitation.created_at.desc())
        .all()
    )

    result = []
    for invitation in invitations:
        project = (
            db.query(Project)
            .filter(Project.id == invitation.project_id)
            .first()
        )
        inviter = (
            db.query(User)
            .filter(User.id == invitation.invited_by)
            .first()
        )

        result.append(build_invitation_response(invitation, project, inviter))

    return result

"""
接受邀請

流程：
- 驗證 invitation 是否存在
- 驗證是否為本人
- 建立 ProjectMember（若不存在）
- 更新 status = accepted
"""
@router.post("/{invitation_id}/accept", response_model=InvitationResponse)
def accept_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invitation = (
        db.query(ProjectInvitation)
        .filter(ProjectInvitation.id == invitation_id)
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.email.lower() != current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot accept this invitation",
        )

    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation is no longer pending",
        )

    project = db.query(Project).filter(Project.id == invitation.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    existing_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == invitation.project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )

    if not existing_member:
        db.add(
            ProjectMember(
                project_id=invitation.project_id,
                user_id=current_user.id,
                role="member",
            )
        )

    invitation.status = "accepted"
    invitation.responded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(invitation)

    inviter = db.query(User).filter(User.id == invitation.invited_by).first()
    return build_invitation_response(invitation, project, inviter)


"""
拒絕邀請

流程：
- 驗證 invitation
- 更新 status = declined
"""
@router.post("/{invitation_id}/decline", response_model=InvitationResponse)
def decline_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invitation = (
        db.query(ProjectInvitation)
        .filter(ProjectInvitation.id == invitation_id)
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )

    if invitation.email.lower() != current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot decline this invitation",
        )

    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation is no longer pending",
        )

    invitation.status = "declined"
    invitation.responded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(invitation)

    project = db.query(Project).filter(Project.id == invitation.project_id).first()
    inviter = db.query(User).filter(User.id == invitation.invited_by).first()

    return build_invitation_response(invitation, project, inviter)