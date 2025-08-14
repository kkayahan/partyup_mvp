from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.report import Report
from app.db.schemas.report import ReportCreate
from app.db.models.user import User
from app.services.security import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("")
def create_report(payload: ReportCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    report = Report(reporter_id=user.id, listing_id=payload.listing_id, message_id=payload.message_id, reason=payload.reason, details=payload.details)
    db.add(report); db.commit()
    return {"ok": True}
