from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_active_admin
from app.crud.product import (
    get_product, get_product_by_slug, get_products, get_featured_products,
    get_related_products, search_products, create_product, update_product, 
    delete_product, update_product_stock
)
from app.models.user import User as DBUser
from app.schemas.product import (
    Product, ProductSummary, ProductCreate, ProductUpdate, ProductStockUpdate
)

router = APIRouter()


@router.get("/", response_model=List[ProductSummary])
def get_all_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock: Optional[bool] = Query(None),
    is_organic: Optional[bool] = Query(None),
    is_on_sale: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("name", regex="^(price|name|rating|newest)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
) -> Any:
    """
    Get all products with filtering and pagination
    """
    skip = (page - 1) * limit
    
    filters = {
        "category": category,
        "search": search,
        "min_price": min_price,
        "max_price": max_price,
        "in_stock": in_stock,
        "is_organic": is_organic,
        "is_on_sale": is_on_sale,
    }
    
    products = get_products(
        db, skip=skip, limit=limit, filters=filters, 
        sort_by=sort_by, sort_order=sort_order
    )
    return products


@router.get("/featured", response_model=List[ProductSummary])
def get_featured_products_endpoint(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
) -> Any:
    """
    Get featured products
    """
    products = get_featured_products(db, limit=limit)
    return products


@router.get("/search", response_model=List[ProductSummary])
def search_products_endpoint(
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Search products
    """
    skip = (page - 1) * limit
    products = search_products(
        db, query=q, category=category, skip=skip, limit=limit
    )
    return products


@router.get("/{product_id}", response_model=Product)
def get_product_by_id(
    *,
    db: Session = Depends(get_db),
    product_id: str,
) -> Any:
    """
    Get product by ID
    """
    product = get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.get("/slug/{slug}", response_model=Product)
def get_product_by_slug_endpoint(
    *,
    db: Session = Depends(get_db),
    slug: str,
) -> Any:
    """
    Get product by slug
    """
    product = get_product_by_slug(db, slug=slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.get("/{product_id}/related", response_model=List[ProductSummary])
def get_related_products_endpoint(
    *,
    db: Session = Depends(get_db),
    product_id: str,
    limit: int = Query(6, ge=1, le=20),
) -> Any:
    """
    Get related products
    """
    product = get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    related_products = get_related_products(db, product=product, limit=limit)
    return related_products


@router.post("/", response_model=Product)
def create_product_endpoint(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Create new product (Admin only)
    """
    product = create_product(db, product_in=product_in)
    return product


@router.put("/{product_id}", response_model=Product)
def update_product_endpoint(
    *,
    db: Session = Depends(get_db),
    product_id: str,
    product_in: ProductUpdate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Update product (Admin only)
    """
    product = get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product = update_product(db, db_product=product, product_in=product_in)
    return product


@router.delete("/{product_id}")
def delete_product_endpoint(
    *,
    db: Session = Depends(get_db),
    product_id: str,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Delete product (Admin only)
    """
    product = get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    success = delete_product(db, product_id=product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete product"
        )
    
    return {"message": "Product deleted successfully"}


@router.patch("/{product_id}/stock", response_model=Product)
def update_product_stock_endpoint(
    *,
    db: Session = Depends(get_db),
    product_id: str,
    stock_update: ProductStockUpdate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Update product stock (Admin only)
    """
    product = get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product = update_product_stock(
        db, db_product=product, 
        stock_quantity=stock_update.stock_quantity,
        in_stock=stock_update.in_stock
    )
    return product
