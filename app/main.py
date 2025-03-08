from fastapi import FastAPI
from app.api import auth
from app.api import shanyraks
from app.utils.middleware import RefreshTokenMiddleware

app = FastAPI()
app.add_middleware(RefreshTokenMiddleware)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(shanyraks.router, prefix="/shanyraks", tags=["shanyraks"])


