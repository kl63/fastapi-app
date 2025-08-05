from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification type enum"""
    ORDER_UPDATE = "order_update"
    PROMOTION = "promotion"
    SYSTEM = "system"
    REMINDER = "reminder"


class NotificationChannel(str, Enum):
    """Notification delivery channel enum"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationBase(BaseModel):
    """Base notification schema"""
    user_id: str
    title: str
    message: str
    type: NotificationType
    data: Optional[Dict[str, Any]] = None
    channels: list[NotificationChannel] = [NotificationChannel.IN_APP]


class NotificationCreate(NotificationBase):
    """Schema for creating notification"""
    pass


class NotificationInDBBase(NotificationBase):
    """Base notification schema for DB"""
    id: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Notification(NotificationInDBBase):
    """Notification response schema"""
    pass


class NotificationInDB(NotificationInDBBase):
    """Notification schema for DB operations"""
    pass


class NotificationMarkRead(BaseModel):
    """Schema for marking notification as read"""
    is_read: bool = True
