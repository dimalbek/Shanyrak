from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordBearer
from ...repositories.posts import PostRepository
from ...serializers.posts import PostCreate, PostInfo, PostUpdate
from ...repositories.comments import CommentRepository
from ...serializers.comments import CommentCreate, CommentInfo, CommentInfoList
from ...database.database import get_db
from sqlalchemy.orm import Session
from ..auth.auth import decode_jwt

router = APIRouter()
post_repository = PostRepository()
comments_repository = CommentRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")


# Shanyraks


# post shanyrak
@router.post("/")
def post_post(
    post_input: PostCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_jwt(token)
    post_id = str(post_repository.create_post(db, user_id, post_input))
    return {"id": post_id}


# get shanyrak
@router.get("/{id}", response_model=PostInfo)
def get_post(id: int, db: Session = Depends(get_db)):
    db_post = post_repository.get_post_by_id(db, id)
    return db_post


# update shanyrak
@router.patch("/{id}")
def update_post(
    id: int,
    post_input: PostUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_jwt(token)
    post_repository.update_post(db, id, user_id, post_input)
    return Response(content=f"Post with id {user_id} updated", status_code=200)


# delete shanyrak
@router.delete("/{id}")
def delete_post(
    id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    user_id = decode_jwt(token)
    post_repository.delete_post(db, id, user_id)
    return Response(content=f"Post with id {user_id} deleted", status_code=200)


# Comments


# post comment
@router.post("/{id}/comments")
def post_comment(
    comment: CommentCreate,
    id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_jwt(token)
    comment = comments_repository.create_comment(db, user_id, id, comment)
    return Response(
        content=f"Comment with id {comment.id} created to post with id {id}",
        status_code=200,
    )


# get comments
@router.get("/{id}/comments", response_model=CommentInfoList)
def get_comment(id: int, db: Session = Depends(get_db)):
    comments = comments_repository.get_comment_by_post_id(db, id)
    comments_list = []
    for com in comments:
        comments_list.append(
            CommentInfo(
                id=com.id,
                content=com.content,
                created_at=com.created_at,
                author_id=com.author_id,
            )
        )
    return CommentInfoList(comments=comments_list)


# update comment
@router.patch("/{id}/comments/{comment_id}")
def patch_comment(
    content: str,
    id: int,
    comment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_jwt(token)
    comments_repository.update_comment(db, user_id, id, comment_id, content)
    return Response(
        content=f"Comment with id {comment_id} on post with {id} updated",
        status_code=200
    )
