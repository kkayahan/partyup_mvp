from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id", ondelete="CASCADE"), index=True, nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), index=True, nullable=True)
    reason = Column(String(64), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(32), nullable=False, default="open")
