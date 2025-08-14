from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.templates import templates
from app.db.session import get_db
from app.db.models.user import User
from app.core.config import settings
from app.core.security import verify_password, create_access_token  # mevcut projede var
from sqlalchemy import select

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, next: str | None = None):
    return templates.TemplateResponse("login.html", {"request": request, "next": next})

@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str | None = Form(None),
    db: Session = Depends(get_db)
):
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        # tekrar forma dön
        return templates.TemplateResponse("login.html", 
            {"request": request, "error": "Wrong email or password"}, status_code=401)
    token = create_access_token({"sub": str(user.id)})
    request.session["access_token"] = token
    request.session["user_id"] = user.id
    return RedirectResponse(next or "/feed", status_code=302)

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    display_name: str = Form(...),
    db: Session = Depends(get_db)
):
    if db.execute(select(User).where(User.email == email)).scalar_one_or_none():
        return templates.TemplateResponse("register.html", 
            {"request": request, "error": "Email already registered"}, status_code=400)
    from app.core.security import get_password_hash
    user = User(email=email, display_name=display_name, hashed_password=get_password_hash(password))
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    request.session["access_token"] = token
    request.session["user_id"] = user.id
    return RedirectResponse("/profile", status_code=302)

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)
