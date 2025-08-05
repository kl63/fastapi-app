from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.review import (
    get_product_reviews, get_user_reviews, create_review,
    update_review, delete_review, get_review
)
from app.models.user import User as DBUser
from app.schemas.review import Review, ReviewCreate, ReviewUpdate

router = APIRouter()


@router.get("/product/{product_id}", response_model=List[Review])
def get_product_reviews_endpoint(
    *,
    db: Session = Depends(get_db),
    product_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """
    Get reviews for a product
    """
    reviews = get_product_reviews(db, product_id=product_id, skip=skip, limit=limit)
    return reviews


@router.get("/user", response_model=List[Review])
def get_user_reviews_endpoint(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """
    Get current user's reviews
    """
    reviews = get_user_reviews(db, user_id=current_user.id, skip=skip, limit=limit)
    return reviews


@router.post("/", response_model=Review)
def create_review_endpoint(
    *,
    db: Session = Depends(get_db),
    review_in: ReviewCreate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Create new review
    """
    review = create_review(db, user_id=current_user.id, review_in=review_in)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create review. You may have already reviewed this product."
        )
    return review


@router.put("/{review_id}", response_model=Review)
def update_review_endpoint(
    *,
    db: Session = Depends(get_db),
    review_id: str,
    review_in: ReviewUpdate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Update review
    """
    review = get_review(db, review_id=review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user owns the review
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    review = update_review(db, db_review=review, review_in=review_in)
    return review


@router.delete("/{review_id}")
def delete_review_endpoint(
    *,
    db: Session = Depends(get_db),
    review_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Delete review
    """
    review = get_review(db, review_id=review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user owns the review
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = delete_review(db, review_id=review_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete review"
        )
    
    return {"message": "Review deleted successfully"}
