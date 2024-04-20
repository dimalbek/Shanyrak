from pydantic import BaseModel
from typing import List


class PostCreate(BaseModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str


class PostInfo(BaseModel):
    id: int
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str
    user_id: int
    total_comments: int


class PostUpdate(BaseModel):
    type: str = None
    price: int = None
    address: str = None
    area: float = None
    rooms_count: int = None
    description: str = None


class SearchShanyrak(BaseModel):
    id: int
    type: str
    price: int
    address: str
    area: float
    rooms_count: int


class SearchShanyrakList(BaseModel):
    total: int
    objects: List[SearchShanyrak]
