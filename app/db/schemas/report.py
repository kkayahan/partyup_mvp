from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ReportCreate(BaseModel):
    listing_id: Optional[int] = None
    message_id: Optional[int] = None
    reason: str
    details: Optional[str] = None

class ReportOut(BaseModel):
    id: int
    reporter_id: int
    listing_id: Optional[int] = None
    message_id: Optional[int] = None
    reason: str
    details: Optional[str] = None
    status: str
    created_at: datetime         # <— datetime

    model_config = ConfigDict(from_attributes=True)
