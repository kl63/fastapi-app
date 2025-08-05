from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_active_admin
from app.crud.notification import (
    get_user_notifications, get_notification, mark_notification_as_read,
    mark_all_notifications_as_read, delete_notification, create_notification
)
from app.models.user import User as DBUser
from app.schemas.notification import Notification, NotificationCreate, NotificationMarkRead

router = APIRouter()


@router.get("/", response_model=List[Notification])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    unread_only: bool = Query(False),
) -> Any:
    """
    Get user's notifications
    """
    notifications = get_user_notifications(
        db, user_id=current_user.id, skip=skip, limit=limit, unread_only=unread_only
    )
    return notifications


@router.get("/{notification_id}", response_model=Notification)
def get_notification_endpoint(
    *,
    db: Session = Depends(get_db),
    notification_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get specific notification by ID
    """
    notification = get_notification(db, notification_id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Check if user owns the notification
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return notification


@router.put("/{notification_id}/read")
def mark_notification_read(
    *,
    db: Session = Depends(get_db),
    notification_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Mark notification as read
    """
    notification = get_notification(db, notification_id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Check if user owns the notification
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = mark_notification_as_read(db, notification_id=notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not mark notification as read"
        )
    
    return {"message": "Notification marked as read"}


@router.put("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Mark all notifications as read
    """
    success = mark_all_notifications_as_read(db, user_id=current_user.id)
    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}")
def delete_notification_endpoint(
    *,
    db: Session = Depends(get_db),
    notification_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Delete notification
    """
    notification = get_notification(db, notification_id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Check if user owns the notification
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = delete_notification(db, notification_id=notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete notification"
        )
    
    return {"message": "Notification deleted successfully"}


# Admin endpoint
@router.post("/send")
def send_notification_admin(
    *,
    db: Session = Depends(get_db),
    notification_in: NotificationCreate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Send notification to user (admin only)
    """
    notification = create_notification(db, notification_in=notification_in)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create notification"
        )
    
    return {"message": "Notification sent successfully"}
