"""
⭐⭐⭐ Core RPC Client для ms-agent
KEY INTEGRATION для получения предпочтений преподавателей!
"""
import grpc
import logging
from typing import List, Dict, Any, Optional
import os

# Import generated proto
try:
    import sys
    sys.path.append('/app/ms-core')
    from proto.generated import core_pb2, core_pb2_grpc
except ImportError:
    # Fallback для разработки
    core_pb2 = None
    core_pb2_grpc = None

logger = logging.getLogger(__name__)


class CoreClient:
    """RPC клиент для ms-core"""
    
    def __init__(
        self,
        host: str = None,
        port: int = None
    ):
        """
        Инициализация клиента
        
        Args:
            host: ms-core host (или из env)
            port: ms-core port (или из env)
        """
        self.host = host or os.getenv('MS_CORE_HOST', 'localhost')
        self.port = port or int(os.getenv('MS_CORE_PORT', 50054))
        self.address = f'{self.host}:{self.port}'
        
        # Create channel
        self.channel = grpc.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ]
        )
        
        if core_pb2_grpc:
            self.stub = core_pb2_grpc.CoreServiceStub(self.channel)
            logger.info(f"CoreClient initialized: {self.address}")
        else:
            self.stub = None
            logger.warning("Proto files not available, CoreClient disabled")
    
    def get_all_preferences(
        self,
        semester: Optional[int] = None,
        academic_year: Optional[str] = None,
        teacher_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        ⭐⭐⭐ KEY METHOD!!!
        Получить ВСЕ предпочтения преподавателей для fitness-функции
        
        Args:
            semester: Семестр (опционально)
            academic_year: Учебный год (опционально)
            teacher_ids: Список преподавателей (опционально)
        
        Returns:
            List[Dict] с предпочтениями преподавателей:
            [
                {
                    'teacher_id': int,
                    'teacher_name': str,
                    'teacher_priority': int (1-4),
                    'preferences': [
                        {
                            'day_of_week': int (1-6),
                            'time_slot': int (1-6),
                            'is_preferred': bool
                        },
                        ...
                    ]
                },
                ...
            ]
        """
        if not self.stub:
            logger.error("CoreClient not initialized")
            return []
        
        try:
            request = core_pb2.GetAllPreferencesRequest(
                semester=semester or 0,
                academic_year=academic_year or '',
                teacher_ids=teacher_ids or []
            )
            
            logger.info(f"Calling GetAllPreferences: semester={semester}, year={academic_year}")
            
            response = self.stub.GetAllPreferences(request, timeout=30)
            
            # Преобразовать в список словарей
            result = []
            for pref_set in response.preferences_sets:
                teacher_data = {
                    'teacher_id': pref_set.teacher_id,
                    'teacher_name': pref_set.teacher_name,
                    'teacher_priority': pref_set.teacher_priority,
                    'preferences': []
                }
                
                for pref in pref_set.preferences:
                    teacher_data['preferences'].append({
                        'day_of_week': pref.day_of_week,
                        'time_slot': pref.time_slot,
                        'is_preferred': pref.is_preferred,
                        'preference_strength': pref.preference_strength
                    })
                
                result.append(teacher_data)
            
            logger.info(f"Retrieved preferences for {len(result)} teachers")
            
            return result
            
        except grpc.RpcError as e:
            logger.error(f"RPC error calling GetAllPreferences: {e.code()} - {e.details()}")
            return []
        except Exception as e:
            logger.error(f"Error calling GetAllPreferences: {e}", exc_info=True)
            return []
    
    def get_teacher(self, teacher_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить преподавателя
        
        Args:
            teacher_id: ID преподавателя
        
        Returns:
            Dict с информацией о преподавателе или None
        """
        if not self.stub:
            return None
        
        try:
            request = core_pb2.GetTeacherRequest(
                id=teacher_id,
                include_preferences=False
            )
            
            response = self.stub.GetTeacher(request, timeout=10)
            
            if not response.teacher:
                return None
            
            teacher = response.teacher
            return {
                'id': teacher.id,
                'full_name': teacher.full_name,
                'email': teacher.email,
                'employment_type': teacher.employment_type,
                'priority': teacher.priority,
                'department': teacher.department,
                'is_active': teacher.is_active
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error calling GetTeacher: {e.code()}")
            return None
    
    def health_check(self) -> bool:
        """
        Проверить доступность ms-core
        
        Returns:
            True если сервис доступен
        """
        if not self.stub:
            return False
        
        try:
            request = core_pb2.HealthCheckRequest()
            response = self.stub.HealthCheck(request, timeout=5)
            return response.status == 'healthy'
        except:
            return False
    
    def close(self):
        """Закрыть соединение"""
        if self.channel:
            self.channel.close()
            logger.info("CoreClient connection closed")


# Глобальный клиент
_core_client: Optional[CoreClient] = None


def get_core_client() -> CoreClient:
    """Получить глобальный экземпляр Core клиента"""
    global _core_client
    if _core_client is None:
        _core_client = CoreClient()
    return _core_client


def close_core_client():
    """Закрыть глобальный клиент"""
    global _core_client
    if _core_client is not None:
        _core_client.close()
        _core_client = None

