from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..database.models import Post
from ..serializers.posts import PostCreate


class PostRepository:
    @staticmethod
    def create_post(db: Session, user_id: int, post_data: PostCreate):
        try:
            existing_post = (
                db.query(Post)
                .filter(
                    Post.user_id == user_id,
                    Post.type == post_data.type,
                    Post.price == post_data.price,
                    Post.address == post_data.address,
                    Post.area == post_data.area,
                    Post.rooms_count == post_data.rooms_count,
                    Post.description == post_data.description,
                )
                .first()
            )

            if existing_post:
                raise HTTPException(
                    status_code=400, detail="Following post already exists")

            db_post = Post(**post_data.model_dump(), user_id=user_id)
            db.add(db_post)
            db.commit()
            db.refresh(db_post)

        except Exception:
            db.rollback()
            raise HTTPException(status_code=400, detail="Integrity error")

        return db_post.id
