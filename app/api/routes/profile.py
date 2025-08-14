from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.templates import templates
from app.db.session import get_db
from app.core.ui_auth_helpers import get_user_from_session

router = APIRouter()

@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_session(request, db)
    if not user:
        return RedirectResponse("/login?next=/profile", status_code=302)
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@router.post("/profile")
def profile_save(
    request: Request,
    display_name: str = Form(...),
    language: str | None = Form(None),
    db: Session = Depends(get_db)
):
    user = get_user_from_session(request, db)
    if not user:
        return RedirectResponse("/login?next=/profile", status_code=302)
    user.display_name = display_name
    if language: 
        user.language = language
    db.add(user); db.commit()
    return RedirectResponse("/profile", status_code=302)
