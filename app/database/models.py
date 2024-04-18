from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)

    posts = relationship("Post", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True, nullable=False)
    price = Column(Integer, nullable=False)
    address = Column(String, index=True, nullable=False)
    area = Column(Float, nullable=False)
    rooms_count = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="posts")
