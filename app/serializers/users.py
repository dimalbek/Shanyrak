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
