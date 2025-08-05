from typing import Any, Dict, Optional, Union, List
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


def get_notification(db: Session, notification_id: str) -> Optional[Notification]:
    """Get notification by ID"""
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_user_notifications(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    unread_only: bool = False
) -> List[Notification]:
    """Get user's notifications"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def create_notification(db: Session, notification_in: NotificationCreate) -> Optional[Notification]:
    """Create new notification"""
    try:
        notification_id = str(uuid.uuid4())
        db_notification = Notification(
            id=notification_id,
            user_id=notification_in.user_id,
            title=notification_in.title,
            message=notification_in.message,
            type=notification_in.type,
            data=notification_in.data,
            channels=notification_in.channels,
            is_read=False,
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except Exception:
        db.rollback()
        return None


def mark_notification_as_read(db: Session, notification_id: str) -> bool:
    """Mark notification as read"""
    try:
        notification = get_notification(db, notification_id)
        if not notification:
            return False
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.add(notification)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def mark_all_notifications_as_read(db: Session, user_id: str) -> bool:
    """Mark all user notifications as read"""
    try:
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def delete_notification(db: Session, notification_id: str) -> bool:
    """Delete notification"""
    try:
        notification = get_notification(db, notification_id=notification_id)
        if not notification:
            return False
        
        db.delete(notification)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def get_unread_count(db: Session, user_id: str) -> int:
    """Get count of unread notifications for user"""
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()
