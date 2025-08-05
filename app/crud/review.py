from typing import Any, Dict, Optional, Union, List
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.review import Review
from app.models.product import Product
from app.schemas.review import ReviewCreate, ReviewUpdate


def get_review(db: Session, review_id: str) -> Optional[Review]:
    """Get review by ID"""
    return db.query(Review).filter(Review.id == review_id).first()


def get_product_reviews(
    db: Session, 
    product_id: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[Review]:
    """Get reviews for a product"""
    return db.query(Review).filter(
        Review.product_id == product_id
    ).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()


def get_user_reviews(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[Review]:
    """Get reviews by a user"""
    return db.query(Review).filter(
        Review.user_id == user_id
    ).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()


def get_user_product_review(db: Session, user_id: str, product_id: str) -> Optional[Review]:
    """Get user's review for a specific product"""
    return db.query(Review).filter(
        and_(
            Review.user_id == user_id,
            Review.product_id == product_id
        )
    ).first()


def create_review(db: Session, user_id: str, review_in: ReviewCreate) -> Optional[Review]:
    """Create new review"""
    # Check if product exists
    product = db.query(Product).filter(Product.id == review_in.product_id).first()
    if not product:
        return None
    
    # Check if user already reviewed this product
    existing_review = get_user_product_review(db, user_id, review_in.product_id)
    if existing_review:
        return None  # User already reviewed this product
    
    # Create new review
    review_id = str(uuid.uuid4())
    db_review = Review(
        id=review_id,
        user_id=user_id,
        product_id=review_in.product_id,
        rating=review_in.rating,
        title=review_in.title,
        comment=review_in.comment,
        is_verified=False,  # TODO: Verify if user actually purchased the product
        helpful_count=0,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Update product rating average
    update_product_rating(db, review_in.product_id)
    
    return db_review


def update_review(
    db: Session, 
    db_review: Review, 
    review_in: Union[ReviewUpdate, Dict[str, Any]]
) -> Review:
    """Update review"""
    if isinstance(review_in, dict):
        update_data = review_in
    else:
        update_data = review_in.dict(exclude_unset=True)
    
    # Update review attributes
    for field in update_data:
        if hasattr(db_review, field):
            setattr(db_review, field, update_data[field])
            
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Update product rating average
    update_product_rating(db, db_review.product_id)
    
    return db_review


def delete_review(db: Session, review_id: str) -> bool:
    """Delete review"""
    try:
        review = get_review(db, review_id=review_id)
        if not review:
            return False
        
        product_id = review.product_id
        db.delete(review)
        db.commit()
        
        # Update product rating average
        update_product_rating(db, product_id)
        
        return True
    except Exception:
        db.rollback()
        return False


def update_product_rating(db: Session, product_id: str):
    """Update product's average rating and review count"""
    try:
        reviews = db.query(Review).filter(Review.product_id == product_id).all()
        
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
            review_count = len(reviews)
        else:
            avg_rating = 0.0
            review_count = 0
        
        # Update product
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.rating_average = round(avg_rating, 2)
            product.review_count = review_count
            db.add(product)
            db.commit()
            
    except Exception:
        db.rollback()
