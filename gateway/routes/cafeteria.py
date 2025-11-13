"""
Cafeteria Routes
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from middleware.auth import get_current_user
from rpc_clients.cafeteria_client import get_cafeteria_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ MODELS ============

class OrderItemRequest(BaseModel):
    """Request model for order item"""
    menu_item_id: int = Field(..., gt=0, description="Menu item ID")
    quantity: int = Field(..., gt=0, le=10, description="Quantity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "menu_item_id": 1,
                "quantity": 2
            }
        }


class CreateOrderRequest(BaseModel):
    """Request model for creating an order"""
    items: List[OrderItemRequest] = Field(..., min_items=1, description="Order items")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"menu_item_id": 1, "quantity": 2},
                    {"menu_item_id": 3, "quantity": 1}
                ]
            }
        }


# ============ ENDPOINTS ============

@router.get("/cafeteria/menu")
async def get_menu(
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    user: dict = Depends(get_current_user)
):
    """Get cafeteria menu"""
    cafeteria_client = get_cafeteria_client()
    
    try:
        items = cafeteria_client.get_menu(date)
        
        return {
            "success": True,
            "items": items,
            "date": date or "today",
            "total_count": len(items)
        }
    except Exception as e:
        logger.error(f"Error getting menu: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get menu: {str(e)}"
        )


@router.post("/cafeteria/orders", status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    user: dict = Depends(get_current_user)
):
    """Create an order"""
    cafeteria_client = get_cafeteria_client()
    
    try:
        items = [{'menu_item_id': item.menu_item_id, 'quantity': item.quantity} for item in request.items]
        
        order = cafeteria_client.create_order(
            user_id=user.get('id'),
            items=items
        )
        
        return {
            "success": True,
            "order": order,
            "message": "Order created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@router.get("/cafeteria/orders")
async def list_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date: Optional[str] = Query(None, description="Filter by date"),
    user: dict = Depends(get_current_user)
):
    """List orders"""
    cafeteria_client = get_cafeteria_client()
    
    try:
        result = cafeteria_client.list_orders(
            page=page,
            page_size=page_size,
            user_id=user.get('id'),
            status=status,
            date=date
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error listing orders: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list orders: {str(e)}"
        )


@router.get("/cafeteria/orders/{order_id}")
async def get_order(
    order_id: int,
    user: dict = Depends(get_current_user)
):
    """Get order by ID"""
    cafeteria_client = get_cafeteria_client()
    
    try:
        order = cafeteria_client.get_order(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found"
            )
        
        return {
            "success": True,
            "order": order
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get order: {str(e)}"
        )
