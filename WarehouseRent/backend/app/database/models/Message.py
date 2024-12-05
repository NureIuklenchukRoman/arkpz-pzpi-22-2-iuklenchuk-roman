from sqlalchemy import Column, Integer, Float, ForeignKey, String, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime
from ..base_model import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="message")
