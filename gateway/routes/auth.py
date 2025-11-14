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
from rpc_clients.core_client import get_core_client

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
    
    Если указан student_group_id, автоматически создается запись студента,
    что увеличит размер группы через триггер БД.
    """
    try:
        # При регистрации НЕ передаем teacher_id в ms-auth напрямую
        # Сначала создаем пользователя, затем связываем преподавателя в ms-core
        # и только после успешного связывания обновляем teacher_id в ms-auth
        register_data = data.dict()
        teacher_id_to_link = register_data.pop('teacher_id', None)  # Временно убираем из данных регистрации
        student_group_id_to_link = register_data.pop('student_group_id', None)  # Временно убираем
        
        response = auth_client.register(register_data)
        
        if not response['success']:
            raise HTTPException(status_code=400, detail=response['message'])
        
        user_id = response['user']['id']
        
        # Если преподаватель указал существующий teacher_id, связать его с пользователем
        if data.primary_role == 'teacher' and teacher_id_to_link:
            try:
                core_client = get_core_client()
                
                logger.info(f"Linking teacher {teacher_id_to_link} to registered user {user_id}")
                
                try:
                    # Проверить, что преподаватель существует
                    teacher = core_client.get_teacher(teacher_id_to_link)
                    if not teacher:
                        logger.warning(f"⚠️ Teacher {teacher_id_to_link} not found, skipping link")
                    elif teacher.get('user_id') and teacher['user_id'] != 0:
                        logger.warning(f"⚠️ Teacher {teacher_id_to_link} is already linked to user {teacher['user_id']}, skipping link. Registration will complete without teacher link.")
                    else:
                        # Связать существующего преподавателя с пользователем
                        link_result = core_client.link_teacher_to_user(teacher_id_to_link, user_id)
                        if not link_result.get('success'):
                            logger.warning(f"⚠️ Failed to link teacher {teacher_id_to_link} to user {user_id}: {link_result.get('message')}")
                        else:
                            logger.info(f"✅ Successfully linked teacher {teacher_id_to_link} to user {user_id}")
                            
                            # Обновляем данные преподавателя из данных регистрации
                            try:
                                update_data = {}
                                if data.email:
                                    update_data['email'] = data.email
                                if data.phone:
                                    update_data['phone'] = data.phone
                                if data.full_name:
                                    update_data['full_name'] = data.full_name
                                
                                if update_data:
                                    logger.info(f"📝 Updating teacher {teacher_id_to_link} data from registration: {list(update_data.keys())}")
                                    update_data['updated_by'] = user_id
                                    updated_teacher = core_client.update_teacher(teacher_id_to_link, update_data)
                                    logger.info(f"✅ Teacher {teacher_id_to_link} data updated successfully")
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to update teacher data, but link is successful: {e}")
                            
                            # Проверяем, что связь установлена
                            try:
                                teacher_check = core_client.get_teacher(teacher_id_to_link)
                                if teacher_check and teacher_check.get('user_id') == user_id:
                                    logger.info(f"✅ Verified: teacher {teacher_id_to_link} is linked to user {user_id}")
                                    # teacher_id будет обновляться автоматически в /api/auth/me через проверку связи в ms-core
                                else:
                                    logger.warning(f"⚠️ Warning: teacher {teacher_id_to_link} user_id mismatch. Expected: {user_id}, Got: {teacher_check.get('user_id') if teacher_check else None}")
                            except Exception as e:
                                logger.error(f"❌ Error verifying teacher link: {e}")
                        
                except grpc.RpcError as e:
                    logger.error(f"❌ gRPC error linking teacher: {e.code()}: {e.details()}")
                    # Не прерываем регистрацию, пользователь уже создан
                except Exception as e:
                    logger.error(f"❌ Unexpected error linking teacher: {type(e).__name__}: {e}", exc_info=True)
                    # Не прерываем регистрацию, пользователь уже создан
                
            except Exception as e:
                logger.error(f"❌ Error linking teacher during registration: {e}", exc_info=True)
                # Не прерываем регистрацию, пользователь уже создан
        
        # Если студент указал группу, создать запись студента
        if data.primary_role == 'student' and student_group_id_to_link:
            try:
                core_client = get_core_client()
                
                logger.info(f"Creating student for registered user {user_id} with group_id={student_group_id_to_link}")
                
                # Генерируем уникальный номер студенческого билета
                import time
                import random
                # Используем timestamp + user_id + случайное число для уникальности
                student_number = f"{int(time.time())}{user_id:04d}{random.randint(10, 99)}"
                
                # Разбиваем ФИО на части для правильного заполнения
                # Обычно формат: "Фамилия Имя Отчество"
                name_parts = data.full_name.strip().split()
                if len(name_parts) >= 3:
                    last_name = name_parts[0]  # Фамилия
                    first_name = name_parts[1]  # Имя
                    middle_name = name_parts[2]  # Отчество
                elif len(name_parts) == 2:
                    last_name = name_parts[0]
                    first_name = name_parts[1]
                    middle_name = None
                else:
                    first_name = data.full_name
                    last_name = ''
                    middle_name = None
                
                # Создать студента
                student_data = {
                    'full_name': data.full_name,
                    'first_name': first_name,
                    'last_name': last_name,
                    'middle_name': middle_name,
                    'student_number': student_number,
                    'group_id': student_group_id_to_link,
                    'email': data.email,
                    'phone': data.phone if data.phone else None,
                }
                
                logger.info(f"Student data to create: {student_data}")
                
                try:
                    student_result = core_client.create_student(student_data)
                    student_id = student_result.get('id')
                    
                    if not student_id:
                        logger.error(f"❌ Student creation failed: no ID returned. Result: {student_result}")
                    else:
                        logger.info(f"✅ Student created successfully with ID: {student_id}")
                        
                        # Связать студента с пользователем
                        link_result = core_client.link_student_to_user(student_id, user_id)
                        if not link_result.get('success'):
                            logger.warning(f"⚠️ Failed to link student {student_id} to user {user_id}: {link_result.get('message')}")
                        else:
                            logger.info(f"✅ Successfully linked student {student_id} to user {user_id}. Group size will be updated automatically via DB trigger.")
                            
                except grpc.RpcError as e:
                    logger.error(f"❌ gRPC error creating student: {e.code()}: {e.details()}")
                    raise  # Пробрасываем, чтобы обработать в основном except
                except Exception as e:
                    logger.error(f"❌ Unexpected error creating student: {type(e).__name__}: {e}", exc_info=True)
                    raise
                
            except Exception as e:
                logger.error(f"❌ Error creating student during registration: {e}", exc_info=True)
                # Не прерываем регистрацию, пользователь уже создан
                # Размер группы можно будет обновить позже вручную или при создании студента
        
        return {
            "success": True,
            "user": {
                "id": response['user']['id'],
                "username": response['user']['username'],
                "email": response['user']['email'],
                "full_name": response['user']['full_name'],
                "role": response['user']['primary_role'],
                "roles": response['user']['roles'],
                "teacher_id": response['user'].get('teacher_id') if response['user'].get('teacher_id') else None,
                "student_group_id": response['user'].get('student_group_id') if response['user'].get('student_group_id') else None
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
                "roles": response['user']['roles'],
                "teacher_id": response['user'].get('teacher_id') if response['user'].get('teacher_id') else None,
                "student_group_id": response['user'].get('student_group_id') if response['user'].get('student_group_id') else None
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
        
        user_id = user['id']
        teacher_id = user.get('teacher_id') if user.get('teacher_id') else None
        student_group_id = user.get('student_group_id') if user.get('student_group_id') else None
        
        # После связывания преподавателя/студента в ms-core, данные могут не синхронизироваться в ms-auth
        # Поэтому дополнительно проверяем связь в ms-core
        try:
            core_client = get_core_client()
            
            # Если нет teacher_id в ms-auth, но роль - преподаватель, ищем связь в ms-core
            # Также проверяем, даже если teacher_id есть, чтобы убедиться в актуальности данных
            if user['primary_role'] == 'teacher':
                logger.info(f"🔍 Checking teacher link for user {user_id} (current teacher_id from ms-auth: {teacher_id})")
                try:
                    # Ищем преподавателя, связанного с этим пользователем
                    logger.info(f"📞 Calling get_teacher_by_user_id({user_id})")
                    teacher_by_user = core_client.get_teacher_by_user_id(user_id)
                    logger.info(f"📥 Response from get_teacher_by_user_id: {teacher_by_user}")
                    
                    if teacher_by_user and teacher_by_user.get('id'):
                        new_teacher_id = teacher_by_user['id']
                        if teacher_id != new_teacher_id:
                            logger.info(f"✅ Found linked teacher {new_teacher_id} for user {user_id} via ms-core (was: {teacher_id})")
                            teacher_id = new_teacher_id
                        elif not teacher_id:
                            logger.info(f"✅ Found linked teacher {new_teacher_id} for user {user_id} via ms-core")
                            teacher_id = new_teacher_id
                        else:
                            logger.info(f"✅ Teacher {teacher_id} already linked to user {user_id}, data is up to date")
                    else:
                        logger.warning(f"⚠️ No teacher found for user {user_id} in ms-core. Response: {teacher_by_user}")
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.NOT_FOUND:
                        logger.info(f"ℹ️ Teacher not found for user {user_id} (this is normal if not yet linked)")
                    else:
                        logger.error(f"❌ gRPC error finding teacher for user {user_id}: {e.code()}: {e.details()}")
                    # Если teacher_id был в ms-auth, но не найден в ms-core, возможно связь разорвана
                    if teacher_id:
                        logger.warning(f"⚠️ Teacher {teacher_id} from ms-auth not found in ms-core for user {user_id}, clearing teacher_id")
                        teacher_id = None
                except Exception as e:
                    logger.error(f"❌ Unexpected error finding teacher for user {user_id}: {type(e).__name__}: {e}", exc_info=True)
                    # Если teacher_id был в ms-auth, но не найден в ms-core, возможно связь разорвана
                    if teacher_id:
                        logger.warning(f"⚠️ Teacher {teacher_id} from ms-auth not found in ms-core for user {user_id}, clearing teacher_id")
                        teacher_id = None
            
            # Если нет student_group_id в ms-auth, но роль - студент, ищем связь в ms-core
            if not student_group_id and user['primary_role'] == 'student':
                try:
                    # Ищем студента, связанного с этим пользователем
                    student_by_user = core_client.get_student_by_user_id(user_id)
                    if student_by_user and student_by_user.get('group_id'):
                        student_group_id = student_by_user['group_id']
                        logger.info(f"✅ Found linked student with group {student_group_id} for user {user_id} via ms-core")
                except Exception as e:
                    logger.debug(f"Could not find student for user {user_id}: {e}")
                    
        except Exception as e:
            logger.warning(f"Error checking links in ms-core for user {user_id}: {e}")
            # Не прерываем запрос, используем данные из ms-auth
        
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
                "teacher_id": teacher_id,
                "student_group_id": student_group_id,
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


@router.get("/register/groups")
async def get_groups_for_registration():
    """
    Получить список активных групп для регистрации (публичный endpoint)
    
    Используется для выбора группы при регистрации студента
    """
    try:
        core_client = get_core_client()
        logger.info("Fetching groups for registration")
        
        if not core_client.stub:
            logger.warning("Core client stub is None - proto files may not be loaded")
            return {
                "success": True,
                "groups": []
            }
        
        result = core_client.list_groups(
            page=1,
            page_size=200,  # Большой лимит для получения всех групп
            only_active=True
        )
        
        logger.info(f"Core service response: total_count={result.get('total_count', 0)}, groups_count={len(result.get('groups', []))}")
        
        # Возвращаем только необходимые поля
        groups = [
            {
                'id': g['id'],
                'name': g['name'],
                'short_name': g.get('short_name', ''),
                'year': g.get('year', 0),
                'level': g.get('level', ''),
            }
            for g in result.get('groups', [])
        ]
        
        logger.info(f"Returning {len(groups)} groups for registration")
        
        return {
            "success": True,
            "groups": groups
        }
    except Exception as e:
        logger.error(f"Error getting groups for registration: {e}", exc_info=True)
        # Возвращаем пустой список вместо ошибки, чтобы форма работала
        return {
            "success": True,
            "groups": [],
            "error": str(e)
        }


@router.get("/register/teachers")
async def get_teachers_for_registration():
    """
    Получить список активных преподавателей для регистрации (публичный endpoint)
    
    Используется для выбора преподавателя при регистрации
    """
    try:
        core_client = get_core_client()
        logger.info("Fetching teachers for registration")
        
        if not core_client.stub:
            logger.warning("Core client stub is None - proto files may not be loaded")
            return {
                "success": True,
                "teachers": []
            }
        
        result = core_client.list_teachers(
            page=1,
            page_size=200,  # Большой лимит для получения всех преподавателей
            only_active=True
        )
        
        logger.info(f"Core service response: total_count={result.get('total_count', 0)}, teachers_count={len(result.get('teachers', []))}")
        
        # Фильтруем только свободных преподавателей (без user_id или user_id = 0/None)
        # Это предотвращает попытки связать уже занятого преподавателя
        all_teachers = result.get('teachers', [])
        
        # Логируем все преподаватели для отладки
        for t in all_teachers:
            teacher_id = t.get('id')
            user_id = t.get('user_id')
            logger.info(f"📋 Teacher {teacher_id}: user_id={user_id} (type={type(user_id).__name__})")
        
        free_teachers = []
        for t in all_teachers:
            user_id = t.get('user_id')
            # Преподаватель свободен, если user_id отсутствует, равен None, 0 или пустой строке
            # Также проверяем, если user_id не в словаре вообще
            is_free = (
                'user_id' not in t or  # Ключ отсутствует
                user_id is None or      # None
                user_id == 0 or         # 0 (int)
                user_id == '' or        # Пустая строка
                (isinstance(user_id, str) and user_id.strip() == '')  # Пустая строка после strip
            )
            if is_free:
                free_teachers.append(t)
                logger.info(f"✅ Teacher {t.get('id')} is FREE (user_id={user_id})")
            else:
                logger.info(f"❌ Teacher {t.get('id')} is LINKED (user_id={user_id})")
        
        logger.info(f"Filtered to {len(free_teachers)} free teachers (out of {len(all_teachers)} total)")
        
        # Возвращаем только необходимые поля
        teachers = [
            {
                'id': t['id'],
                'full_name': t['full_name'],
                'email': t.get('email', ''),
                'position': t.get('position', ''),
                'department': t.get('department', ''),
            }
            for t in free_teachers
        ]
        
        logger.info(f"Returning {len(teachers)} teachers for registration")
        
        return {
            "success": True,
            "teachers": teachers
        }
    except Exception as e:
        logger.error(f"Error getting teachers for registration: {e}", exc_info=True)
        # Возвращаем пустой список вместо ошибки, чтобы форма работала
        return {
            "success": True,
            "teachers": [],
            "error": str(e)
        }

