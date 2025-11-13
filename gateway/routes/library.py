"""
Library Routes
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

from middleware.auth import get_current_user
from rpc_clients.library_client import get_library_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ MODELS ============

class ReserveBookRequest(BaseModel):
    """Request model for reserving a book"""
    days: int = Field(14, ge=1, le=90, description="Loan period in days")
    
    class Config:
        json_schema_extra = {
            "example": {
                "days": 14
            }
        }


# ============ ENDPOINTS ============

@router.get("/books")
async def list_books(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    author: Optional[str] = Query(None, description="Filter by author"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and author"),
    user: dict = Depends(get_current_user)
):
    """List books"""
    library_client = get_library_client()
    
    try:
        result = library_client.list_books(
            page=page,
            page_size=page_size,
            author=author,
            category=category,
            search=search
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error listing books: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list books: {str(e)}"
        )


@router.get("/books/{book_id}")
async def get_book(
    book_id: int,
    user: dict = Depends(get_current_user)
):
    """Get book by ID"""
    library_client = get_library_client()
    
    try:
        book = library_client.get_book(book_id)
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book {book_id} not found"
            )
        
        return {
            "success": True,
            "book": book
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting book: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get book: {str(e)}"
        )


@router.post("/books/{book_id}/reserve", status_code=status.HTTP_201_CREATED)
async def reserve_book(
    book_id: int,
    request: ReserveBookRequest,
    user: dict = Depends(get_current_user)
):
    """Reserve a book"""
    library_client = get_library_client()
    
    try:
        result = library_client.reserve_book(
            book_id=book_id,
            user_id=user.get('id'),
            days=request.days
        )
        
        return {
            "success": result['success'],
            "message": result['message'],
            "reservation_id": result.get('reservation_id', 0)
        }
    except Exception as e:
        logger.error(f"Error reserving book: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reserve book: {str(e)}"
        )


@router.get("/reservations")
async def list_reservations(
    status: Optional[str] = Query(None, description="Filter by status"),
    user: dict = Depends(get_current_user)
):
    """List reservations"""
    library_client = get_library_client()
    
    try:
        reservations = library_client.get_reservations(
            user_id=user.get('id'),
            status=status
        )
        
        return {
            "success": True,
            "reservations": reservations,
            "total_count": len(reservations)
        }
    except Exception as e:
        logger.error(f"Error listing reservations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reservations: {str(e)}"
        )


@router.post("/reservations/{reservation_id}/return", status_code=status.HTTP_200_OK)
async def return_book(
    reservation_id: int,
    user: dict = Depends(get_current_user)
):
    """Return a book"""
    library_client = get_library_client()
    
    try:
        result = library_client.return_book(reservation_id)
        
        return {
            "success": result['success'],
            "message": result['message']
        }
    except Exception as e:
        logger.error(f"Error returning book: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to return book: {str(e)}"
        )
