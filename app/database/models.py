from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    DateTime,
)
from .database import Base
from sqlalchemy.orm import relationship
import pytz
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    favorites = Column(String, nullable=True)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, index=True, nullable=False)
    price = Column(Integer, nullable=False)
    address = Column(String, index=True, nullable=False)
    area = Column(Float, nullable=False)
    rooms_count = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(
        pytz.timezone('Asia/Almaty')))

    author_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
