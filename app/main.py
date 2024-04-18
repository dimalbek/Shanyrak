from fastapi import FastAPI
from app.api.auth import auth
from app.api.shanyraks import shanyraks

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(shanyraks.router, prefix="/shanyraks", tags=["shanyraks"])
