from typing import Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel
from pydantic.generics import GenericModel

# Generic type for pagination
T = TypeVar('T')


class PaginationParams:
    """
    Pagination query parameters
    """
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of items to skip"),
        limit: int = Query(100, ge=1, le=100, description="Max number of items to return"),
    ):
        self.skip = skip
        self.limit = limit


class Page(GenericModel, Generic[T]):
    """
    Pagination response with items and metadata
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams):
        """
        Create paginated response
        """
        pages = (total + params.limit - 1) // params.limit if params.limit > 0 else 0
        page = (params.skip // params.limit) + 1 if params.limit > 0 else 1
        
        return cls(
            items=items,
            total=total,
            page=page,
            size=len(items),
            pages=pages,
        )
