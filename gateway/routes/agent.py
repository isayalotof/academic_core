"""
Agent REST Endpoints
HTTP REST API endpoints для агента генерации расписания
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import logging
import grpc

from rpc_clients.agent_client import agent_client
from middleware.auth import get_current_user, require_staff

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])


# ============ REQUEST/RESPONSE MODELS ============

class GenerateScheduleRequest(BaseModel):
    """Запрос на генерацию расписания"""
    semester: int = Field(..., ge=1, le=12, description="Номер семестра обучения (1-12)")
    max_iterations: Optional[int] = Field(100, ge=1, le=500, description="Максимум итераций")
    skip_stage1: bool = Field(False, description="Пропустить Stage 1 (использовать существующее)")
    skip_stage2: bool = Field(False, description="Пропустить Stage 2 (без аудиторий)")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "semester": 3,
                    "max_iterations": 100,
                    "skip_stage1": False,
                    "skip_stage2": False
                },
                {
                    "semester": 1,
                    "max_iterations": 200,
                    "skip_stage1": False,
                    "skip_stage2": False
                },
                {
                    "semester": 5,
                    "max_iterations": 50,
                    "skip_stage1": True,
                    "skip_stage2": False
                }
            ]
        }


# ============ ENDPOINTS ============

@router.post("/generate", dependencies=[Depends(require_staff)])
async def generate_schedule(
    data: GenerateScheduleRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Запустить генерацию расписания
    
    Требуется роль: staff или admin
    """
    try:
        request_data = data.dict()
        request_data['created_by'] = current_user['user_id']
        
        result = agent_client.generate_schedule(request_data)
        
        if not result.get('success', False):
            error_detail = result.get('error') or result.get('message') or 'Generation failed'
            logger.error(f"Generation failed: {error_detail}")
            raise HTTPException(status_code=500, detail=error_detail)
        
        return {
            "success": True,
            "job_id": result['job_id'],
            "message": result['message']
        }
        
    except grpc.RpcError as e:
        error_detail = e.details() if hasattr(e, 'details') else str(e)
        logger.error(f"RPC error in generate_schedule: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent service error: {error_detail}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_schedule: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}")
async def get_generation_status(job_id: str):
    """
    Получить статус генерации
    
    Доступно всем аутентифицированным пользователям
    """
    try:
        result = agent_client.get_generation_status(job_id)
        
        if not result.get('found'):
            raise HTTPException(status_code=404, detail="Generation not found")
        
        return {
            "success": True,
            "generation": {
                "job_id": result['job_id'],
                "status": result['status'],
                "stage": result['stage'],
                "current_iteration": result['current_iteration'],
                "max_iterations": result['max_iterations'],
                "current_score": result['current_score'],
                "best_score": result['best_score'],
                "progress_percentage": result['progress_percentage'],
                "last_reasoning": result['last_reasoning']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting generation status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule")
async def get_schedule(
    generation_id: Optional[int] = None,
    only_active: bool = True
):
    """
    Получить расписание
    
    Доступно всем аутентифицированным пользователям
    """
    try:
        schedules = agent_client.get_schedule(
            generation_id=generation_id,
            only_active=only_active
        )
        
        return {
            "success": True,
            "total_count": len(schedules),
            "schedules": schedules
        }
        
    except Exception as e:
        logger.error(f"Error getting schedule: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

