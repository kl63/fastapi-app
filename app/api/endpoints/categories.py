from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_active_admin
from app.crud.category import (
    get_category, get_category_by_slug, get_categories, 
    create_category, update_category, delete_category
)
from app.models.user import User as DBUser
from app.schemas.category import Category, CategoryCreate, CategoryUpdate

router = APIRouter()


@router.get("/", response_model=List[Category])
def get_all_categories(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    parent: Optional[str] = Query(None),
) -> Any:
    """
    Get all categories with pagination and optional parent filter
    """
    skip = (page - 1) * limit
    categories = get_categories(
        db, skip=skip, limit=limit, parent_id=parent
    )
    return categories


@router.get("/{category_id}", response_model=Category)
def get_category_by_id(
    *,
    db: Session = Depends(get_db),
    category_id: str,
) -> Any:
    """
    Get category by ID
    """
    category = get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.get("/slug/{slug}", response_model=Category)
def get_category_by_slug_endpoint(
    *,
    db: Session = Depends(get_db),
    slug: str,
) -> Any:
    """
    Get category by slug
    """
    category = get_category_by_slug(db, slug=slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.post("/", response_model=Category)
def create_category_endpoint(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Create new category (Admin only)
    """
    category = create_category(db, category_in=category_in)
    return category


@router.put("/{category_id}", response_model=Category)
def update_category_endpoint(
    *,
    db: Session = Depends(get_db),
    category_id: str,
    category_in: CategoryUpdate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Update category (Admin only)
    """
    category = get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category = update_category(db, db_category=category, category_in=category_in)
    return category


@router.delete("/{category_id}")
def delete_category_endpoint(
    *,
    db: Session = Depends(get_db),
    category_id: str,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Delete category (Admin only)
    """
    category = get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    success = delete_category(db, category_id=category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with existing products"
        )
    
    return {"message": "Category deleted successfully"}
