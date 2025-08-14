from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.listing import Listing
from app.services.security import get_current_user
from app.services.matching import score

router = APIRouter(prefix="/matching", tags=["matching"])

@router.get("/suggestions")
def suggestions(db: Session = Depends(get_db), user: User = Depends(get_current_user), limit: int = 20):
    # Build a simple user profile based on their last listing (or minimal profile)
    last_listing = db.query(Listing).filter(Listing.user_id == user.id).order_by(Listing.created_at.desc()).first()
    user_profile = {
        "display_name": getattr(user, "display_name", None),
        "language": getattr(user, "language", None),
        "timezone": getattr(user, "timezone", None),
    }
    if last_listing:
        user_profile.update({
            "game": last_listing.game,
            "server": last_listing.server,
            "availability": last_listing.availability,
            "role": (last_listing.team_need or {}).get("preferred_role"),
            "game_specific": last_listing.game_specific,
        })
    # Score other listings
    items = db.query(Listing).filter(Listing.is_active == True, Listing.is_deleted == False, Listing.user_id != user.id).all()
    def to_dict(l: Listing):
        # provide 'age_days' ~ 0 for recency bonus
        return {
            "id": l.id, "user_id": l.user_id, "game": l.game, "server": l.server,
            "language": l.language, "availability": l.availability, "team_need": l.team_need,
            "game_specific": l.game_specific, "age_days": 0
        }
    scored = [{"listing_id": l.id, "score": score(user_profile, to_dict(l))} for l in items]
    scored.sort(key=lambda x: x["score"], reverse=True)
    top_ids = [x["listing_id"] for x in scored[:limit]]
    # return full objects in same order
    id_to_obj = {l.id: l for l in items}
    return [{"score": s["score"], "listing": id_to_obj[s["listing_id"]].__dict__} for s in scored[:limit]]
