from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
from app.db.session import get_db
from app.db.models.listing import Listing
from app.db.schemas.listing import ListingCreate, ListingOut, ListingUpdate
from app.services.security import get_current_user
from app.db.models.user import User

# eskisi (soruna sebep oluyor)
# from app.main import templates

# yenisi
from app.core.templates import templates


router = APIRouter(prefix="/listings", tags=["listings"])

@router.post("", response_model=ListingOut)
def create_listing(payload: ListingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    listing = Listing(user_id=user.id, **payload.dict())
    db.add(listing); db.commit(); db.refresh(listing)
    return listing

@router.get("", response_model=List[ListingOut])
def list_listings(
    db: Session = Depends(get_db),
    game: Optional[str] = None,
    server: Optional[str] = None,
    language: Optional[str] = None,
    availability: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    q: Optional[str] = Query(None, description="Search title"),
    limit: int = 50,
):
    query = db.query(Listing).filter(Listing.is_deleted == False, Listing.is_active == True)
    if game:
        query = query.filter(Listing.game == game)
    if server:
        query = query.filter(Listing.server == server)
    if language:
        query = query.filter(Listing.language == language)
    if availability:
        query = query.filter(Listing.availability.ilike(f"%{availability}%"))
    if tags:
        arr = [t.strip() for t in tags.split(",") if t.strip()]
        if arr:
            query = query.filter(text("tags && :tags")).params(tags=arr)
    if q:
        query = query.filter(text("title ILIKE :q")).params(q=f"%{q}%")
    return query.order_by(Listing.created_at.desc()).limit(limit).all()

@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.get(Listing, listing_id)
    if not listing or listing.is_deleted:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@router.patch("/{listing_id}", response_model=ListingOut)
def patch_listing(listing_id: int, payload: ListingUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    listing = db.get(Listing, listing_id)
    if not listing or listing.is_deleted:
        raise HTTPException(status_code=404, detail="Not found")
    if listing.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(listing, k, v)
    db.add(listing); db.commit(); db.refresh(listing)
    return listing

@router.delete("/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    listing = db.get(Listing, listing_id)
    if not listing or listing.is_deleted:
        raise HTTPException(status_code=404, detail="Not found")
    if listing.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not owner")
    listing.is_deleted = True; listing.is_active = False
    db.add(listing); db.commit()
    return {"ok": True}


# app/api/routes/listings.py
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.listing import Listing
from app.main import templates  # Jinja2Templates instance

router = APIRouter()

@router.get("/feed", response_class=HTMLResponse)
def feed_page(
    request: Request,
    game: str | None = Query(None),
    server: str | None = Query(None),
    language: str | None = Query(None),
    tags: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Listing).filter(Listing.is_active == True, Listing.is_deleted == False)
    if game: q = q.filter(Listing.game == game)
    if server: q = q.filter(Listing.server.ilike(f"%{server}%"))
    if language: q = q.filter(Listing.language == language)
    if tags:
        # basit tag araması: JSONB array @> [tag]
        for t in [t.strip() for t in tags.split(",") if t.strip()]:
            q = q.filter(Listing.tags.contains([t]))
    listings = q.order_by(Listing.created_at.desc()).limit(60).all()
    return templates.TemplateResponse(
        "listings_feed.html",
        {"request": request, "listings": listings},
    )

from fastapi import APIRouter, Depends, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.listing import Listing
from app.db.schemas.listing import ListingCreate
from app.core.templates import templates
from app.core.config import settings

router = APIRouter()

@router.get("/feed", response_class=HTMLResponse)
def feed_page(
    request: Request,
    game: str | None = Query(None),
    server: str | None = Query(None),
    language: str | None = Query(None),
    tags: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Listing).filter(Listing.is_active == True, Listing.is_deleted == False)
    if game: q = q.filter(Listing.game == game)
    if server: q = q.filter(Listing.server.ilike(f"%{server}%"))
    if language: q = q.filter(Listing.language == language)
    if tags:
        for t in [t.strip() for t in tags.split(",") if t.strip()]:
            q = q.filter(Listing.tags.contains([t]))
    listings = q.order_by(Listing.created_at.desc()).limit(60).all()
    return templates.TemplateResponse("listings_feed.html",
        {"request": request, "listings": listings})

@router.get("/listings/new", response_class=HTMLResponse)
def new_listing_form(request: Request):
    return templates.TemplateResponse("listings_new.html", {"request": request})

@router.post("/ui/listings")
def create_listing_ui(
    request: Request,
    game: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    region: str | None = Form(None),
    server: str | None = Form(None),
    language: str | None = Form(None),
    playstyle: str | None = Form(None),
    voice: str | None = Form(None),
    availability: str | None = Form(None),
    tags: str | None = Form(None),
    db: Session = Depends(get_db),
):
    from app.db.models.user import User
    # basit auth: sessiondaki token’dan kullanıcıyı çöz (UI login birazdan)
    from app.core.ui_auth_helpers import get_user_from_session
    user = get_user_from_session(request, db)
    if not user:
        return RedirectResponse("/login?next=/listings/new", status_code=302)

    tags_list = [t.strip() for t in (tags or "").split(",") if t.strip()]
    lc = ListingCreate(
        game=game, title=title, description=description, region=region, server=server,
        language=language, playstyle=playstyle, voice=voice,
        availability=availability, tags=tags_list, team_need={}, game_specific={}
    )
    listing = Listing(**lc.dict(), user_id=user.id)
    db.add(listing); db.commit(); db.refresh(listing)
    return RedirectResponse(f"/feed?game={game}", status_code=302)
