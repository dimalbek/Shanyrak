from fastapi import APIRouter, Depends, Response, HTTPException, Form, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import EmailStr
from datetime import timedelta
from jose import JWTError, jwt, ExpiredSignatureError
from ..repositories.users import UsersRepository
from ..schemas.users import UserCreate, UserLogin, UserUpdate, UserInfo, FavoritesList
from ..database.database import get_db
from ..utils.security import (
    hash_password,
    verify_password,
    decode_access_token,
    decode_refresh_token,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_user_auto_refresh,
)

router = APIRouter()
users_repository = UsersRepository()


# Endpoint to refresh the access token
@router.post("/refresh")
def refresh(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    try:
        user_id = decode_refresh_token(refresh_token)
        new_access_token = create_access_token(user_id)
    except JWTError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid refresh token", 
            headers={"WWW-Authenticate": "Bearer"}
        )

    response = JSONResponse(
        content={"access_token": new_access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="access_token", value=new_access_token, httponly=True, samesite="lax"
    )
    print(f"NEW ACCESS TOKEN GENERATED: {new_access_token}")
    return response


# Registration
@router.post("/users")
def post_signup(user_input: UserCreate, db: Session = Depends(get_db)):
    user_input.password = hash_password(user_input.password)
    new_user = users_repository.create_user(db, user_input)
    return Response(
        status_code=201, content=f"Successful signup. User_id = {new_user.id}"
    )


# Login
@router.post("/users/login")
def post_login(
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
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )

    response.set_cookie(
        key="access_token", value=access_token, httponly=True, samesite="lax"
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, samesite="lax"
    )
    return response


# Update user
@router.patch("/users/me")
def patch_user(
    user_input: UserUpdate,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user_data["user_id"]
    if user_input.password:
        user_input.password = hash_password(user_input.password)
    users_repository.update_user(db, user_id, user_input)
    return {
        "message": "User updated successfully",
    }


# Get user info
@router.get("/users/me", response_model=UserInfo)
def get_user(
    user_data: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_id = user_data["user_id"]
    user = users_repository.get_by_id(db, user_id)
    user.phone = user.phone.replace("-", " ")
    response_data = UserInfo(
        id=user_id,
        username=user.username,
        phone=user.phone[4:],
        name=user.name,
        city=user.city,
    )

    return response_data


# Add to favorites
@router.post("/users/favorites/shanyraks/{id}")
def add_to_favorites(
    id: int,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user_data["user_id"]
    users_repository.add_to_favorites(db, user_id, id)
    return {
        "message": f"Post with id {id} added to favorites",
    }


# Get favorites
@router.get("/users/favorites/shanyraks", response_model=FavoritesList)
def get_favorites(
    user_data: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_id = user_data["user_id"]
    shanyraks_list = users_repository.get_favorites(db, user_id)
    return FavoritesList(shanyraks=shanyraks_list)


# Delete from favorites
@router.delete("/users/favorites/shanyraks/{id}")
def delete_favorite(
    id: int, user_data: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_id = user_data["user_id"]
    users_repository.delete_from_favorites(db, user_id, id)
    return {
        "message": f"Post with id {id} deleted from favorites",
    }
