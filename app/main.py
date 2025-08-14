from fastapi import FastAPI, Request, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.config import settings
from app.services.rate_limit import RateLimitMiddleware
from app.db.session import get_db
from app.db.models.listing import Listing
from app.core.templates import templates  # <= BURADAN AL



from app.api.routes.auth import router as auth_router
from app.api.routes.listings import router as listings_router
from app.api.routes.messages import router as messages_router
from app.api.routes.reports import router as reports_router
from app.api.routes.matching import router as matching_router
from app.api.routes.ui_auth import router as ui_auth_router   # <= yeni
from app.api.routes.profile import router as profile_router   # <= yeni

app = FastAPI(title="PartyUp")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# JSON API router'ları
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(listings_router, tags=["listings"])
app.include_router(matching_router, prefix="/matching", tags=["matching"])
app.include_router(messages_router, prefix="/messages", tags=["messages"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])

# UI router'ları
app.include_router(ui_auth_router, tags=["ui-auth"])
app.include_router(profile_router, tags=["profile-ui"])

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

# JSON /listings’i yanlışlıkla açanlar için UI feed’e yönlendir
@app.get("/listings", include_in_schema=False)
def listings_redirect():
    return RedirectResponse(url="/feed")

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, limit=120, window=60)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# API routers
app.include_router(auth_router)
app.include_router(listings_router)
app.include_router(messages_router)
app.include_router(reports_router)
app.include_router(matching_router)

# --- UI routes (Jinja + HTMX) ---
@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request, "title": "PartyUp"})

from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.listing import Listing
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

@app.get("/feed", response_class=HTMLResponse)
def feed_page(request: Request, game: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Listing).filter(Listing.is_active == True, Listing.is_deleted == False)
    if game:
        q = q.filter(Listing.game == game)
    listings = q.order_by(Listing.created_at.desc()).limit(50).all()
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings, "selected_game": game})

@app.get("/listings", response_class=HTMLResponse)
def listings_page(request: Request):
    return templates.TemplateResponse("listings_feed.html", {"request": request, "title": "Listings"})

@app.get("/listings/partial", response_class=HTMLResponse)
def listings_partial(request: Request, db: Session = Depends(get_db), game: Optional[str] = None, server: Optional[str] = None,
                     language: Optional[str] = None, availability: Optional[str] = None, tags: Optional[str] = None, q: Optional[str] = None):
    from sqlalchemy import text
    query = db.query(Listing).filter(Listing.is_deleted == False, Listing.is_active == True)
    if game: query = query.filter(Listing.game == game)
    if server: query = query.filter(Listing.server == server)
    if language: query = query.filter(Listing.language == language)
    if availability: query = query.filter(Listing.availability.ilike(f"%{availability}%"))
    if tags:
        arr = [t.strip() for t in tags.split(",") if t.strip()]
        if arr: query = query.filter(text("tags && :tags")).params(tags=arr)
    if q: query = query.filter(text("title ILIKE :q")).params(q=f"%{q}%")
    listings = query.order_by(Listing.created_at.desc()).limit(50).all()
    return templates.TemplateResponse("listings_partial.html", {"request": request, "listings": listings})

@app.get("/listings/new", response_class=HTMLResponse)
def listings_new(request: Request):
    return templates.TemplateResponse("listings_new.html", {"request": request, "title": "New Listing"})

@app.get("/ui/fields", response_class=HTMLResponse)
def fields_partial(request: Request, game: str = "wow"):
    mapping = {
        "wow": "partials/_wow_fields.html",
        "dota2": "partials/_dota2_fields.html",
        "new_world": "partials/_new_world_fields.html",
        "diablo": "partials/_diablo_fields.html",
        "knight_online": "partials/_ko_fields.html",
    }
    tpl = mapping.get(game, "partials/_wow_fields.html")
    return templates.TemplateResponse(tpl, {"request": request})

@app.post("/ui/listings", response_class=HTMLResponse)
async def ui_create_listing(
    request: Request,
    game: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    region: str = Form(None),
    server: str = Form(None),
    language: str = Form("en"),
    playstyle: str = Form(None),
    voice: str = Form(None),
    availability: str = Form(None),
    tags: str = Form(""),
):
    # Minimal demo: store to DB without auth as user_id = 1
    from app.db.session import SessionLocal
    from app.db.models.listing import Listing
    db = SessionLocal()
    try:
        # Collect nested form fields like game_specific[class]
        form = await request.form()
        game_specific = {}
        team_need = {}
        for k, v in form.multi_items():
            if k.startswith("game_specific["):
                key = k[len("game_specific["):-1]
                # checkbox returns "on"
                if v == "on": v = True
                game_specific[key] = v
            if k.startswith("team_need["):
                key = k[len("team_need["):-1]
                team_need[key] = v
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        listing = Listing(
            user_id=1, game=game, title=title, description=description, region=region, server=server,
            language=language, playstyle=playstyle, voice=voice, availability=availability,
            tags=tag_list, game_specific=game_specific, team_need=team_need
        )
        db.add(listing); db.commit(); db.refresh(listing)
    finally:
        db.close()
    return HTMLResponse(f"<div class='p-4 rounded bg-emerald-800/30 border border-emerald-700'>Published listing #{listing.id}</div>")


