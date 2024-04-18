from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..database.models import User
from pydantic import BaseModel, EmailStr
from ..serializers.users import UserCreate


class UsersRepository:
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        try:
            # Check if the user already exists
            existing_user = db.query(User).filter(
                User.username == user_data.username
            ).first()

            if existing_user:
                raise HTTPException(
                    status_code=400, detail="User already exists"
                )

            new_user = User(
                username=user_data.username,
                phone=user_data.phone,
                password=user_data.password,
                name=user_data.name,
                city=user_data.city,
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="User already exists")
        return new_user
