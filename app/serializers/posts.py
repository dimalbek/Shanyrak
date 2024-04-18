from pydantic import BaseModel


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
