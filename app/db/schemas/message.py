from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class MessageCreate(BaseModel):
    listing_id: int
    receiver_id: int
    content: str

class MessageOut(BaseModel):
    id: int
    listing_id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime         # <— datetime

    model_config = ConfigDict(from_attributes=True)
