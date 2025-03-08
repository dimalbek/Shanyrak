from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Optional
from ..database.models import Post, Comment
from ..schemas.posts import PostCreate, PostUpdate


class PostRepository:
    def create_post(self, db: Session, user_id: int, post_data: PostCreate):
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
                    status_code=400, detail="Following post already exists"
                )

            db_post = Post(**post_data.model_dump(), user_id=user_id)
            db.add(db_post)
            db.commit()
            db.refresh(db_post)

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Integrity error")

        return db_post.id

    def get_post_by_id(self, db: Session, post_id: int):
        db_post = db.query(Post).filter(Post.id == post_id).first()
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")
        db_comments = db.query(Comment).filter(
            Comment.post_id == post_id
        ).all()

        if not db_comments:
            return db_post, 0
        total_comments = len(db_comments)
        return db_post, total_comments

    def update_post(
        self, db: Session, post_id: int, user_id: int, post_data: PostUpdate
    ):
        db_post = db.query(Post).filter(Post.id == post_id).first()

        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")
        if db_post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        for field, value in post_data.model_dump(exclude_unset=True).items():
            setattr(db_post, field, value)

        try:
            db.commit()
            db.refresh(db_post)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Integrity Error")

    def delete_post(self, db: Session, post_id: int, user_id: int):
        db_post = db.query(Post).filter(Post.id == post_id).first()
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")
        if db_post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        db.delete(db_post)
        db.commit()
        return db_post

    def get_posts(
        self,
        db: Session,
        limit: int,
        offset: int,
        type: Optional[str],
        rooms_count: Optional[int],
        price_from: int,
        price_until: Optional[int],
    ):
        db_posts = db.query(Post)
        if type:
            db_posts = db_posts.filter(Post.type == type)
        if rooms_count is not None:
            db_posts = db_posts.filter(Post.rooms_count == rooms_count)
        if price_until is not None:
            db_posts = db_posts.filter(Post.price <= price_until)
        db_posts = db_posts.filter(Post.price >= price_from)
        total_count = db_posts.count()
        db_posts = db_posts.limit(limit).offset(offset).all()
        return db_posts, total_count

