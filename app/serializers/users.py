from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserCreate(BaseModel):
    username: EmailStr
    phone: PhoneNumber = "+7 --- --- ----"
    password: str
    name: str
    city: str


class UserLogin(BaseModel):
    username: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: EmailStr = None
    phone: PhoneNumber = None
    password: str = None
    name: str = None
    city: str = None


class UserInfo(BaseModel):
    id: int
    username: EmailStr
    phone: str
    name: str
    city: str
