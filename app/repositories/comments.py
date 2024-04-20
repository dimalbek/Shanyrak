from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..database.models import Comment, Post, User
from ..serializers.comments import CommentCreate


class CommentRepository:
    def create_comment(
        self, db: Session,
        user_id: int,
        post_id: int,
        comment_data: CommentCreate
    ):
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            db_post = db.query(Post).filter(Post.id == post_id).first()

            if not db_post:
                raise HTTPException(status_code=404, detail="Post not found")
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            new_comment = Comment(
                content=comment_data.content,
                author_id=user_id,
                post_id=post_id,
            )

            db.add(new_comment)
            db.commit()
            db.refresh(new_comment)

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Integrity error")

        return new_comment

    def get_comment_by_post_id(
        self, db: Session, post_id: int
    ) -> list[Comment]:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Not found such Post")

        comments = db.query(Comment).filter(Comment.post_id == post_id).all()
        return comments

    def update_comment(
        self, db: Session,
        user_id: int,
        post_id: int,
        comment_id: int,
        content: str,
    ):
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_post = db.query(Post).filter(Post.id == post_id).first()
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")

        db_comment = db.query(Comment).filter(
            Comment.id == comment_id,
            Comment.post_id == post_id
        ).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        if db_comment.author_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        db_comment.content = content
        try:
            db.commit()
            db.refresh(db_comment)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))