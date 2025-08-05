from sqlalchemy import Boolean, Column, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Notification(Base):
    """
    Notification model for user notifications
    """
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    
    # Notification content
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # "order", "promotion", "system", "reminder"
    
    # Notification data
    data = Column(JSON, nullable=True)  # Additional data (order_id, product_id, etc.)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Delivery channels
    sent_email = Column(Boolean, default=False)
    sent_push = Column(Boolean, default=False)
    sent_sms = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.title} - {self.type}>"
