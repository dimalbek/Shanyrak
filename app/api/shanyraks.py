import enum
from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session
from pydantic import EmailStr
from typing import Optional
from ..repositories.posts import PostRepository
from ..schemas.posts import (
    PostCreate,
    PostInfo,
    PostUpdate,
    SearchShanyrak,
    SearchShanyrakList,
)
from ..repositories.comments import CommentRepository
from ..schemas.comments import CommentCreate, CommentInfo, CommentInfoList
from ..database.database import get_db
from ..utils.security import (
    get_current_user,
)

router = APIRouter()
post_repository = PostRepository()
comments_repository = CommentRepository()

class PostType(str, enum.Enum):
    rent = "rent"
    buy = "buy"


# Shanyraks

# Create post (shanyrak)
@router.post("/")
def post_post(
    post_input: PostCreate,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user_data["user_id"]
    post_id = str(post_repository.create_post(db, user_id, post_input))
    return {"id": post_id}


# Get post
@router.get("/{id}", response_model=PostInfo)
def get_post(id: int, db: Session = Depends(get_db)):
    db_post, total_comments = post_repository.get_post_by_id(db, id)
    return PostInfo(**db_post.__dict__, total_comments=total_comments)


# Update post
@router.patch("/{id}")
def update_post(
    id: int,
    post_input: PostUpdate,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user_data["user_id"]
    post_repository.update_post(db, id, user_id, post_input)
    return Response(content=f"Post with id {id} updated", status_code=200)


# Delete post
@router.delete("/{id}")
def delete_post(
    id: int,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user_data["user_id"]
    post_repository.delete_post(db, id, user_id)
    return Response(content=f"Post with id {id} deleted", status_code=200)


# Comments

# Create comment
@router.post("/{id}/comments")
def post_comment(
    comment: CommentCreate,
    id: int,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user_data["user_id"]
    new_comment = comments_repository.create_comment(db, user_id, id, comment)
    return Response(
        status_code=200,
        content=f"Comment with id {new_comment.id} created for post with id {id}",
    )


# Get comments
@router.get("/{id}/comments", response_model=CommentInfoList)
def get_comment(id: int, db: Session = Depends(get_db)):
    comments = comments_repository.get_comment_by_post_id(db, id)
    comments_list = [
        CommentInfo(
            id=com.id,
            content=com.content,
            created_at=com.created_at,
            author_id=com.author_id,
        )
        for com in comments
    ]
    return CommentInfoList(comments=comments_list)


# Update comment
@router.patch("/{id}/comments/{comment_id}")
def patch_comment(
    content: str,
    id: int,
    comment_id: int,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user_data["user_id"]
    comments_repository.update_comment(db, user_id, id, comment_id, content)
    return Response(
        status_code=200,
        content=f"Comment with id {comment_id} on post {id} updated",
    )


# Delete comment
@router.delete("/{id}/comments/{comment_id}")
def delete_comment(
    id: int,
    comment_id: int,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user_data["user_id"]
    comments_repository.delete_comment(db, user_id, id, comment_id)
    return Response(
        status_code=200,
        content=f"Comment with id {comment_id} on post {id} deleted",
    )


# Search & Pagination
@router.get("/", response_model=SearchShanyrakList)
def search_posts(
    db: Session = Depends(get_db),
    limit: int = Query(5, ge=1, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    type: Optional[PostType] = Query(None, description="Post type (rent, buy, sale)"),
    rooms_count: Optional[int] = Query(None, ge=0, description="Required number of rooms"),
    price_from: int = Query(0, ge=0, description="Minimum price"),
    price_until: Optional[int] = Query(None, ge=0, description="Maximum price"),
):
    posts, total_count = post_repository.get_posts(
        db, limit, offset, type, rooms_count, price_from, price_until
    )
    posts_list_formatted = [SearchShanyrak.model_validate(post.__dict__) for post in posts]
    return SearchShanyrakList(total=total_count, objects=posts_list_formatted)
