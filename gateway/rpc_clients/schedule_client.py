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
            # After proto generation:
            # request = schedule_pb2.GroupScheduleRequest(
            #     group_id=group_id,
            #     semester=semester,
            #     academic_year=academic_year,
            #     day_of_week=day_of_week,
            #     week_type=week_type,
            #     only_active=True
            # )
            # response = self.stub.GetScheduleForGroup(request)
            # return [self._lesson_to_dict(lesson) for lesson in response.lessons]
            
            # Placeholder
            logger.info(f"GetGroupSchedule: group_id={group_id}")
            return []
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            raise
    
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
            logger.info(f"GetTeacherSchedule: teacher_id={teacher_id}")
            # Implementation after proto generation
            return []
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            raise
    
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

