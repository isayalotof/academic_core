"""
Events Routes - Campus Events
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

from middleware.auth import get_current_user
from rpc_clients.events_client import get_events_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ MODELS ============

class CreateEventRequest(BaseModel):
    """Request model for creating an event"""
    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: str = Field(..., min_length=1, description="Event description")
    type: str = Field(..., min_length=1, max_length=50, description="Event type")
    location: str = Field(..., min_length=1, max_length=200, description="Event location")
    start_time: str = Field(..., description="Start time (ISO format)")
    end_time: str = Field(..., description="End time (ISO format)")
    max_participants: Optional[int] = Field(None, ge=1, description="Maximum participants")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Конференция по ИИ",
                "description": "Ежегодная конференция по искусственному интеллекту",
                "type": "conference",
                "location": "Аудитория 101",
                "start_time": "2025-12-01T10:00:00Z",
                "end_time": "2025-12-01T18:00:00Z",
                "max_participants": 100
            }
        }


# ============ ENDPOINTS ============

@router.get("/events")
async def list_events(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    type: Optional[str] = Query(None, description="Filter by type"),
    start_date: Optional[str] = Query(None, description="Filter by start date"),
    end_date: Optional[str] = Query(None, description="Filter by end date"),
    user: dict = Depends(get_current_user)
):
    """List campus events"""
    events_client = get_events_client()
    
    try:
        result = events_client.list_events(
            page=page,
            page_size=page_size,
            type=type,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error listing events: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list events: {str(e)}"
        )


@router.get("/events/{event_id}")
async def get_event(
    event_id: int,
    user: dict = Depends(get_current_user)
):
    """Get event by ID"""
    events_client = get_events_client()
    
    try:
        event = events_client.get_event(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )
        
        return {
            "success": True,
            "event": event
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event: {str(e)}"
        )


@router.post("/events/{event_id}/register", status_code=status.HTTP_201_CREATED)
async def register_for_event(
    event_id: int,
    user: dict = Depends(get_current_user)
):
    """Register for event"""
    events_client = get_events_client()
    
    try:
        result = events_client.register_for_event(
            event_id=event_id,
            user_id=user.get('id')
        )
        
        return {
            "success": result['success'],
            "message": result['message']
        }
    except Exception as e:
        logger.error(f"Error registering for event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register for event: {str(e)}"
        )


@router.get("/events/{event_id}/registrations")
async def get_registrations(
    event_id: int,
    user: dict = Depends(get_current_user)
):
    """Get registrations for event"""
    events_client = get_events_client()
    
    try:
        registrations = events_client.get_registrations(event_id)
        
        return {
            "success": True,
            "registrations": registrations,
            "total_count": len(registrations)
        }
    except Exception as e:
        logger.error(f"Error getting registrations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get registrations: {str(e)}"
        )
