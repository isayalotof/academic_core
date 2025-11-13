"""
Documents Routes - Document Requests
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

from middleware.auth import get_current_user
from rpc_clients.documents_client import get_documents_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ MODELS ============

class RequestDocumentRequest(BaseModel):
    """Request model for requesting a document"""
    document_type: str = Field(..., min_length=1, max_length=100, description="Document type")
    purpose: str = Field(..., min_length=1, description="Purpose of request")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "certificate",
                "purpose": "Для подачи документов в магистратуру",
                "notes": "Срочно, нужно до 15 декабря"
            }
        }


# ============ ENDPOINTS ============

@router.post("/documents/request", status_code=status.HTTP_201_CREATED)
async def request_document(
    request: RequestDocumentRequest,
    user: dict = Depends(get_current_user)
):
    """Request a document"""
    documents_client = get_documents_client()
    
    try:
        doc_request = documents_client.request_document(
            document_type=request.document_type,
            purpose=request.purpose,
            requested_by=user.get('id'),
            notes=request.notes
        )
        
        return {
            "success": True,
            "request": doc_request,
            "message": "Document request created successfully"
        }
    except Exception as e:
        logger.error(f"Error requesting document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request document: {str(e)}"
        )


@router.get("/documents/requests")
async def list_requests(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    user: dict = Depends(get_current_user)
):
    """List document requests"""
    documents_client = get_documents_client()
    
    try:
        result = documents_client.list_requests(
            page=page,
            page_size=page_size,
            requested_by=user.get('id'),
            status=status,
            document_type=document_type
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error listing requests: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list requests: {str(e)}"
        )


@router.get("/documents/requests/{request_id}")
async def get_request(
    request_id: int,
    user: dict = Depends(get_current_user)
):
    """Get document request by ID"""
    documents_client = get_documents_client()
    
    try:
        doc_request = documents_client.get_request(request_id)
        
        if not doc_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Request {request_id} not found"
            )
        
        return {
            "success": True,
            "request": doc_request
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get request: {str(e)}"
        )
