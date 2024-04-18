from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordBearer
from ...repositories.posts import PostRepository
from ...serializers.posts import PostCreate, PostInfo, PostUpdate
from ...database.database import get_db
from sqlalchemy.orm import Session
from ..auth.auth import decode_jwt

router = APIRouter()
post_repository = PostRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")


@router.post("/")
def post_post(
    post_input: PostCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_jwt(token)
    post_id = str(post_repository.create_post(db, user_id, post_input))
    return {"id": post_id}


@router.get("/{id}", response_model=PostInfo)
def get_post(id: int, db: Session = Depends(get_db)):
    db_post = post_repository.get_post_by_id(db, id)
    return db_post


@router.patch("/{id}")
def update_post(
    id: int,
    post_input: PostUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = int(decode_jwt(token))
    post_repository.update_post(db, id, user_id, post_input)
    return Response(content=f"Post with id {user_id} updated", status_code=200)


@router.delete("/{id}")
def delete_post(
    id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    user_id = decode_jwt(token)
    post_repository.delete_post(db, id, user_id)
    return Response(content=f"Post with id {user_id} deleted", status_code=200)
