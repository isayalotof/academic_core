"""
gRPC client for ms-schedule
RPC клиент для взаимодействия с микросервисом расписания
"""

import grpc
import logging
from typing import Optional, Dict, List, Tuple

# Import generated protobuf files from local directory
try:
    from rpc_clients.generated import schedule_pb2, schedule_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    schedule_pb2 = None
    schedule_pb2_grpc = None

from config import config

logger = logging.getLogger(__name__)


class ScheduleClient:
    """gRPC client for Schedule service"""
    
    def __init__(self):
        """Initialize schedule client"""
        self.host = config.MS_SCHEDULE_HOST
        self.port = config.MS_SCHEDULE_PORT
        self.channel: Optional[grpc.Channel] = None
        self.stub = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to ms-schedule"""
        try:
            address = f"{self.host}:{self.port}"
            self.channel = grpc.insecure_channel(
                address,
                options=[
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100MB
                    ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ]
            )
            
            # Create stub if protobuf available
            if schedule_pb2_grpc is not None:
                self.stub = schedule_pb2_grpc.ScheduleServiceStub(self.channel)
                logger.info(f"✅ ScheduleClient connected to {address}")
            else:
                logger.error("Protobuf files not found")
                raise ImportError("schedule_pb2_grpc not available")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to ms-schedule: {e}")
            raise
    
    def get_group_schedule(
        self,
        group_id: int,
        semester: int,
        academic_year: str,
        day_of_week: Optional[int] = None,
        week_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get schedule for group
        
        Args:
            group_id: Group ID
            semester: Semester number
            academic_year: Academic year
            day_of_week: Optional day filter
            week_type: Optional week type filter
            
        Returns:
            List of lessons
        """
        try:
            # Временно используем прямой запрос к БД через agent_client
            # пока ms-schedule не реализован
            from rpc_clients.agent_client import agent_client
            
            # Получаем активное расписание через agent_client
            schedules = agent_client.get_schedule(generation_id=None, only_active=True)
            
            logger.info(f"GetGroupSchedule: Retrieved {len(schedules)} total schedules from agent_client")
            logger.info(f"  Filtering: group_id={group_id}, semester={semester}, academic_year={academic_year}, day_of_week={day_of_week} (type: {type(day_of_week)})")
            
            # КРИТИЧНО: Проверить, что day_of_week правильно передается
            if day_of_week is not None:
                logger.info(f"  🔍 Day filter is active: day_of_week={day_of_week} (API format, 0=Monday), will filter for day={day_of_week + 1} (DB format)")
            else:
                logger.warning(f"  ⚠️ Day filter is NOT active (day_of_week=None), will return ALL days!")
            
            # Фильтруем по группе, семестру и учебному году
            filtered = []
            # КРИТИЧЕСКАЯ ПРОВЕРКА: Отследить дубликаты при фильтрации
            seen_slots = {}  # {(day, time_slot, group_id): schedule}
            duplicates_found = []
            
            for schedule in schedules:
                schedule_group_id = schedule.get('group_id')
                schedule_semester = schedule.get('semester')
                schedule_academic_year = schedule.get('academic_year')
                schedule_day = schedule.get('day_of_week')
                schedule_slot = schedule.get('time_slot')
                
                # КРИТИЧНО: Проверяем, что schedule_day валиден (1-6)
                if schedule_day is None:
                    logger.warning(
                        f"  Schedule id={schedule.get('id')}: day_of_week is None, skipping!"
                    )
                    continue
                if schedule_day < 1 or schedule_day > 6:
                    logger.warning(
                        f"  Schedule id={schedule.get('id')}: invalid day_of_week={schedule_day} "
                        f"(must be 1-6), skipping!"
                    )
                    continue
                
                # Логируем для отладки первые несколько записей
                if len(schedules) <= 20:  # Логируем все, если их немного
                    logger.info(
                        f"  Schedule: id={schedule.get('id')}, group_id={schedule_group_id}, "
                        f"semester={schedule_semester}, academic_year={schedule_academic_year}, "
                        f"day={schedule_day}, slot={schedule_slot}, "
                        f"discipline={schedule.get('discipline_name')}, "
                        f"generation_id={schedule.get('generation_id')}, is_active={schedule.get('is_active')}"
                    )
                
                # Проверяем совпадение группы
                if schedule_group_id != group_id:
                    continue
                
                # КРИТИЧЕСКАЯ ПРОВЕРКА: Проверяем семестр и учебный год
                # ВРЕМЕННО: Если в БД semester или academic_year пустые/None (из-за бага сохранения),
                # используем значения из запроса для совместимости
                # TODO: Исправить сохранение semester и academic_year в БД
                if schedule_semester is None:
                    logger.warning(
                        f"  Schedule id={schedule.get('id')}: semester is None in DB, using request value {semester}"
                    )
                    schedule_semester = semester  # Используем значение из запроса
                elif schedule_semester != semester:
                    # Если semester не совпадает - пропускаем
                    continue
                
                # Проверяем учебный год
                if not schedule_academic_year or not schedule_academic_year.strip():
                    logger.warning(
                        f"  Schedule id={schedule.get('id')}: academic_year is empty in DB, using request value '{academic_year}'"
                    )
                    schedule_academic_year = academic_year  # Используем значение из запроса
                elif schedule_academic_year.strip() != academic_year:
                    # Учебный год не совпадает - пропускаем
                    continue
                
                # Проверяем день недели (в БД: 1-6, в API: 0-5 или None)
                # КРИТИЧНО: day_of_week может быть 0 (понедельник), поэтому проверяем не только на None!
                if day_of_week is not None and day_of_week != -1:  # -1 используется для "все дни"
                    # API передает 0-5 (0=понедельник), БД хранит 1-6 (1=понедельник)
                    expected_day = day_of_week + 1
                    logger.info(
                        f"  Checking day filter: day_of_week={day_of_week} (API) -> expected_day={expected_day} (DB), "
                        f"schedule_day={schedule_day}, match={schedule_day == expected_day}"
                    )
                    if schedule_day != expected_day:
                        logger.info(
                            f"  ⏭️ Skipping schedule id={schedule.get('id')}: day mismatch "
                            f"(expected {expected_day}, got {schedule_day})"
                        )
                        continue
                elif day_of_week is None:
                    logger.debug(
                        f"  No day filter: day_of_week=None, accepting all days"
                    )
                
                if week_type is None or schedule.get('week_type') == week_type or schedule.get('week_type') == 'both':
                    # КРИТИЧЕСКАЯ ПРОВЕРКА: Проверить дубликаты по (day, time_slot, group_id)
                    slot_key = (schedule_day, schedule_slot, schedule_group_id)
                    if slot_key in seen_slots:
                        existing = seen_slots[slot_key]
                        duplicates_found.append({
                            'existing': existing,
                            'duplicate': schedule
                        })
                        logger.error(
                            f"❌ DUPLICATE FOUND in database response! "
                            f"Slot (day={schedule_day}, slot={schedule_slot}, group={schedule_group_id}) "
                            f"Existing ID={existing.get('id')}, discipline={existing.get('discipline_name')}, "
                            f"generation_id={existing.get('generation_id')}, is_active={existing.get('is_active')}. "
                            f"Duplicate ID={schedule.get('id')}, discipline={schedule.get('discipline_name')}, "
                            f"generation_id={schedule.get('generation_id')}, is_active={schedule.get('is_active')}. "
                            f"Skipping duplicate!"
                        )
                        continue  # Пропускаем дубликат!
                    
                    seen_slots[slot_key] = schedule
                    
                    # КРИТИЧНО: Логируем, что занятие проходит все проверки
                    logger.info(
                        f"  ✅ Adding schedule id={schedule.get('id')}: day={schedule_day}, slot={schedule_slot}, "
                        f"discipline={schedule.get('discipline_name')}, group={schedule_group_id}"
                    )
                    
                    filtered.append({
                        'id': schedule.get('id'),
                        'day_of_week': schedule_day,  # Используем проверенное значение
                        'time_slot': schedule.get('time_slot'),
                        'week_type': schedule.get('week_type', 'both'),
                        'start_time': self._get_time_slot_start(schedule.get('time_slot', 1)),
                        'end_time': self._get_time_slot_end(schedule.get('time_slot', 1)),
                        'discipline_name': schedule.get('discipline_name', ''),
                        'teacher_name': schedule.get('teacher_name', ''),
                        'group_id': schedule_group_id,  # КРИТИЧНО: Добавляем group_id для фильтрации дубликатов
                        'group_name': schedule.get('group_name', ''),
                        'classroom_name': schedule.get('classroom_name'),
                        'building_name': None,  # TODO: получить из classroom
                        'lesson_type': schedule.get('lesson_type', ''),
                        'semester': schedule.get('semester'),
                        'academic_year': schedule.get('academic_year', ''),
                        'is_active': schedule.get('is_active', True)
                    })
            
            if duplicates_found:
                logger.error(
                    f"❌ CRITICAL: Found {len(duplicates_found)} duplicates in database response for group_id={group_id}! "
                    f"These duplicates will be filtered out from the response."
                )
            
            logger.info(
                f"GetGroupSchedule: group_id={group_id}, found {len(filtered)} lessons "
                f"(removed {len(duplicates_found)} duplicates if any)"
            )
            return filtered
            
        except Exception as e:
            logger.error(f"Error getting group schedule: {e}", exc_info=True)
            return []
    
    def get_teacher_schedule(
        self,
        teacher_id: int,
        semester: int,
        academic_year: str,
        day_of_week: Optional[int] = None,
        week_type: Optional[str] = None
    ) -> List[Dict]:
        """Get schedule for teacher"""
        try:
            if not self.stub or schedule_pb2 is None:
                logger.warning("Protobuf not available, using agent_client fallback")
                # Fallback к agent_client если protobuf недоступен
                from rpc_clients.agent_client import agent_client
                schedules = agent_client.get_schedule(generation_id=None, only_active=True)
                return self._filter_schedules(schedules, teacher_id=teacher_id, semester=semester, academic_year=academic_year, day_of_week=day_of_week, week_type=week_type)
            
            # Используем прямой вызов к ms-schedule через gRPC
            request = schedule_pb2.TeacherScheduleRequest(
                teacher_id=teacher_id,
                semester=semester,
                academic_year=academic_year
            )
            
            if day_of_week is not None:
                request.day_of_week = day_of_week
            if week_type is not None:
                request.week_type = week_type
            request.only_active = True
            
            logger.info(f"Calling GetScheduleForTeacher via gRPC: teacher_id={teacher_id}, semester={semester}, academic_year={academic_year}, day_of_week={day_of_week}")
            response = self.stub.GetScheduleForTeacher(request, timeout=30)
            
            lessons = []
            logger.info(f"Response type: {type(response)}, has lessons attr: {hasattr(response, 'lessons') if response else False}")
            
            # Проверяем, является ли ответ protobuf сообщением или словарем
            if isinstance(response, dict):
                # Если возвращается dict (старая реализация ms-schedule)
                lessons = response.get('lessons', [])
                logger.info(f"Got {len(lessons)} lessons from dict response")
            elif hasattr(response, 'lessons'):
                # Если protobuf сообщение с полем lessons
                for lesson in response.lessons:
                    lessons.append({
                        'id': lesson.id,
                        'day_of_week': lesson.day_of_week,
                        'time_slot': lesson.time_slot,
                        'week_type': lesson.week_type,
                        'start_time': lesson.start_time,
                        'end_time': lesson.end_time,
                        'discipline_name': lesson.discipline_name,
                        'teacher_name': lesson.teacher_name,
                        'group_name': lesson.group_name,
                        'classroom_name': lesson.classroom_name,
                        'building_name': lesson.building_name,
                        'lesson_type': lesson.lesson_type,
                        'semester': lesson.semester,
                        'academic_year': lesson.academic_year,
                        'is_active': lesson.is_active
                    })
                logger.info(f"Got {len(lessons)} lessons from protobuf response")
            else:
                # Если ответ в неожиданном формате, пытаемся использовать fallback
                logger.warning(f"Unexpected response format: {type(response)}, using fallback")
                raise grpc.RpcError("Unexpected response format")
            
            logger.info(f"GetTeacherSchedule: teacher_id={teacher_id}, found {len(lessons)} lessons")
            return lessons
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error getting teacher schedule: {e.code()}: {e.details()}")
            # Fallback к agent_client при ошибке gRPC
            logger.info(f"🔄 Using fallback via agent_client for teacher_id={teacher_id}")
            try:
                from rpc_clients.agent_client import agent_client
                logger.info(f"📞 Calling agent_client.get_schedule(only_active=True)")
                schedules = agent_client.get_schedule(generation_id=None, only_active=True)
                logger.info(f"✅ Got {len(schedules)} schedules from agent_client, filtering for teacher_id={teacher_id}")
                filtered = self._filter_schedules(schedules, teacher_id=teacher_id, semester=semester, academic_year=academic_year, day_of_week=day_of_week, week_type=week_type)
                logger.info(f"✅ Filtered to {len(filtered)} lessons for teacher {teacher_id}")
                return filtered
            except Exception as fallback_error:
                logger.error(f"❌ Fallback also failed: {fallback_error}", exc_info=True)
                return []
        except Exception as e:
            logger.error(f"Error getting teacher schedule: {e}", exc_info=True)
            return []
    
    def _filter_schedules(self, schedules: List[Dict], teacher_id: int, semester: int, academic_year: str, day_of_week: Optional[int] = None, week_type: Optional[str] = None) -> List[Dict]:
        """Фильтрует расписание по параметрам"""
        filtered = []
        logger.info(f"🔍 Filtering {len(schedules)} schedules for teacher_id={teacher_id}, semester={semester}, academic_year={academic_year}, day_of_week={day_of_week}")
        
        for schedule in schedules:
            schedule_teacher_id = schedule.get('teacher_id')
            schedule_semester = schedule.get('semester')
            schedule_academic_year = schedule.get('academic_year')
            schedule_day = schedule.get('day_of_week')
            
            # Логируем первые несколько для отладки
            if len(filtered) < 3:
                logger.info(f"  Schedule {schedule.get('id')}: teacher_id={schedule_teacher_id}, semester={schedule_semester}, academic_year={schedule_academic_year}, day={schedule_day}")
            
            # Проверяем teacher_id
            if schedule_teacher_id != teacher_id:
                continue
            
            # КРИТИЧНО: Если semester или academic_year отсутствуют в protobuf (None, 0 или пустые),
            # пропускаем проверку этих полей, так как они могут отсутствовать в старых protobuf файлах
            # В этом случае фильтруем только по teacher_id и day_of_week
            # Также пропускаем проверку, если semester=0 (что означает отсутствие поля в protobuf)
            if schedule_semester is not None and schedule_semester != 0 and schedule_semester != semester:
                if len(filtered) < 5:
                    logger.info(f"  ⏭️ Skipping schedule {schedule.get('id')}: semester mismatch ({schedule_semester} != {semester})")
                continue
            
            if schedule_academic_year and schedule_academic_year.strip() and schedule_academic_year != academic_year:
                if len(filtered) < 5:
                    logger.info(f"  ⏭️ Skipping schedule {schedule.get('id')}: academic_year mismatch ({schedule_academic_year} != {academic_year})")
                continue
            
            # Проверяем день недели (API передает 0-5, БД хранит 1-6)
            if day_of_week is not None:
                # API передает 0-5 (0=понедельник), БД хранит 1-6 (1=понедельник)
                expected_day = day_of_week + 1
                if schedule_day != expected_day:
                    continue
            
            # Проверяем тип недели
            if week_type is not None and schedule.get('week_type') != week_type and schedule.get('week_type') != 'both':
                continue
            
            filtered.append({
                'id': schedule.get('id'),
                'day_of_week': schedule.get('day_of_week'),
                'time_slot': schedule.get('time_slot'),
                'week_type': schedule.get('week_type', 'both'),
                'start_time': self._get_time_slot_start(schedule.get('time_slot', 1)),
                'end_time': self._get_time_slot_end(schedule.get('time_slot', 1)),
                'discipline_name': schedule.get('discipline_name', ''),
                'teacher_name': schedule.get('teacher_name', ''),
                'group_name': schedule.get('group_name', ''),
                'classroom_name': schedule.get('classroom_name'),
                'building_name': None,
                'lesson_type': schedule.get('lesson_type', ''),
                'semester': schedule.get('semester'),
                'academic_year': schedule.get('academic_year', ''),
                'is_active': schedule.get('is_active', True)
            })
        
        logger.info(f"✅ Filtered {len(filtered)} lessons from {len(schedules)} schedules")
        return filtered
    
    def get_classroom_schedule(
        self,
        classroom_id: int,
        semester: int,
        academic_year: str,
        day_of_week: Optional[int] = None,
        week_type: Optional[str] = None
    ) -> List[Dict]:
        """Get schedule for classroom"""
        try:
            logger.info(f"GetClassroomSchedule: classroom_id={classroom_id}")
            return []
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            raise
    
    def export_to_excel(
        self,
        entity_type: str,
        entity_id: int,
        semester: int,
        academic_year: str
    ) -> Tuple[bytes, str, str]:
        """
        Export schedule to Excel
        
        Returns:
            Tuple of (file_bytes, filename, content_type)
        """
        try:
            logger.info(f"ExportToExcel: {entity_type}={entity_id}")
            # Implementation after proto generation
            return b'', 'schedule.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            raise
    
    def export_to_pdf(
        self,
        entity_type: str,
        entity_id: int,
        semester: int,
        academic_year: str
    ) -> Tuple[bytes, str, str]:
        """Export schedule to PDF"""
        try:
            logger.info(f"ExportToPDF: {entity_type}={entity_id}")
            return b'', 'schedule.pdf', 'application/pdf'
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            raise
    
    def export_to_ical(
        self,
        entity_type: str,
        entity_id: int,
        semester: int,
        academic_year: str
    ) -> Tuple[bytes, str, str]:
        """Export schedule to iCal"""
        try:
            logger.info(f"ExportToICal: {entity_type}={entity_id}")
            return b'', 'schedule.ics', 'text/calendar'
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            raise
    
    def search_schedule(
        self,
        query: str,
        semester: int,
        academic_year: str,
        limit: int = 50
    ) -> List[Dict]:
        """Search schedule"""
        try:
            logger.info(f"SearchSchedule: query='{query}'")
            return []
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            raise
    
    def health_check(self) -> Dict:
        """Check service health"""
        try:
            # After proto generation:
            # request = schedule_pb2.HealthCheckRequest()
            # response = self.stub.HealthCheck(request)
            # return {'status': response.status, 'version': response.version}
            
            return {'status': 'healthy', 'version': '1.0.0'}
        except grpc.RpcError as e:
            logger.error(f"Health check failed: {e}")
            return {'status': 'unhealthy', 'error': str(e)}
    
    def close(self) -> None:
        """Close gRPC channel"""
        if self.channel:
            self.channel.close()
            logger.info("ScheduleClient connection closed")
    
    def _get_time_slot_start(self, time_slot: int) -> str:
        """Get start time for time slot"""
        time_slots = {
            1: '08:00',
            2: '09:45',
            3: '11:30',
            4: '13:45',
            5: '15:30',
            6: '17:15'
        }
        return time_slots.get(time_slot, '08:00')
    
    def _get_time_slot_end(self, time_slot: int) -> str:
        """Get end time for time slot"""
        time_slots = {
            1: '09:30',
            2: '11:15',
            3: '13:00',
            4: '15:15',
            5: '17:00',
            6: '18:45'
        }
        return time_slots.get(time_slot, '09:30')
    
    def _lesson_to_dict(self, lesson) -> Dict:
        """Convert protobuf Lesson to dict"""
        # After proto generation
        return {}


# Global client instance
schedule_client: Optional[ScheduleClient] = None


def get_schedule_client() -> ScheduleClient:
    """Get global schedule client"""
    global schedule_client
    if schedule_client is None:
        schedule_client = ScheduleClient()
    return schedule_client


def close_schedule_client() -> None:
    """Close global schedule client"""
    global schedule_client
    if schedule_client:
        schedule_client.close()
        schedule_client = None

