"""
LMS Routes - Learning Management System
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

from middleware.auth import get_current_user
from rpc_clients.lms_client import get_lms_client

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ MODELS ============

class EnrollRequest(BaseModel):
    """Request model for enrolling in course"""
    course_id: int = Field(..., gt=0, description="Course ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "course_id": 1
            }
        }


# ============ ENDPOINTS ============

@router.get("/courses")
async def list_courses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    teacher_id: Optional[int] = Query(None, description="Filter by teacher"),
    status: Optional[str] = Query(None, description="Filter by status"),
    user: dict = Depends(get_current_user)
):
    """List courses"""
    lms_client = get_lms_client()
    
    try:
        result = lms_client.list_courses(
            page=page,
            page_size=page_size,
            teacher_id=teacher_id,
            status=status
        )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error listing courses: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list courses: {str(e)}"
        )


@router.get("/courses/{course_id}")
async def get_course(
    course_id: int,
    user: dict = Depends(get_current_user)
):
    """Get course by ID"""
    lms_client = get_lms_client()
    
    try:
        course = lms_client.get_course(course_id)
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_id} not found"
            )
        
        return {
            "success": True,
            "course": course
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course: {str(e)}"
        )


@router.post("/courses/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: int,
    user: dict = Depends(get_current_user)
):
    """Enroll in course"""
    lms_client = get_lms_client()
    
    try:
        result = lms_client.enroll_in_course(
            course_id=course_id,
            student_id=user.get('id')
        )
        
        return {
            "success": result['success'],
            "message": result['message']
        }
    except Exception as e:
        logger.error(f"Error enrolling in course: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enroll in course: {str(e)}"
        )


@router.get("/courses/{course_id}/modules")
async def list_modules(
    course_id: int,
    user: dict = Depends(get_current_user)
):
    """List modules for course"""
    lms_client = get_lms_client()
    
    try:
        modules = lms_client.list_modules(course_id)
        
        return {
            "success": True,
            "modules": modules,
            "total_count": len(modules)
        }
    except Exception as e:
        logger.error(f"Error listing modules: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list modules: {str(e)}"
        )


@router.get("/modules/{module_id}/materials")
async def list_materials(
    module_id: int,
    user: dict = Depends(get_current_user)
):
    """List materials for module"""
    lms_client = get_lms_client()
    
    try:
        materials = lms_client.list_materials(module_id)
        
        return {
            "success": True,
            "materials": materials,
            "total_count": len(materials)
        }
    except Exception as e:
        logger.error(f"Error listing materials: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list materials: {str(e)}"
        )


@router.get("/students/{student_id}/courses")
async def get_student_courses(
    student_id: int,
    user: dict = Depends(get_current_user)
):
    """Get courses for student"""
    lms_client = get_lms_client()
    
    try:
        result = lms_client.get_student_courses(student_id)
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error getting student courses: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student courses: {str(e)}"
        )


@router.get("/students/{student_id}/courses/{course_id}/progress")
async def get_progress(
    student_id: int,
    course_id: int,
    user: dict = Depends(get_current_user)
):
    """Get student progress for course"""
    lms_client = get_lms_client()
    
    try:
        result = lms_client.get_progress(student_id, course_id)
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error getting progress: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )
