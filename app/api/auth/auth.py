from fastapi import APIRouter, Depends, Form, Request, Response, HTTPException
from jose import jwt
from passlib.context import CryptContext
from ...repositories.users import UsersRepository
from ...serializers.users import UserCreate, UserLogin
from ...database.database import get_db
from sqlalchemy.orm import Session


router = APIRouter()
users_repository = UsersRepository()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(user_id: int) -> str:
    body = {"user_id": user_id}
    token = jwt.encode(body, "shanyrak_secret", "HS256")
    return token


def decode_jwt(token: str) -> int:
    data = jwt.decode(token, "shanyrak_secret", "HS256")
    return data["user_id"]


# registration
@router.post("/signup")
def post_signup(
    user_input: UserCreate,
    db: Session = Depends(get_db),
):
    user_input.password = hash_password(user_input.password)
    new_user = users_repository.create_user(db, user_input)
    return Response(
        status_code=200, content=f"successfull signup. User_id = {new_user.id}"
    )


# login
@router.post("/login")
def post_login(
    user_input: UserLogin, db: Session = Depends(get_db)
):
    user = users_repository.get_user_by_username(db, user_input)
    if not verify_password(user_input.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_jwt(user.id)
    return {"access_token": access_token, "token_type": "bearer"}
