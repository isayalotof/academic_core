"""
Schedule RPC Client для ms-agent
Подключение к ms-schedule для массового создания занятий
"""
import grpc
import logging
from typing import List, Dict, Any
import os

# Import generated proto
try:
    import sys
    sys.path.append('/app/ms-schedule')
    from proto.generated import schedule_pb2, schedule_pb2_grpc
except ImportError:
    schedule_pb2 = None
    schedule_pb2_grpc = None

logger = logging.getLogger(__name__)


class ScheduleClient:
    """RPC клиент для ms-schedule"""
    
    def __init__(self, host: str = None, port: int = None):
        """
        Инициализация клиента
        
        Args:
            host: ms-schedule host (или из env)
            port: ms-schedule port (или из env)
        """
        self.host = host or os.getenv('MS_SCHEDULE_HOST', 'localhost')
        self.port = port or int(os.getenv('MS_SCHEDULE_PORT', 50055))
        self.address = f'{self.host}:{self.port}'
        
        # Create channel
        self.channel = grpc.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ]
        )
        
        if schedule_pb2_grpc:
            self.stub = schedule_pb2_grpc.ScheduleServiceStub(self.channel)
            logger.info(f"ScheduleClient initialized: {self.address}")
        else:
            self.stub = None
            logger.warning("Proto files not available, ScheduleClient disabled")
    
    def bulk_create_lessons(
        self,
        lessons: List[Dict[str, Any]],
        generation_id: str = None
    ) -> Dict[str, Any]:
        """
        ⭐ KEY METHOD для ms-agent!
        Массовое создание занятий после генерации расписания
        
        Args:
            lessons: Список занятий для создания
            generation_id: ID генерации
        
        Returns:
            Dict с результатом операции:
            {
                'success': bool,
                'created_count': int,
                'failed_count': int,
                'errors': List[str]
            }
        """
        if not self.stub:
            raise Exception("ScheduleClient not initialized")
        
        logger.info(f"BulkCreateLessons: {len(lessons)} lessons, gen_id={generation_id}")
        
        try:
            # Преобразовать lessons в proto messages
            lesson_items = []
            for lesson in lessons:
                lesson_items.append(schedule_pb2.LessonInput(
                    day_of_week=lesson['day_of_week'],
                    time_slot=lesson['time_slot'],
                    discipline_id=lesson.get('discipline_id', 0),
                    discipline_name=lesson.get('discipline_name', ''),
                    teacher_id=lesson.get('teacher_id', 0),
                    teacher_name=lesson.get('teacher_name', ''),
                    group_id=lesson.get('group_id', 0),
                    group_name=lesson.get('group_name', ''),
                    classroom_id=lesson.get('classroom_id', 0),
                    classroom_name=lesson.get('classroom_name', ''),
                    lesson_type=lesson.get('lesson_type', 'lecture'),
                    semester=lesson.get('semester', 1),
                    academic_year=lesson.get('academic_year', ''),
                    notes=lesson.get('notes', '')
                ))
            
            request = schedule_pb2.BulkCreateRequest(
                lessons=lesson_items,
                generation_id=generation_id or ''
            )
            
            response = self.stub.BulkCreateLessons(request, timeout=120)
            
            result = {
                'success': response.success,
                'created_count': response.created_count,
                'failed_count': response.failed_count,
                'errors': list(response.errors)
            }
            
            logger.info(
                f"BulkCreateLessons result: created={result['created_count']}, "
                f"failed={result['failed_count']}"
            )
            
            return result
            
        except grpc.RpcError as e:
            logger.error(f"RPC error calling BulkCreateLessons: {e.code()} - {e.details()}")
            return {
                'success': False,
                'created_count': 0,
                'failed_count': len(lessons),
                'errors': [f"RPC error: {e.details()}"]
            }
        except Exception as e:
            logger.error(f"Error calling BulkCreateLessons: {e}", exc_info=True)
            return {
                'success': False,
                'created_count': 0,
                'failed_count': len(lessons),
                'errors': [str(e)]
            }
    
    def activate_schedule(
        self,
        semester: int,
        academic_year: str,
        generation_id: str
    ) -> bool:
        """
        ⭐ Активировать расписание после успешной генерации
        
        Args:
            semester: Семестр (1 или 2)
            academic_year: Учебный год (например "2024/2025")
            generation_id: ID генерации
        
        Returns:
            True если успешно активировано
        """
        if not self.stub:
            raise Exception("ScheduleClient not initialized")
        
        logger.info(f"ActivateSchedule: sem={semester}, year={academic_year}, gen={generation_id}")
        
        try:
            request = schedule_pb2.ActivateRequest(
                semester=semester,
                academic_year=academic_year,
                generation_id=generation_id
            )
            
            response = self.stub.ActivateSchedule(request, timeout=60)
            
            logger.info(f"ActivateSchedule result: {response.success}")
            
            return response.success
            
        except grpc.RpcError as e:
            logger.error(f"RPC error calling ActivateSchedule: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            logger.error(f"Error calling ActivateSchedule: {e}", exc_info=True)
            return False
    
    def get_schedule(
        self,
        semester: int,
        academic_year: str,
        group_id: int = None,
        teacher_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Получить расписание для проверки
        
        Args:
            semester: Семестр
            academic_year: Учебный год
            group_id: ID группы (опционально)
            teacher_id: ID преподавателя (опционально)
        
        Returns:
            Список занятий
        """
        if not self.stub:
            return []
        
        try:
            if group_id:
                request = schedule_pb2.GetScheduleRequest(
                    group_id=group_id,
                    semester=semester,
                    academic_year=academic_year
                )
                response = self.stub.GetGroupSchedule(request, timeout=30)
            elif teacher_id:
                request = schedule_pb2.GetScheduleRequest(
                    teacher_id=teacher_id,
                    semester=semester,
                    academic_year=academic_year
                )
                response = self.stub.GetTeacherSchedule(request, timeout=30)
            else:
                return []
            
            # Преобразовать в список словарей
            lessons = []
            for lesson in response.lessons:
                lessons.append({
                    'id': lesson.id,
                    'day_of_week': lesson.day_of_week,
                    'time_slot': lesson.time_slot,
                    'discipline_name': lesson.discipline_name,
                    'teacher_name': lesson.teacher_name,
                    'group_name': lesson.group_name,
                    'classroom_name': lesson.classroom_name,
                    'lesson_type': lesson.lesson_type
                })
            
            return lessons
            
        except grpc.RpcError as e:
            logger.error(f"RPC error getting schedule: {e.code()}")
            return []
        except Exception as e:
            logger.error(f"Error getting schedule: {e}", exc_info=True)
            return []
    
    def health_check(self) -> bool:
        """
        Проверить доступность ms-schedule
        
        Returns:
            True если сервис доступен
        """
        if not self.stub:
            return False
        
        try:
            request = schedule_pb2.HealthCheckRequest()
            response = self.stub.HealthCheck(request, timeout=5)
            return response.status == 'healthy'
        except:
            return False
    
    def close(self):
        """Закрыть соединение"""
        if self.channel:
            self.channel.close()
            logger.info("ScheduleClient connection closed")


# Глобальный клиент
_schedule_client = None


def get_schedule_client() -> ScheduleClient:
    """Получить глобальный экземпляр Schedule клиента"""
    global _schedule_client
    if _schedule_client is None:
        _schedule_client = ScheduleClient()
    return _schedule_client


def close_schedule_client():
    """Закрыть глобальный клиент"""
    global _schedule_client
    if _schedule_client is not None:
        _schedule_client.close()
        _schedule_client = None

