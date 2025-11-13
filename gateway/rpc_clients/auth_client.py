"""
Auth RPC Client
gRPC клиент для взаимодействия с ms-auth
"""

import grpc
import logging
from typing import Optional, Dict, Any

# Import generated protobuf files from local directory
try:
    from rpc_clients.generated import auth_pb2, auth_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    auth_pb2 = None
    auth_pb2_grpc = None

from config import config

logger = logging.getLogger(__name__)


class AuthClient:
    """gRPC client for authentication microservice"""
    
    def __init__(self):
        """Initialize gRPC channel and stub"""
        self.address = f'{config.MS_AUTH_HOST}:{config.MS_AUTH_PORT}'
        self.channel = None
        self.stub = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to gRPC service"""
        try:
            self.channel = grpc.insecure_channel(
                self.address,
                options=[
                    ('grpc.max_send_message_length', 4 * 1024 * 1024),
                    ('grpc.max_receive_message_length', 4 * 1024 * 1024),
                ]
            )
            
            if auth_pb2_grpc is not None:
                self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)
                logger.info(f"Connected to ms-auth at {self.address}")
            else:
                logger.error("Protobuf files not found")
                
        except Exception as e:
            logger.error(f"Failed to connect to ms-auth: {e}")
            raise
    
    def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        try:
            request = auth_pb2.RegisterRequest(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                full_name=data['full_name'],
                phone=data.get('phone', ''),
                primary_role=data['primary_role'],
                teacher_id=data.get('teacher_id', 0),
                student_group_id=data.get('student_group_id', 0)
            )
            response = self.stub.Register(request, timeout=10)
            
            return {
                'success': response.success,
                'user': self._user_to_dict(response.user) if response.user.id else None,
                'tokens': self._tokens_to_dict(response.tokens) if response.tokens.access_token else None,
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error registering user: {e}")
            raise
    
    def login(self, username: str, password: str, ip_address: str = '', user_agent: str = '') -> Dict[str, Any]:
        """Login user"""
        try:
            request = auth_pb2.LoginRequest(
                username=username,
                password=password,
                ip_address=ip_address,
                user_agent=user_agent
            )
            response = self.stub.Login(request, timeout=10)
            
            return {
                'success': response.success,
                'user': self._user_to_dict(response.user) if response.user.id else None,
                'tokens': self._tokens_to_dict(response.tokens) if response.tokens.access_token else None,
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error logging in: {e}")
            raise
    
    def validate_token(self, access_token: str) -> Dict[str, Any]:
        """Validate access token"""
        try:
            request = auth_pb2.ValidateTokenRequest(access_token=access_token)
            response = self.stub.ValidateToken(request, timeout=5)
            
            return {
                'valid': response.valid,
                'user_id': response.user_id,
                'username': response.username,
                'primary_role': response.primary_role,
                'roles': list(response.roles),
                'expires_at': response.expires_at,
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error validating token: {e}")
            return {'valid': False, 'message': str(e)}
    
    def refresh_token(self, refresh_token: str, ip_address: str = '', user_agent: str = '') -> Dict[str, Any]:
        """Refresh access token"""
        try:
            request = auth_pb2.RefreshTokenRequest(
                refresh_token=refresh_token,
                ip_address=ip_address,
                user_agent=user_agent
            )
            response = self.stub.RefreshToken(request, timeout=10)
            
            return {
                'success': response.success,
                'tokens': self._tokens_to_dict(response.tokens) if response.tokens.access_token else None,
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error refreshing token: {e}")
            raise
    
    def logout(self, user_id: int, refresh_token: str = '') -> Dict[str, Any]:
        """Logout user"""
        try:
            request = auth_pb2.LogoutRequest(
                user_id=user_id,
                refresh_token=refresh_token
            )
            response = self.stub.Logout(request, timeout=5)
            
            return {
                'success': response.success,
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error logging out: {e}")
            raise
    
    def get_current_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get current user by access token"""
        try:
            request = auth_pb2.GetCurrentUserRequest(access_token=access_token)
            response = self.stub.GetCurrentUser(request, timeout=5)
            
            if response.user.id:
                return self._user_to_dict(response.user)
            return None
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                return None
            logger.error(f"RPC error getting current user: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check service health"""
        if not self.stub or auth_pb2 is None:
            return False
        try:
            request = auth_pb2.HealthCheckRequest()
            response = self.stub.HealthCheck(request, timeout=5)
            return response.status == 'healthy'
        except Exception:
            return False
    
    @staticmethod
    def _user_to_dict(user) -> Dict[str, Any]:
        """Convert protobuf User to dict"""
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'primary_role': user.primary_role,
            'roles': list(user.roles),
            'teacher_id': user.teacher_id,
            'staff_id': user.staff_id,
            'student_group_id': user.student_group_id,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'last_login_at': user.last_login_at,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
    
    @staticmethod
    def _tokens_to_dict(tokens) -> Dict[str, Any]:
        """Convert protobuf TokenPair to dict"""
        return {
            'access_token': tokens.access_token,
            'refresh_token': tokens.refresh_token,
            'expires_in': tokens.expires_in,
            'token_type': tokens.token_type
        }
    
    def close(self) -> None:
        """Close gRPC channel"""
        if self.channel:
            self.channel.close()
            logger.info("gRPC channel closed")


# Singleton instance
auth_client = AuthClient()

