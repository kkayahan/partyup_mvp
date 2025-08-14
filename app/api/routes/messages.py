from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.message import Message
from app.db.models.user import User
from app.db.schemas.message import MessageCreate, MessageOut
from app.services.security import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("", response_model=MessageOut)
def send_message(payload: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    msg = Message(listing_id=payload.listing_id, sender_id=user.id, receiver_id=payload.receiver_id, content=payload.content)
    db.add(msg); db.commit(); db.refresh(msg)
    return msg

@router.get("/thread/{other_user_id}", response_model=List[MessageOut])
def get_thread(other_user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    msgs = db.query(Message).filter(
        ((Message.sender_id == user.id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user.id))
    ).order_by(Message.created_at.asc()).all()
    return msgs
