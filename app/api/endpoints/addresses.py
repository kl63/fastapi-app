from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.address import (
    get_user_addresses, get_address, create_address,
    update_address, delete_address, set_default_address
)
from app.models.user import User as DBUser
from app.schemas.address import Address, AddressCreate, AddressUpdate

router = APIRouter()


@router.get("/", response_model=List[Address])
def get_addresses(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get user's addresses
    """
    addresses = get_user_addresses(db, user_id=current_user.id)
    return addresses


@router.post("/", response_model=Address)
def create_address_endpoint(
    *,
    db: Session = Depends(get_db),
    address_in: AddressCreate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Create new address
    """
    address = create_address(db, user_id=current_user.id, address_in=address_in)
    return address


@router.get("/{address_id}", response_model=Address)
def get_address_endpoint(
    *,
    db: Session = Depends(get_db),
    address_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get specific address by ID
    """
    address = get_address(db, address_id=address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # Check if user owns the address
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return address


@router.put("/{address_id}", response_model=Address)
def update_address_endpoint(
    *,
    db: Session = Depends(get_db),
    address_id: str,
    address_in: AddressUpdate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Update address
    """
    address = get_address(db, address_id=address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # Check if user owns the address
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    address = update_address(db, db_address=address, address_in=address_in)
    return address


@router.delete("/{address_id}")
def delete_address_endpoint(
    *,
    db: Session = Depends(get_db),
    address_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Delete address
    """
    address = get_address(db, address_id=address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # Check if user owns the address
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = delete_address(db, address_id=address_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete address"
        )
    
    return {"message": "Address deleted successfully"}


@router.put("/{address_id}/default")
def set_default_address_endpoint(
    *,
    db: Session = Depends(get_db),
    address_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Set address as default
    """
    address = get_address(db, address_id=address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # Check if user owns the address
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = set_default_address(db, user_id=current_user.id, address_id=address_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not set default address"
        )
    
    return {"message": "Default address updated successfully"}
