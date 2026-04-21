from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.comment_like import CommentLike
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.utils.deps import get_current_user, get_db

# 建立 comments 路由，所有留言相關 API 都會以 /comments 開頭
router = APIRouter(prefix="/comments", tags=["comments"])

"""
將 Comment ORM 轉換成前端需要的 response 格式

功能：
- 補上 user_name
- 計算 likes 數量
- 判斷目前使用者是否已按讚
"""
def build_comment_response(comment: Comment, db: Session, current_user_id: int):
    
    # 查詢留言作者
    user = db.query(User).filter(User.id == comment.user_id).first()

    # 計算按讚數量
    likes_count = (
        db.query(func.count(CommentLike.id))
        .filter(CommentLike.comment_id == comment.id)
        .scalar()
    ) or 0

    # 判斷目前使用者是否按過讚
    is_liked = (
        db.query(CommentLike)
        .filter(
            CommentLike.comment_id == comment.id,
            CommentLike.user_id == current_user_id,
        )
        .first()
        is not None
    )

    return {
        "id": comment.id,
        "task_id": comment.task_id,
        "user_id": comment.user_id,
        "user_name": user.name if user else "Unknown",
        "content": comment.content,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "likes_count": likes_count,
        "is_liked": is_liked,
    }


"""
取得指定任務的所有留言

流程：
1. 檢查 task 是否存在
2. 查詢該 task 的所有留言
3. 依時間排序（舊 → 新）
4. 轉換成 response 格式
"""
@router.get("/task/{task_id}", response_model=list[CommentResponse])
def get_comments_by_task(
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

    comments = (
        db.query(Comment)
        .filter(Comment.task_id == task_id)
        .order_by(Comment.created_at.asc(), Comment.id.asc())
        .all()
    )

    return [
        build_comment_response(comment, db, current_user.id)
        for comment in comments
    ]


"""
新增留言

流程：
- 檢查 task 是否存在
- 驗證留言內容不可為空
- 建立 Comment
- 回傳完整留言資訊
"""
@router.post("/task/{task_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    content = payload.content.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment content cannot be empty",
        )

    new_comment = Comment(
        task_id=task_id,
        user_id=current_user.id,
        content=content,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return build_comment_response(new_comment, db, current_user.id)


"""
編輯留言

限制：
- 只能修改自己的留言
- 內容不可為空
- 更新 updated_at
"""
@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to edit this comment",
        )

    content = payload.content.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment content cannot be empty",
        )

    comment.content = content
    comment.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(comment)

    return build_comment_response(comment, db, current_user.id)


"""
刪除留言

限制：
- 只能刪除自己的留言
"""
@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete this comment",
        )

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}


"""
切換留言按讚（Like / Unlike）

邏輯：
- 如果已存在 like → 刪除（取消按讚）
- 如果不存在 → 新增 like
"""
@router.post("/{comment_id}/like", status_code=status.HTTP_200_OK)
def toggle_like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    existing_like = (
        db.query(CommentLike)
        .filter(
            CommentLike.comment_id == comment_id,
            CommentLike.user_id == current_user.id,
        )
        .first()
    )

    if existing_like:
        db.delete(existing_like)
        db.commit()
        return {"liked": False}

    new_like = CommentLike(
        comment_id=comment_id,
        user_id=current_user.id,
    )
    db.add(new_like)
    db.commit()

    return {"liked": True}