from typing import Any, Dict, Optional, Union, List
import uuid
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: str) -> Optional[Category]:
    """Get category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
    """Get category by slug"""
    return db.query(Category).filter(Category.slug == slug).first()


def get_categories(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    parent_id: Optional[str] = None
) -> List[Category]:
    """Get multiple categories with pagination and optional parent filter"""
    query = db.query(Category).filter(Category.is_active == True)
    
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    
    return query.order_by(Category.sort_order, Category.name).offset(skip).limit(limit).all()


def create_category(db: Session, category_in: CategoryCreate) -> Category:
    """Create new category"""
    category_id = str(uuid.uuid4())
    db_category = Category(
        id=category_id,
        name=category_in.name,
        slug=category_in.slug,
        description=category_in.description,
        icon=category_in.icon,
        image=category_in.image,
        parent_id=category_in.parent_id,
        is_active=category_in.is_active,
        is_featured=category_in.is_featured,
        sort_order=category_in.sort_order,
        meta_title=category_in.meta_title,
        meta_description=category_in.meta_description,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
    db: Session, 
    db_category: Category, 
    category_in: Union[CategoryUpdate, Dict[str, Any]]
) -> Category:
    """Update category"""
    if isinstance(category_in, dict):
        update_data = category_in
    else:
        update_data = category_in.dict(exclude_unset=True)
    
    # Update category attributes
    for field in update_data:
        if hasattr(db_category, field):
            setattr(db_category, field, update_data[field])
            
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: str) -> bool:
    """Delete category"""
    try:
        category = get_category(db, category_id=category_id)
        if not category:
            return False
        
        # Check if category has products (you might want to prevent deletion)
        # For now, we'll just delete it
        db.delete(category)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
