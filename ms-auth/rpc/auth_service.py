"""
gRPC Auth Service Implementation
Имплементация gRPC сервиса для аутентификации
"""

import grpc
import hashlib
import logging

try:
    from proto.generated import auth_pb2, auth_pb2_grpc
except ImportError:
    auth_pb2 = None
    auth_pb2_grpc = None

from db.connection import db
from services.auth import auth_service
from services.token import token_service
from services.user_crud import user_crud
from utils.validators import validate_register_data, validate_login_data
from utils.cache import cache
from utils.metrics import (
    rpc_requests_total, rpc_duration_seconds,
    registrations_total, logins_total, token_validations_total
)
from config import config

logger = logging.getLogger(__name__)


class AuthServicer:
    """gRPC Auth Service Implementation"""
    
    def __init__(self):
        pass
    
    def _build_user_message(self, user: dict):
        """Построить protobuf сообщение User"""
        if auth_pb2 is None:
            return None
        
        return auth_pb2.User(
            id=user.get('id', 0),
            username=user.get('username', ''),
            email=user.get('email', ''),
            full_name=user.get('full_name', ''),
            phone=user.get('phone', '') or '',
            primary_role=user.get('primary_role', ''),
            roles=user.get('roles', []),
            teacher_id=user.get('teacher_id', 0) or 0,
            staff_id=user.get('staff_id', 0) or 0,
            student_group_id=user.get('student_group_id', 0) or 0,
            is_active=user.get('is_active', True),
            is_verified=user.get('is_verified', False),
            last_login_at=str(user.get('last_login_at', '') or ''),
            created_at=str(user.get('created_at', '')),
            updated_at=str(user.get('updated_at', ''))
        )
    
    def _build_token_pair(self, tokens: dict):
        """Построить protobuf сообщение TokenPair"""
        if auth_pb2 is None:
            return None
        
        return auth_pb2.TokenPair(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            expires_in=tokens['expires_in'],
            token_type=tokens.get('token_type', 'Bearer')
        )
    
    def Register(self, request, context):
        """Регистрация нового пользователя"""
        method = "Register"
        
        try:
            # Валидация
            request_data = {
                'username': request.username,
                'email': request.email,
                'password': request.password,
                'full_name': request.full_name,
                'primary_role': request.primary_role
            }
            
            errors = validate_register_data(request_data)
            if errors:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Validation errors: {', '.join(errors)}")
                registrations_total.labels(status='validation_error').inc()
                return auth_pb2.RegisterResponse(success=False, message='; '.join(errors))
            
            # Регистрация
            user, tokens = auth_service.register(
                username=request.username,
                email=request.email,
                password=request.password,
                full_name=request.full_name,
                phone=request.phone if request.phone else None,
                primary_role=request.primary_role,
                teacher_id=request.teacher_id if request.teacher_id else None,
                student_group_id=request.student_group_id if request.student_group_id else None
            )
            
            logger.info(f"✅ User registered: {user['username']} (ID: {user['id']})")
            registrations_total.labels(status='success').inc()
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.RegisterResponse(
                success=True,
                user=self._build_user_message(user),
                tokens=self._build_token_pair(tokens),
                message="Registration successful"
            )
            
        except ValueError as e:
            logger.warning(f"Registration failed: {e}")
            registrations_total.labels(status='error').inc()
            rpc_requests_total.labels(method=method, status='validation_error').inc()
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return auth_pb2.RegisterResponse(success=False, message=str(e))
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            registrations_total.labels(status='error').inc()
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_pb2.RegisterResponse(success=False, message="Internal error")
    
    def Login(self, request, context):
        """Вход пользователя"""
        method = "Login"
        
        try:
            # Валидация
            request_data = {
                'username': request.username,
                'password': request.password
            }
            
            errors = validate_login_data(request_data)
            if errors:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Validation errors: {', '.join(errors)}")
                logins_total.labels(status='validation_error').inc()
                return auth_pb2.LoginResponse(success=False, message='; '.join(errors))
            
            # Вход
            user, tokens = auth_service.login(
                username=request.username,
                password=request.password,
                ip_address=request.ip_address if request.ip_address else '',
                user_agent=request.user_agent if request.user_agent else '',
                device_id=request.device_id if request.device_id else ''
            )
            
            logger.info(f"✅ User logged in: {user['username']} (IP: {request.ip_address})")
            logins_total.labels(status='success').inc()
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.LoginResponse(
                success=True,
                user=self._build_user_message(user),
                tokens=self._build_token_pair(tokens),
                message="Login successful"
            )
            
        except ValueError as e:
            logger.warning(f"Login failed for {request.username}: {e}")
            logins_total.labels(status='failed').inc()
            rpc_requests_total.labels(method=method, status='auth_failed').inc()
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(str(e))
            return auth_pb2.LoginResponse(success=False, message=str(e))
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            logins_total.labels(status='error').inc()
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_pb2.LoginResponse(success=False, message="Internal error")
    
    def ValidateToken(self, request, context):
        """Валидировать access token"""
        method = "ValidateToken"
        
        try:
            # Проверка кэша
            token_hash = hashlib.sha256(request.access_token.encode()).hexdigest()
            cache_key = f"token_valid:{token_hash}"
            cached = cache.get(cache_key)
            
            if cached and config.CACHE_ENABLED:
                rpc_requests_total.labels(method=method, status='cache_hit').inc()
                token_validations_total.labels(result='valid').inc()
                return cached
            
            # Валидация
            result = token_service.validate_access_token(request.access_token)
            
            if result['valid']:
                payload = result['payload']
                response = auth_pb2.ValidateTokenResponse(
                    valid=True,
                    user_id=int(payload['sub']),
                    username=payload['username'],
                    primary_role=payload['role'],
                    roles=payload['roles'],
                    expires_at=int(payload['exp']),
                    message="Token valid"
                )
                
                # Кэшировать на 5 минут
                if config.CACHE_ENABLED:
                    cache.set(cache_key, response, ttl=300)
                
                token_validations_total.labels(result='valid').inc()
                rpc_requests_total.labels(method=method, status='valid').inc()
            else:
                response = auth_pb2.ValidateTokenResponse(
                    valid=False,
                    message=result.get('error', 'Invalid token')
                )
                token_validations_total.labels(result='invalid').inc()
                rpc_requests_total.labels(method=method, status='invalid').inc()
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            token_validations_total.labels(result='error').inc()
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.ValidateTokenResponse(valid=False, message="Internal error")
    
    def RefreshToken(self, request, context):
        """Обновить access token используя refresh token"""
        method = "RefreshToken"
        
        try:
            tokens = auth_service.refresh_tokens(
                refresh_token=request.refresh_token,
                ip_address=request.ip_address if request.ip_address else '',
                user_agent=request.user_agent if request.user_agent else ''
            )
            
            logger.info(f"✅ Tokens refreshed")
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.RefreshTokenResponse(
                success=True,
                tokens=self._build_token_pair(tokens),
                message="Tokens refreshed"
            )
            
        except ValueError as e:
            logger.warning(f"Token refresh failed: {e}")
            rpc_requests_total.labels(method=method, status='invalid_token').inc()
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(str(e))
            return auth_pb2.RefreshTokenResponse(success=False, message=str(e))
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_pb2.RefreshTokenResponse(success=False, message="Internal error")
    
    def Logout(self, request, context):
        """Выход пользователя"""
        method = "Logout"
        
        try:
            auth_service.logout(
                user_id=request.user_id,
                refresh_token=request.refresh_token
            )
            
            # Инвалидация кэша токенов
            cache.invalidate_pattern('token_valid:*')
            
            logger.info(f"✅ User logged out: ID={request.user_id}")
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.LogoutResponse(
                success=True,
                message="Logged out successfully"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_pb2.LogoutResponse(success=False, message="Internal error")
    
    def GetCurrentUser(self, request, context):
        """Получить текущего пользователя по access token"""
        method = "GetCurrentUser"
        
        try:
            # Валидация токена
            result = token_service.validate_access_token(request.access_token)
            
            if not result['valid']:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details(result['error'])
                return auth_pb2.UserResponse(message=result['error'])
            
            # Получить пользователя
            user_id = int(result['payload']['sub'])
            user = user_crud.get_by_id(user_id)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return auth_pb2.UserResponse(message="User not found")
            
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.UserResponse(
                user=self._build_user_message(user),
                message="User retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.UserResponse(message="Internal error")
    
    def HealthCheck(self, request, context):
        """Проверка здоровья сервиса"""
        return auth_pb2.HealthCheckResponse(
            status="healthy",
            version=config.SERVICE_VERSION
        )
    
    # ============================================================
    # USER MANAGEMENT METHODS
    # ============================================================
    
    def GetUser(self, request, context):
        """Get user by ID, username, or email"""
        method = "GetUser"
        
        try:
            user = None
            
            # Determine which identifier was provided
            if request.HasField('id'):
                user = user_crud.get_by_id(request.id)
            elif request.HasField('username'):
                user = user_crud.get_by_username(request.username)
            elif request.HasField('email'):
                user = user_crud.get_by_email(request.email)
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("No identifier provided")
                return auth_pb2.UserResponse(message="No identifier provided")
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return auth_pb2.UserResponse(message="User not found")
            
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.UserResponse(
                user=self._build_user_message(user),
                message="User retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.UserResponse(message="Internal error")
    
    def UpdateUser(self, request, context):
        """Update user"""
        method = "UpdateUser"
        
        try:
            # Build updates dict (only non-empty fields)
            updates = {}
            
            if request.full_name:
                updates['full_name'] = request.full_name
            if request.email:
                updates['email'] = request.email
            if request.phone:
                updates['phone'] = request.phone
            if request.HasField('is_active'):
                updates['is_active'] = request.is_active
            
            if not updates:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("No fields to update")
                return auth_pb2.UserResponse(message="No fields to update")
            
            # Update user
            user = user_crud.update(request.id, updates)
            
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return auth_pb2.UserResponse(message="User not found")
            
            logger.info(f"✅ User updated: ID={request.id}")
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.UserResponse(
                user=self._build_user_message(user),
                message="User updated successfully"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.UserResponse(message="Internal error")
    
    def DeleteUser(self, request, context):
        """Delete user (soft or hard delete)"""
        method = "DeleteUser"
        
        try:
            success = user_crud.delete(request.id, request.hard_delete)
            
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found or delete failed")
                return auth_pb2.DeleteResponse(
                    success=False,
                    message="User not found or delete failed"
                )
            
            delete_type = "hard" if request.hard_delete else "soft"
            logger.info(f"✅ User deleted ({delete_type}): ID={request.id}")
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.DeleteResponse(
                success=True,
                message=f"User deleted successfully ({delete_type})"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.DeleteResponse(success=False, message="Internal error")
    
    def ListUsers(self, request, context):
        """List users with pagination and filters"""
        method = "ListUsers"
        
        try:
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 20
            
            users, total = user_crud.list_users(
                page=page,
                page_size=page_size,
                only_active=request.only_active if request.HasField('only_active') else None,
                search_query=request.search_query if request.search_query else None,
                sort_by=request.sort_by if request.sort_by else 'username',
                sort_order=request.sort_order if request.sort_order else 'ASC'
            )
            
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.ListUsersResponse(
                users=[self._build_user_message(u) for u in users],
                total_count=total,
                page=page,
                page_size=page_size
            )
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.ListUsersResponse()
    
    # ============================================================
    # PASSWORD MANAGEMENT METHODS
    # ============================================================
    
    def ChangePassword(self, request, context):
        """Change user password"""
        method = "ChangePassword"
        
        try:
            from services.password import password_service
            
            # Get user
            user = user_crud.get_by_id(request.user_id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return auth_pb2.ChangePasswordResponse(
                    success=False,
                    message="User not found"
                )
            
            # Verify old password
            if not password_service.verify_password(request.old_password, user['password_hash']):
                logger.warning(f"Password change failed: incorrect old password (User ID={request.user_id})")
                return auth_pb2.ChangePasswordResponse(
                    success=False,
                    message="Incorrect old password"
                )
            
            # Hash new password
            new_hash = password_service.hash_password(request.new_password)
            
            # Update password
            success = user_crud.update_password(request.user_id, new_hash)
            
            if success:
                logger.info(f"✅ Password changed: User ID={request.user_id}")
                rpc_requests_total.labels(method=method, status='success').inc()
                return auth_pb2.ChangePasswordResponse(
                    success=True,
                    message="Password changed successfully"
                )
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                return auth_pb2.ChangePasswordResponse(
                    success=False,
                    message="Failed to update password"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.ChangePasswordResponse(success=False, message="Internal error")
    
    def RequestPasswordReset(self, request, context):
        """Request password reset token (email would be sent in production)"""
        method = "RequestPasswordReset"
        
        try:
            # Get user by email
            user = user_crud.get_by_email(request.email)
            
            if not user:
                # Security: Don't reveal if user exists
                logger.warning(f"Password reset requested for non-existent email: {request.email}")
                return auth_pb2.PasswordResetResponse(
                    success=True,
                    message="If the email exists, a reset link will be sent"
                )
            
            # Generate reset token (simplified for now - in production use signed JWT)
            import secrets
            reset_token = secrets.token_urlsafe(32)
            
            # Store token in cache (TTL: 1 hour)
            cache_key = f"password_reset:{reset_token}"
            cache.set(cache_key, user['id'], ttl=3600)
            
            logger.info(f"✅ Password reset requested: User ID={user['id']}, Email={request.email}")
            logger.info(f"🔑 Reset token (for testing): {reset_token}")
            
            rpc_requests_total.labels(method=method, status='success').inc()
            
            # In production, send email here
            # email_service.send_reset_email(user['email'], reset_token)
            
            return auth_pb2.PasswordResetResponse(
                success=True,
                message="If the email exists, a reset link will be sent"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.PasswordResetResponse(success=False, message="Internal error")
    
    def ResetPassword(self, request, context):
        """Reset password using reset token"""
        method = "ResetPassword"
        
        try:
            from services.password import password_service
            
            # Verify token
            cache_key = f"password_reset:{request.token}"
            user_id = cache.get(cache_key)
            
            if not user_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Invalid or expired reset token")
                return auth_pb2.ResetPasswordResponse(
                    success=False,
                    message="Invalid or expired reset token"
                )
            
            # Hash new password
            new_hash = password_service.hash_password(request.new_password)
            
            # Update password
            success = user_crud.update_password(user_id, new_hash)
            
            if success:
                # Invalidate token
                cache.delete(cache_key)
                
                logger.info(f"✅ Password reset successful: User ID={user_id}")
                rpc_requests_total.labels(method=method, status='success').inc()
                
                return auth_pb2.ResetPasswordResponse(
                    success=True,
                    message="Password reset successfully"
                )
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                return auth_pb2.ResetPasswordResponse(
                    success=False,
                    message="Failed to reset password"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.ResetPasswordResponse(success=False, message="Internal error")
    
    # ============================================================
    # ROLE MANAGEMENT METHODS
    # ============================================================
    
    def AssignRole(self, request, context):
        """Assign role to user"""
        method = "AssignRole"
        
        try:
            from db.queries import roles as role_queries
            
            # Get role by code
            role = db.execute_query(
                role_queries.SELECT_ROLE_BY_CODE,
                {'code': request.role_code},
                fetch=True
            )
            
            if not role:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Role not found: {request.role_code}")
                return auth_pb2.AssignRoleResponse(
                    success=False,
                    message=f"Role not found: {request.role_code}"
                )
            
            role_id = role[0]['id']
            
            # Assign role
            db.execute_query(
                role_queries.INSERT_USER_ROLE,
                {
                    'user_id': request.user_id,
                    'role_id': role_id,
                    'granted_by': request.granted_by if request.granted_by else None
                },
                fetch=False
            )
            
            logger.info(f"✅ Role assigned: User ID={request.user_id}, Role={request.role_code}")
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.AssignRoleResponse(
                success=True,
                message=f"Role '{request.role_code}' assigned successfully"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.AssignRoleResponse(success=False, message="Internal error")
    
    def RevokeRole(self, request, context):
        """Revoke role from user"""
        method = "RevokeRole"
        
        try:
            from db.queries import roles as role_queries
            
            # Get role by code
            role = db.execute_query(
                role_queries.SELECT_ROLE_BY_CODE,
                {'code': request.role_code},
                fetch=True
            )
            
            if not role:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Role not found: {request.role_code}")
                return auth_pb2.RevokeRoleResponse(
                    success=False,
                    message=f"Role not found: {request.role_code}"
                )
            
            role_id = role[0]['id']
            
            # Revoke role
            db.execute_query(
                role_queries.DELETE_USER_ROLE,
                {'user_id': request.user_id, 'role_id': role_id},
                fetch=False
            )
            
            logger.info(f"✅ Role revoked: User ID={request.user_id}, Role={request.role_code}")
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.RevokeRoleResponse(
                success=True,
                message=f"Role '{request.role_code}' revoked successfully"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.RevokeRoleResponse(success=False, message="Internal error")
    
    def GetUserRoles(self, request, context):
        """Get all roles for a user"""
        method = "GetUserRoles"
        
        try:
            from db.queries import roles as role_queries
            
            # Get user roles
            roles = db.execute_query(
                role_queries.SELECT_USER_ROLES,
                {'user_id': request.user_id},
                fetch=True
            )
            
            role_messages = []
            for role in roles:
                role_messages.append(auth_pb2.Role(
                    id=role['id'],
                    name=role['name'],
                    code=role['code'],
                    description=role.get('description', '') or '',
                    permissions=dict(role.get('permissions', {}))
                ))
            
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.UserRolesResponse(roles=role_messages)
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.UserRolesResponse()
    
    # ============================================================
    # LOGIN HISTORY METHOD
    # ============================================================
    
    def GetLoginHistory(self, request, context):
        """Get login history for user"""
        method = "GetLoginHistory"
        
        try:
            from db.queries import login_history as history_queries
            
            limit = request.limit if request.limit > 0 else 50
            only_successful = request.only_successful if request.HasField('only_successful') else None
            
            # Get login history
            history = db.execute_query(
                history_queries.GET_LOGIN_HISTORY,
                {
                    'user_id': request.user_id,
                    'limit': limit,
                    'only_successful': only_successful
                },
                fetch=True
            )
            
            entries = []
            for entry in history:
                entries.append(auth_pb2.LoginHistoryEntry(
                    id=entry['id'],
                    username=entry.get('username', ''),
                    success=entry['success'],
                    ip_address=entry.get('ip_address', '') or '',
                    user_agent=entry.get('user_agent', '') or '',
                    failure_reason=entry.get('failure_reason', '') or '',
                    created_at=str(entry.get('created_at', ''))
                ))
            
            rpc_requests_total.labels(method=method, status='success').inc()
            
            return auth_pb2.LoginHistoryResponse(entries=entries)
            
        except Exception as e:
            logger.error(f"❌ Error in {method}: {e}", exc_info=True)
            rpc_requests_total.labels(method=method, status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.LoginHistoryResponse()

