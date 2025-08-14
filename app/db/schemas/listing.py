from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional

class ListingBase(BaseModel):
    game: str
    title: str
    description: str
    region: Optional[str] = None
    server: Optional[str] = None
    language: Optional[str] = None
    playstyle: Optional[str] = None
    voice: Optional[str] = None
    availability: Optional[str] = None
    team_need: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    game_specific: Dict[str, Any] = Field(default_factory=dict)

class ListingCreate(ListingBase):
    pass

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None
    server: Optional[str] = None
    language: Optional[str] = None
    playstyle: Optional[str] = None
    voice: Optional[str] = None
    availability: Optional[str] = None
    team_need: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    game_specific: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ListingOut(ListingBase):
    id: int
    user_id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime         # <— string değil, datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)