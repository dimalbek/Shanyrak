from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from starlette import status
from typing import Dict, Any
import requests

from ..config import (
    SECRET_KEY,
    REFRESH_SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")


def hash_password(password: str) -> str:
    """Hash the user's password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the hashed password matches the plain password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Create an access JWT token for the given user ID."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"user_id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """Create a refresh JWT token for the given user ID."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"user_id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> int:
    """Decode the access JWT token and extract the user ID."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise JWTError("Invalid token")
        return user_id
    except ExpiredSignatureError:
        raise ExpiredSignatureError("Access token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")


def decode_refresh_token(token: str) -> int:
    """Decode the refresh JWT token and extract the user ID."""
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise JWTError("Invalid refresh token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Extracts the access token from cookies.
    If the token is missing or expired, raises a 401 error.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")
    try:
        user_id = decode_access_token(token)
        return {"user_id": user_id, "access_token": token}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")


async def get_current_user_auto_refresh(request: Request) -> Dict[str, Any]:
    """
    Auto-refresh dependency: If the access token is expired,
    attempts to use the refresh token from cookies to generate a new access token.
    On success, returns a dictionary containing the new access token in the "new_access_token" field.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")
    try:
        user_id = decode_access_token(token)
        return {"user_id": user_id, "access_token": token, "new_access_token": None}
    except ExpiredSignatureError:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=401,
                detail="Access token expired and no refresh token provided",
            )
        try:
            user_id = decode_refresh_token(refresh_token)
            new_access_token = create_access_token(user_id)
            print("NEW ACCESS TOKEN GENERATED")
            return {
                "user_id": user_id,
                "access_token": token,
                "new_access_token": new_access_token,
            }
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
