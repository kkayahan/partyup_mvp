from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from app.db.base import Base

class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    game = Column(String(32), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    region = Column(String(64))
    server = Column(String(128))
    language = Column(String(8), nullable=False, index=True)
    playstyle = Column(String(32))
    voice = Column(String(32))
    availability = Column(String(128))
    team_need = Column(JSONB, nullable=False, server_default='{}')
    tags = Column(ARRAY(String(32)), nullable=False, server_default='{}')
    game_specific = Column(JSONB, nullable=False, server_default='{}')
    is_active = Column(Boolean, nullable=False, server_default='true')
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
