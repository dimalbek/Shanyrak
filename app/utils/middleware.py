# middleware.py
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import ExpiredSignatureError
from app.utils.security import decode_access_token, decode_refresh_token, create_access_token

class RefreshTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        new_access_token = None

        # Извлекаем access token из заголовка (формат "Bearer <token>")
        auth: str = request.headers.get("Authorization")
        token = None
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ")[1]

        if token:
            try:
                # Пытаемся декодировать access token
                _ = decode_access_token(token)
            except ExpiredSignatureError:
                # Если access token истёк, ищем refresh token в cookie
                refresh_token = request.cookies.get("refresh_token")
                if refresh_token:
                    try:
                        # Проверяем refresh token
                        user_id = decode_refresh_token(refresh_token)
                        # Создаем новый access token
                        new_access_token = create_access_token(user_id)
                        # Сохраняем новый токен в request.state, чтобы зависимость его увидела
                        request.state.new_access_token = new_access_token
                        print("NEW ACCESS TOKEN GENERATED")
                    except Exception as e:
                        # Если refresh token недействителен, можно кинуть исключение или просто продолжить
                        raise HTTPException(status_code=401, detail="Invalid refresh token")
                else:
                    raise HTTPException(status_code=401, detail="Access token expired. Refresh token required.")

        # Продолжаем выполнение запроса
        response: Response = await call_next(request)

        # Если новый токен создан, устанавливаем его в куки и (опционально) в заголовок ответа
        if new_access_token:
            response.set_cookie(key="access_token", value=new_access_token, httponly=True, samesite="lax")
            response.headers["X-New-Access-Token"] = new_access_token

        return response
