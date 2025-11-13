"""
Auth REST Endpoints
HTTP REST API endpoints для аутентификации
"""

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging
import grpc

from rpc_clients.auth_client import auth_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# ============ REQUEST/RESPONSE MODELS ============

class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=200)
    phone: Optional[str] = None
    primary_role: str = Field(..., description="student, teacher, staff")
    teacher_id: Optional[int] = None
    student_group_id: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "username": "ivanov_teacher",
                    "email": "ivanov@university.ru",
                    "password": "SecurePass123!",
                    "full_name": "Иванов Иван Иванович",
                    "phone": "+7 (999) 123-45-67",
                    "primary_role": "teacher",
                    "teacher_id": 1
                },
                {
                    "username": "petrov_student",
                    "email": "petrov@student.university.ru",
                    "password": "StudentPass456!",
                    "full_name": "Петров Пётр Петрович",
                    "phone": "+7 (999) 765-43-21",
                    "primary_role": "student",
                    "student_group_id": 1
                },
                {
                    "username": "admin_staff",
                    "email": "admin@university.ru",
                    "password": "AdminPass789!",
                    "full_name": "Администратор Системный",
                    "primary_role": "staff"
                }
            ]
        }


class LoginRequest(BaseModel):
    """Запрос на вход"""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "username": "ivanov_teacher",
                    "password": "SecurePass123!"
                },
                {
                    "username": "petrov_student",
                    "password": "StudentPass456!"
                },
                {
                    "username": "admin_staff",
                    "password": "AdminPass789!"
                }
            ]
        }


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
                }
            ]
        }


# ============ ENDPOINTS ============

@router.post("/register", status_code=201)
async def register(data: RegisterRequest, request: Request):
    """
    Регистрация нового пользователя
    
    Доступно всем
    """
    try:
        response = auth_client.register(data.dict())
        
        if not response['success']:
            raise HTTPException(status_code=400, detail=response['message'])
        
        return {
            "success": True,
            "user": {
                "id": response['user']['id'],
                "username": response['user']['username'],
                "email": response['user']['email'],
                "full_name": response['user']['full_name'],
                "role": response['user']['primary_role'],
                "roles": response['user']['roles']
            },
            "tokens": response['tokens'],
            "message": response['message']
        }
        
    except grpc.RpcError as e:
        logger.error(f"RPC error in register: {e}")
        # Обработка специфичных gRPC ошибок
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            detail = e.details() or "User already exists"
            raise HTTPException(status_code=409, detail=detail)
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            detail = e.details() or "Invalid request data"
            raise HTTPException(status_code=400, detail=detail)
        elif e.code() == grpc.StatusCode.UNAUTHENTICATED:
            detail = e.details() or "Authentication failed"
            raise HTTPException(status_code=401, detail=detail)
        else:
            raise HTTPException(
                status_code=500,
                detail="Authentication service error"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in register: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(data: LoginRequest, request: Request):
    """
    Вход пользователя
    
    Доступно всем
    """
    try:
        # Get client IP and User-Agent
        ip_address = request.client.host if request.client else ''
        user_agent = request.headers.get('User-Agent', '')
        
        response = auth_client.login(
            data.username,
            data.password,
            ip_address,
            user_agent
        )
        
        if not response['success']:
            raise HTTPException(status_code=401, detail=response['message'])
        
        return {
            "success": True,
            "user": {
                "id": response['user']['id'],
                "username": response['user']['username'],
                "email": response['user']['email'],
                "full_name": response['user']['full_name'],
                "role": response['user']['primary_role'],
                "roles": response['user']['roles']
            },
            "tokens": response['tokens'],
            "message": response['message']
        }
        
    except grpc.RpcError as e:
        logger.error(f"RPC error in login: {e}")
        # Обработка специфичных gRPC ошибок
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            detail = e.details() or "Invalid credentials"
            raise HTTPException(status_code=401, detail=detail)
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            detail = e.details() or "Invalid request data"
            raise HTTPException(status_code=400, detail=detail)
        else:
            raise HTTPException(
                status_code=500,
                detail="Authentication service error"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_token(data: RefreshTokenRequest, request: Request):
    """
    Обновить access token используя refresh token
    
    Доступно всем с валидным refresh token
    """
    try:
        ip_address = request.client.host if request.client else ''
        user_agent = request.headers.get('User-Agent', '')
        
        response = auth_client.refresh_token(
            data.refresh_token,
            ip_address,
            user_agent
        )
        
        if not response['success']:
            raise HTTPException(status_code=401, detail=response['message'])
        
        return {
            "success": True,
            "tokens": response['tokens'],
            "message": response['message']
        }
        
    except grpc.RpcError as e:
        logger.error(f"RPC error in refresh: {e}")
        # Обработка специфичных gRPC ошибок
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            detail = e.details() or "Invalid refresh token"
            raise HTTPException(status_code=401, detail=detail)
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            detail = e.details() or "Invalid request data"
            raise HTTPException(status_code=400, detail=detail)
        else:
            raise HTTPException(
                status_code=500,
                detail="Authentication service error"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(authorization: str = Header(...)):
    """
    Выход пользователя (отозвать refresh token)
    
    Требуется валидный access token
    """
    try:
        # Извлечь токен
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        
        # Валидировать токен и получить user_id
        validate_response = auth_client.validate_token(token)
        if not validate_response['valid']:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Logout
        user_id = validate_response['user_id']
        response = auth_client.logout(user_id)
        
        return {
            "success": True,
            "message": response['message']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in logout: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_current_user(authorization: str = Header(...)):
    """
    Получить информацию о текущем пользователе
    
    Требуется валидный access token
    """
    try:
        # Извлечь токен
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        
        # Получить пользователя
        user = auth_client.get_current_user(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "success": True,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "full_name": user['full_name'],
                "phone": user['phone'],
                "role": user['primary_role'],
                "roles": user['roles'],
                "is_active": user['is_active'],
                "is_verified": user['is_verified']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_token(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Валидировать access token
    
    Доступно всем (для проверки токена)
    
    Args:
        authorization: Bearer token в заголовке Authorization
    """
    try:
        # Попробовать получить из параметра или из заголовков напрямую
        auth_header = authorization
        if not auth_header:
            # Попробовать получить напрямую из заголовков
            auth_header = (
                request.headers.get("Authorization") or
                request.headers.get("authorization")
            )
        
        # Логирование для отладки (только в dev режиме)
        logger.debug(
            f"Validate token: auth_header={auth_header[:20] if auth_header else None}..."
        )
        
        # Проверить наличие заголовка
        if not auth_header:
            return {
                "valid": False,
                "message": "Authorization header is required"
            }
        
        # Извлечь токен (может быть с префиксом "Bearer " или без него)
        token = auth_header.strip()
        
        # Если есть префикс "Bearer ", убрать его
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "", 1).strip()
        elif token.startswith("bearer "):
            token = token.replace("bearer ", "", 1).strip()
        
        if not token:
            return {
                "valid": False,
                "message": "Token is empty"
            }
        
        # Валидация
        result = auth_client.validate_token(token)
        
        return {
            "valid": result['valid'],
            "user_id": result.get('user_id'),
            "username": result.get('username'),
            "role": result.get('primary_role'),
            "roles": result.get('roles', []),
            "message": result.get('message', '')
        }
        
    except Exception as e:
        logger.error(f"Error validating token: {e}", exc_info=True)
        return {
            "valid": False,
            "message": str(e)
        }

