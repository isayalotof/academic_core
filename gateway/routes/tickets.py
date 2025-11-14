"""
Tickets Routes - Ticket System
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status as http_status
from pydantic import BaseModel, Field
from typing import Optional
import logging

from middleware.auth import get_current_user
from rpc_clients.tickets_client import get_tickets_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ MODELS ============

class CreateTicketRequest(BaseModel):
    """Request model for creating a ticket"""
    title: Optional[str] = Field(None, max_length=200, description="Ticket title (auto-generated if not provided)")
    description: Optional[str] = Field('', description="Ticket description")
    category: str = Field(..., min_length=1, max_length=50, description="Ticket category")
    priority: int = Field(3, ge=1, le=5, description="Priority level (1-5)")
    # Для проблем с аудиторией
    type: Optional[str] = Field(None, description="Ticket type (e.g., 'classroom_issue')")
    lesson_id: Optional[int] = Field(None, description="Lesson ID for classroom issues")
    issues: Optional[list] = Field(None, description="List of issues for classroom problems")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Проблема с доступом к системе",
                "description": "Не могу войти в личный кабинет",
                "category": "technical",
                "priority": 3
            }
        }


class AddCommentRequest(BaseModel):
    """Request model for adding a comment"""
    content: str = Field(..., min_length=1, description="Comment content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Проблема решена, спасибо!"
            }
        }


# ============ ENDPOINTS ============

@router.post("/tickets", status_code=http_status.HTTP_201_CREATED)
async def create_ticket(
    request: CreateTicketRequest,
    user: dict = Depends(get_current_user)
):
    """Create a new ticket"""
    tickets_client = get_tickets_client()
    
    try:
        logger.info(f"Creating ticket: request={request.dict()}, user={user}")
        
        # Получаем user_id и user_name из текущего пользователя
        # get_current_user возвращает 'user_id', а не 'id'
        user_id = user.get('user_id') or user.get('id')
        user_name = user.get('full_name') or user.get('username') or ''
        
        logger.info(f"User data: user_id={user_id}, user_name={user_name}, user_keys={list(user.keys()) if user else 'None'}")
        
        if not user_id:
            logger.error(f"User ID not found in user object: {user}")
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in authentication token"
            )
        
        # Автоматически генерировать заголовок для проблем с аудиторией
        if request.type == 'classroom_issue' and not request.title:
            issues_text = ', '.join(request.issues) if request.issues else 'Проблема в аудитории'
            request.title = f"Проблема в аудитории: {issues_text}"
        
        # Формировать описание
        description = request.description or ''
        if request.type == 'classroom_issue' and request.issues:
            issues_list = '\n'.join([f"- {issue}" for issue in request.issues])
            if description:
                description = f"{description}\n\nВыбранные проблемы:\n{issues_list}"
            else:
                description = f"Выбранные проблемы:\n{issues_list}"
        
        # Проверка что есть либо описание, либо проблемы
        if not description.strip() and not (request.type == 'classroom_issue' and request.issues):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Description or issues must be provided"
            )
        
        # Подготовка данных для создания тикета
        ticket_title = request.title or "Тикет"
        ticket_description = description or "Тикет без описания"
        ticket_category = request.category
        # Приоритет должен быть от 1 до 5, по умолчанию 3
        # Pydantic валидирует это, но на всякий случай проверяем
        ticket_priority = request.priority if request.priority and 1 <= request.priority <= 5 else 3
        
        logger.info(f"Creating ticket with: title='{ticket_title}', category='{ticket_category}', priority={ticket_priority}, created_by={user_id}, created_by_name='{user_name}'")
        
        ticket = tickets_client.create_ticket(
            title=ticket_title,
            description=ticket_description,
            category=ticket_category,
            created_by=user_id,
            created_by_name=user_name,
            priority=ticket_priority
        )
        
        logger.info(f"Ticket created successfully: id={ticket.get('id')}")
        
        return {
            "success": True,
            "ticket": ticket,
            "message": "Ticket created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating ticket: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ticket: {str(e)}"
        )


@router.get("/tickets")
async def list_tickets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    created_by: Optional[int] = Query(None, description="Filter by creator"),
    assigned_to: Optional[int] = Query(None, description="Filter by assignee"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    user: dict = Depends(get_current_user)
):
    """List tickets with filters - только для админов и стаффа"""
    # Проверка прав доступа
    user_role = user.get('role')
    if user_role not in ['admin', 'staff']:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only admins and staff can view tickets"
        )
    
    tickets_client = get_tickets_client()
    
    try:
        result = tickets_client.list_tickets(
            page=page,
            page_size=page_size,
            created_by=created_by,
            assigned_to=assigned_to,
            status=status,
            category=category
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error listing tickets: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tickets: {str(e)}"
        )


@router.get("/tickets/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    user: dict = Depends(get_current_user)
):
    """Get ticket by ID - только для админов и стаффа"""
    # Проверка прав доступа
    user_role = user.get('role')
    if user_role not in ['admin', 'staff']:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only admins and staff can view tickets"
        )
    
    tickets_client = get_tickets_client()
    
    try:
        ticket = tickets_client.get_ticket(ticket_id)
        
        if not ticket:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} not found"
            )
        
        return {
            "success": True,
            "ticket": ticket
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ticket: {str(e)}"
        )


@router.post("/tickets/{ticket_id}/comments", status_code=http_status.HTTP_201_CREATED)
async def add_comment(
    ticket_id: int,
    request: AddCommentRequest,
    user: dict = Depends(get_current_user)
):
    """Add comment to ticket"""
    tickets_client = get_tickets_client()
    
    try:
        comment = tickets_client.add_comment(
            ticket_id=ticket_id,
            user_id=user.get('user_id') or user.get('id'),
            content=request.content
        )
        
        return {
            "success": True,
            "comment": comment,
            "message": "Comment added successfully"
        }
    except Exception as e:
        logger.error(f"Error adding comment: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}"
        )


@router.get("/tickets/{ticket_id}/comments")
async def list_comments(
    ticket_id: int,
    user: dict = Depends(get_current_user)
):
    """List comments for ticket - только для админов и стаффа"""
    # Проверка прав доступа
    user_role = user.get('role')
    if user_role not in ['admin', 'staff']:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only admins and staff can view ticket comments"
        )
    
    tickets_client = get_tickets_client()
    
    try:
        comments = tickets_client.list_comments(ticket_id)
        
        return {
            "success": True,
            "comments": comments,
            "total_count": len(comments)
        }
    except Exception as e:
        logger.error(f"Error listing comments: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list comments: {str(e)}"
        )


@router.patch("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: int,
    status: Optional[str] = Query(None, description="New status"),
    assigned_to: Optional[int] = Query(None, description="Assign to user"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Priority (1-5)"),
    user: dict = Depends(get_current_user)
):
    """Update ticket - только для админов и стаффа"""
    # Проверка прав доступа
    user_role = user.get('role')
    if user_role not in ['admin', 'staff']:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only admins and staff can update tickets"
        )
    
    tickets_client = get_tickets_client()
    
    try:
        ticket = tickets_client.update_ticket(
            ticket_id=ticket_id,
            status=status,
            assigned_to=assigned_to,
            priority=priority
        )
        
        return {
            "success": True,
            "ticket": ticket,
            "message": "Ticket updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating ticket: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update ticket: {str(e)}"
        )
