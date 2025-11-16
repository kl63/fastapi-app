from typing import Any, Dict, Optional, Union, List
import uuid
from sqlalchemy.orm import Session

from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate


def get_address(db: Session, address_id: str) -> Optional[Address]:
    """Get address by ID"""
    return db.query(Address).filter(Address.id == address_id).first()


def get_user_addresses(db: Session, user_id: str) -> List[Address]:
    """Get all addresses for a user"""
    return db.query(Address).filter(Address.user_id == user_id).order_by(
        Address.is_default.desc(), Address.created_at.desc()
    ).all()


def get_default_address(db: Session, user_id: str, address_type: str = None) -> Optional[Address]:
    """Get user's default address, optionally filtered by type"""
    query = db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == True
    )
    
    if address_type:
        query = query.filter(Address.type == address_type)
    
    return query.first()


def create_address(db: Session, user_id: str, address_in: AddressCreate) -> Address:
    """Create new address"""
    address_id = str(uuid.uuid4())
    
    # If this is the first address or marked as default, set as default
    existing_addresses = get_user_addresses(db, user_id)
    is_default = address_in.is_default or len(existing_addresses) == 0
    
    # If setting as default, unset other default addresses of same type
    if is_default:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.type == address_in.type,
            Address.is_default == True
        ).update({"is_default": False})
    
    db_address = Address(
        id=address_id,
        user_id=user_id,
        type=address_in.type,
        first_name=address_in.first_name,
        last_name=address_in.last_name,
        street=address_in.street,
        city=address_in.city,
        state=address_in.state,
        zip_code=address_in.zip_code,
        country=address_in.country,
        phone=address_in.phone,
        is_default=is_default,
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def update_address(
    db: Session, 
    db_address: Address, 
    address_in: Union[AddressUpdate, Dict[str, Any]]
) -> Address:
    """Update address"""
    if isinstance(address_in, dict):
        update_data = address_in
    else:
        update_data = address_in.dict(exclude_unset=True)
    
    # If setting as default, unset other default addresses of same type
    if update_data.get("is_default"):
        db.query(Address).filter(
            Address.user_id == db_address.user_id,
            Address.type == db_address.type,
            Address.id != db_address.id,
            Address.is_default == True
        ).update({"is_default": False})
    
    # Update address attributes
    for field in update_data:
        if hasattr(db_address, field):
            setattr(db_address, field, update_data[field])
            
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def set_default_address(db: Session, user_id: str, address_id: str) -> bool:
    """Set address as default"""
    try:
        address = get_address(db, address_id)
        if not address or address.user_id != user_id:
            return False
        
        # Unset other default addresses of same type
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.type == address.type,
            Address.id != address_id,
            Address.is_default == True
        ).update({"is_default": False})
        
        # Set this address as default
        address.is_default = True
        db.add(address)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def delete_address(db: Session, address_id: str) -> bool:
    """Delete address"""
    try:
        address = get_address(db, address_id=address_id)
        if not address:
            return False
        
        db.delete(address)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
