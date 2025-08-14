from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.user import User

ALGO = getattr(settings, "JWT_ALGORITHM", "HS256")

def get_user_from_session(request, db: Session) -> User | None:
    token = request.session.get("access_token")
    if not token: 
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGO])
        sub = payload.get("sub")
        if not sub: 
            return None
        user = db.get(User, int(sub))
        return user
    except JWTError:
        return None
