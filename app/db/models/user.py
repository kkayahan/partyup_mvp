from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(120), nullable=False)
    language = Column(String(8), nullable=False, default="en")
    timezone = Column(String(64), nullable=False, default="Europe/Amsterdam")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    profile = Column(JSONB, nullable=False, server_default='{}')
