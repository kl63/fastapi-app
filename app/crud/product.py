from typing import Any, Dict, Optional, Union, List
import uuid
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: str) -> Optional[Product]:
    """Get product by ID"""
    return db.query(Product).options(joinedload(Product.category)).filter(Product.id == product_id).first()


def get_product_by_slug(db: Session, slug: str) -> Optional[Product]:
    """Get product by slug"""
    return db.query(Product).options(joinedload(Product.category)).filter(Product.slug == slug).first()


def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: str = "name",
    sort_order: str = "asc"
) -> List[Product]:
    """Get multiple products with filtering, pagination and sorting"""
    query = db.query(Product).options(joinedload(Product.category)).filter(Product.is_active == True)
    
    if filters:
        if filters.get("category"):
            query = query.filter(Product.category_id == filters["category"])
        
        if filters.get("search"):
            search_term = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.tags.contains([filters["search"]])
                )
            )
        
        if filters.get("min_price") is not None:
            query = query.filter(Product.price >= filters["min_price"])
        
        if filters.get("max_price") is not None:
            query = query.filter(Product.price <= filters["max_price"])
        
        if filters.get("in_stock") is not None:
            query = query.filter(Product.in_stock == filters["in_stock"])
        
        if filters.get("is_organic") is not None:
            query = query.filter(Product.is_organic == filters["is_organic"])
        
        if filters.get("is_on_sale") is not None:
            query = query.filter(Product.is_on_sale == filters["is_on_sale"])
    
    # Apply sorting
    if sort_by == "price":
        if sort_order == "desc":
            query = query.order_by(Product.price.desc())
        else:
            query = query.order_by(Product.price.asc())
    elif sort_by == "rating":
        query = query.order_by(Product.rating_average.desc())
    elif sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    else:  # name
        if sort_order == "desc":
            query = query.order_by(Product.name.desc())
        else:
            query = query.order_by(Product.name.asc())
    
    return query.offset(skip).limit(limit).all()


def get_featured_products(db: Session, limit: int = 10) -> List[Product]:
    """Get featured products"""
    return db.query(Product).options(joinedload(Product.category)).filter(
        and_(Product.is_featured == True, Product.is_active == True)
    ).limit(limit).all()


def get_related_products(db: Session, product: Product, limit: int = 6) -> List[Product]:
    """Get related products based on category"""
    return db.query(Product).options(joinedload(Product.category)).filter(
        and_(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.is_active == True
        )
    ).limit(limit).all()


def search_products(
    db: Session, 
    query: str, 
    category: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[Product]:
    """Search products by query"""
    search_term = f"%{query}%"
    db_query = db.query(Product).options(joinedload(Product.category)).filter(
        and_(
            Product.is_active == True,
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.tags.contains([query])
            )
        )
    )
    
    if category:
        db_query = db_query.filter(Product.category_id == category)
    
    return db_query.offset(skip).limit(limit).all()


def create_product(db: Session, product_in: ProductCreate) -> Product:
    """Create new product"""
    product_id = str(uuid.uuid4())
    db_product = Product(
        id=product_id,
        name=product_in.name,
        slug=product_in.slug,
        description=product_in.description,
        short_description=product_in.short_description,
        price=product_in.price,
        original_price=product_in.original_price,
        cost_price=None,  # Add missing cost_price field
        sku=product_in.sku,
        category_id=product_in.category_id,
        brand=product_in.brand,
        unit=product_in.unit,
        weight=product_in.weight,
        dimensions=product_in.dimensions,
        images=product_in.images,
        thumbnail=product_in.thumbnail,
        is_organic=product_in.is_organic,
        is_featured=product_in.is_featured,
        is_on_sale=product_in.is_on_sale,
        is_active=product_in.is_active,
        in_stock=product_in.in_stock,
        stock_quantity=product_in.stock_quantity,
        low_stock_threshold=product_in.low_stock_threshold,
        nutrition_facts=product_in.nutrition_facts,
        ingredients=product_in.ingredients,
        allergens=product_in.allergens,
        tags=product_in.tags,
        meta_title=product_in.meta_title,
        meta_description=product_in.meta_description,
        # Add missing statistics fields with defaults
        view_count=0,
        purchase_count=0,
        rating_average=0.0,
        rating_count=0,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(
    db: Session, 
    db_product: Product, 
    product_in: Union[ProductUpdate, Dict[str, Any]]
) -> Product:
    """Update product"""
    if isinstance(product_in, dict):
        update_data = product_in
    else:
        update_data = product_in.dict(exclude_unset=True)
    
    # Update product attributes
    for field in update_data:
        if hasattr(db_product, field):
            setattr(db_product, field, update_data[field])
            
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product_stock(
    db: Session, 
    db_product: Product, 
    stock_quantity: int,
    in_stock: bool
) -> Product:
    """Update product stock"""
    db_product.stock_quantity = stock_quantity
    db_product.in_stock = in_stock
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: str) -> bool:
    """Delete product"""
    try:
        product = get_product(db, product_id=product_id)
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
