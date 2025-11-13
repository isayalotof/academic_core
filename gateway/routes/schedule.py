"""
Schedule routes for Gateway
REST API endpoints для расписания
"""

from fastapi import APIRouter, HTTPException, Query, Path, Response
from typing import Optional
import logging

from rpc_clients.schedule_client import get_schedule_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schedule", tags=["Schedule"])


# ============ VIEW ENDPOINTS ============

@router.get("/group/{group_id}")
async def get_group_schedule(
    group_id: int = Path(..., description="Group ID"),
    semester: int = Query(..., ge=1, le=12, description="Semester number (1-12)"),
    academic_year: str = Query(..., description="Academic year (e.g. 2025/2026)"),
    day_of_week: Optional[int] = Query(None, ge=1, le=6, description="Day of week (1-6)"),
    week_type: Optional[str] = Query(None, description="Week type (odd/even/both)")
):
    """
    Get schedule for group
    
    - **group_id**: Group ID
    - **semester**: Semester number (1-12)
    - **academic_year**: Academic year (e.g., "2025/2026")
    - **day_of_week**: Optional filter by day (1=Monday, 6=Saturday)
    - **week_type**: Optional filter by week type
    """
    try:
        client = get_schedule_client()
        lessons = client.get_group_schedule(
            group_id=group_id,
            semester=semester,
            academic_year=academic_year,
            day_of_week=day_of_week,
            week_type=week_type
        )
        
        return {
            'success': True,
            'group_id': group_id,
            'semester': semester,
            'academic_year': academic_year,
            'lessons': lessons,
            'total_count': len(lessons)
        }
        
    except Exception as e:
        logger.error(f"Get group schedule error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teacher/{teacher_id}")
async def get_teacher_schedule(
    teacher_id: int = Path(..., description="Teacher ID"),
    semester: int = Query(..., ge=1, le=12, description="Semester number (1-12)"),
    academic_year: str = Query(..., description="Academic year (e.g. 2025/2026)"),
    day_of_week: Optional[int] = Query(None, ge=1, le=6),
    week_type: Optional[str] = Query(None)
):
    """Get schedule for teacher"""
    try:
        client = get_schedule_client()
        lessons = client.get_teacher_schedule(
            teacher_id=teacher_id,
            semester=semester,
            academic_year=academic_year,
            day_of_week=day_of_week,
            week_type=week_type
        )
        
        return {
            'success': True,
            'teacher_id': teacher_id,
            'semester': semester,
            'academic_year': academic_year,
            'lessons': lessons,
            'total_count': len(lessons)
        }
        
    except Exception as e:
        logger.error(f"Get teacher schedule error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classroom/{classroom_id}")
async def get_classroom_schedule(
    classroom_id: int = Path(..., description="Classroom ID"),
    semester: int = Query(..., ge=1, le=12, description="Semester number (1-12)"),
    academic_year: str = Query(..., description="Academic year (e.g. 2025/2026)"),
    day_of_week: Optional[int] = Query(None, ge=1, le=6),
    week_type: Optional[str] = Query(None)
):
    """Get schedule for classroom"""
    try:
        client = get_schedule_client()
        lessons = client.get_classroom_schedule(
            classroom_id=classroom_id,
            semester=semester,
            academic_year=academic_year,
            day_of_week=day_of_week,
            week_type=week_type
        )
        
        return {
            'success': True,
            'classroom_id': classroom_id,
            'semester': semester,
            'academic_year': academic_year,
            'lessons': lessons,
            'total_count': len(lessons)
        }
        
    except Exception as e:
        logger.error(f"Get classroom schedule error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ EXPORT ENDPOINTS ============

@router.get("/export/group/{group_id}/excel")
async def export_group_to_excel(
    group_id: int = Path(...),
    semester: int = Query(..., ge=1, le=12, description="Semester number (1-12)"),
    academic_year: str = Query(..., description="Academic year (e.g. 2025/2026)")
):
    """Export group schedule to Excel"""
    try:
        client = get_schedule_client()
        file_bytes, filename, content_type = client.export_to_excel(
            entity_type='group',
            entity_id=group_id,
            semester=semester,
            academic_year=academic_year
        )
        
        return Response(
            content=file_bytes,
            media_type=content_type,
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        logger.error(f"Export to Excel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/group/{group_id}/pdf")
async def export_group_to_pdf(
    group_id: int = Path(...),
    semester: int = Query(..., ge=1, le=12, description="Semester number (1-12)"),
    academic_year: str = Query(..., description="Academic year (e.g. 2025/2026)")
):
    """Export group schedule to PDF"""
    try:
        client = get_schedule_client()
        file_bytes, filename, content_type = client.export_to_pdf(
            entity_type='group',
            entity_id=group_id,
            semester=semester,
            academic_year=academic_year
        )
        
        return Response(
            content=file_bytes,
            media_type=content_type,
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        logger.error(f"Export to PDF error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/group/{group_id}/ical")
async def export_group_to_ical(
    group_id: int = Path(...),
    semester: int = Query(..., ge=1, le=12, description="Semester number (1-12)"),
    academic_year: str = Query(..., description="Academic year (e.g. 2025/2026)")
):
    """Export group schedule to iCal format (for Google Calendar, Apple Calendar, etc.)"""
    try:
        client = get_schedule_client()
        file_bytes, filename, content_type = client.export_to_ical(
            entity_type='group',
            entity_id=group_id,
            semester=semester,
            academic_year=academic_year
        )
        
        return Response(
            content=file_bytes,
            media_type=content_type,
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        logger.error(f"Export to iCal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/teacher/{teacher_id}/excel")
async def export_teacher_to_excel(
    teacher_id: int = Path(...),
    semester: int = Query(..., ge=1, le=12, description="Semester number (1-12)"),
    academic_year: str = Query(..., description="Academic year (e.g. 2025/2026)")
):
    """Export teacher schedule to Excel"""
    try:
        client = get_schedule_client()
        file_bytes, filename, content_type = client.export_to_excel(
            entity_type='teacher',
            entity_id=teacher_id,
            semester=semester,
            academic_year=academic_year
        )
        
        return Response(
            content=file_bytes,
            media_type=content_type,
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        logger.error(f"Export to Excel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ SEARCH ============

@router.get("/search")
async def search_schedule(
    query: str = Query(..., min_length=2, description="Search query"),
    semester: int = Query(..., ge=1, le=12, description="Semester number (1-12)"),
    academic_year: str = Query(..., description="Academic year (e.g. 2025/2026)"),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Search schedule by text
    
    Search across discipline names, teacher names, and group names.
    """
    try:
        client = get_schedule_client()
        results = client.search_schedule(
            query=query,
            semester=semester,
            academic_year=academic_year,
            limit=limit
        )
        
        return {
            'success': True,
            'query': query,
            'results': results,
            'total_count': len(results)
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

