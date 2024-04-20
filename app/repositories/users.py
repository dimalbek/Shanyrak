from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..database.models import User, Post
from ..serializers.users import UserCreate, UserLogin, UserUpdate, FavoriteInfo
from typing import List


class UsersRepository:
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        try:
            # Check if the user already exists
            existing_user = db.query(User).filter(
                    User.username == user_data.username).first()

            if existing_user:
                raise HTTPException(
                    status_code=400, detail="User already exists")

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

        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400,
                                detail=f"Integrity error: {str(e)}")
        return new_user

    def get_user_by_username(self, db: Session, user_data: UserLogin) -> User:
        db_user = db.query(User).filter(
            User.username == user_data.username).first()
        if not db_user:
            print(f"User with username {user_data.username} not found")
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    def update_user(self, db: Session, user_id: int, user_data: UserUpdate):
        db_user = db.query(User).filter(User.id == user_id).first()

        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(db_user, field, value)

        try:
            db.commit()
            db.refresh(db_user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid user data")

    def get_by_id(self, db: Session, user_id: int) -> User:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    def add_to_favorites(self, db: Session, user_id: int, post_id: int):
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_post = db.query(Post).filter(Post.id == post_id).first()
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")

        if db_user.favorites is None:
            db_user.favorites = ""

        if str(post_id) in db_user.favorites:
            raise HTTPException(status_code=400,
                                detail="Post already in favorites")
        try:
            db_user.favorites += f"{post_id}, "
            db.commit()
            db.refresh(db_user)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_favorites(self, db: Session, user_id: int) -> List[FavoriteInfo]:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        spliited_favs = db_user.favorites.split(",")
        favs_list = []
        for post_id in spliited_favs:
            db_post = db.query(Post).filter(Post.id == post_id).first()
            if not db_post:
                continue
            favs_list.append(FavoriteInfo(id=post_id, address=db_post.address))
        return favs_list

    def delete_from_favorites(self, db: Session, user_id: int, post_id: int):
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if str(post_id) not in db_user.favorites:
            raise HTTPException(status_code=404,
                                detail="Post not in favorites")

        db_user.favorites = db_user.favorites.replace(f"{post_id},", "")
        db.commit()
        db.refresh(db_user)
