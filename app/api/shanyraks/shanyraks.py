from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from ...repositories.posts import PostRepository
from ...serializers.posts import PostCreate, PostInfo
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
