from fastapi import APIRouter, Depends, Response, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from ...repositories.users import UsersRepository
from ...serializers.users import UserCreate, UserLogin, UserUpdate, UserInfo
from ...database.database import get_db
from sqlalchemy.orm import Session
from pydantic import EmailStr

router = APIRouter()
users_repository = UsersRepository()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")

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
@router.post("/users")
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
@router.post("/users/login")
def post_login(
    # user_input: UserLogin,
    username: EmailStr = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
):
    user_data = UserLogin(username=username, password=password)
    user = users_repository.get_user_by_username(db, user_data)
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_jwt(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


# update user
@router.patch("/users/me")
def patch_user(
    user_input: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = decode_jwt(token)
    # if not user_id:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    user_input.password = hash_password(user_input.password)
    users_repository.update_user(db, user_id, user_input)
    return Response(content="User updated successfully", status_code=200)


# get user info
@router.get("/users/me", response_model=UserInfo)
def get_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    user_id = decode_jwt(token)
    # if not user_id:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    user = users_repository.get_by_id(db, user_id)
    user.phone = user.phone.replace("-", " ")
    return UserInfo(
        id=user_id,
        username=user.username,
        phone=user.phone[4:],
        name=user.name,
        city=user.city,
    )
