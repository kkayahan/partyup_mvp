from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import Request, HTTPException
from app.core.config import settings

serializer = URLSafeSerializer(settings.SECRET_KEY, salt="csrf")

def generate_csrf_token(session_id: str) -> str:
    return serializer.dumps({"sid": session_id})

def validate_csrf_token(token: str, session_id: str):
    try:
        data = serializer.loads(token)
        if data.get("sid") != session_id:
            raise HTTPException(status_code=400, detail="Invalid CSRF token")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid CSRF token")
