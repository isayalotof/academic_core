"""
Classroom RPC Client
gRPC клиент для взаимодействия с ms-audit
"""

import grpc
import logging
from typing import Optional, Dict, Any, List

# Import generated protobuf files from local directory
try:
    from rpc_clients.generated import classroom_pb2, classroom_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    classroom_pb2 = None
    classroom_pb2_grpc = None

from config import config

logger = logging.getLogger(__name__)


class ClassroomClient:
    """gRPC client for classroom microservice"""
    
    def __init__(self):
        """Initialize gRPC channel and stub"""
        self.address = f'{config.MS_AUDIT_HOST}:{config.MS_AUDIT_PORT}'
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
            
            if classroom_pb2_grpc is not None:
                self.stub = classroom_pb2_grpc.ClassroomServiceStub(self.channel)
                logger.info(f"Connected to ms-audit at {self.address}")
            else:
                logger.error("Protobuf files not found")
                
        except Exception as e:
            logger.error(f"Failed to connect to ms-audit: {e}")
            raise
    
    def create_classroom(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new classroom"""
        try:
            request = classroom_pb2.CreateClassroomRequest(**data)
            response = self.stub.CreateClassroom(request, timeout=10)
            
            return {
                'success': response.classroom.id > 0,
                'classroom': self._classroom_to_dict(response.classroom),
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error creating classroom: {e}")
            raise
    
    def get_classroom(
        self, 
        classroom_id: Optional[int] = None, 
        code: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get classroom by ID or code"""
        try:
            if classroom_id:
                request = classroom_pb2.GetClassroomRequest(id=classroom_id)
            elif code:
                request = classroom_pb2.GetClassroomRequest(code=code)
            else:
                raise ValueError("Either classroom_id or code must be provided")
            
            response = self.stub.GetClassroom(request, timeout=10)
            
            if response.classroom.id:
                return self._classroom_to_dict(response.classroom)
            return None
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            logger.error(f"RPC error getting classroom: {e}")
            raise
    
    def update_classroom(
        self, 
        classroom_id: int, 
        updates: Dict[str, str]
    ) -> Dict[str, Any]:
        """Update classroom"""
        try:
            request = classroom_pb2.UpdateClassroomRequest(
                id=classroom_id,
                updates=updates
            )
            response = self.stub.UpdateClassroom(request, timeout=10)
            
            return {
                'success': response.classroom.id > 0,
                'classroom': self._classroom_to_dict(response.classroom),
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error updating classroom: {e}")
            raise
    
    def delete_classroom(
        self, 
        classroom_id: int, 
        hard_delete: bool = False
    ) -> Dict[str, Any]:
        """Delete classroom"""
        try:
            request = classroom_pb2.DeleteClassroomRequest(
                id=classroom_id,
                hard_delete=hard_delete
            )
            response = self.stub.DeleteClassroom(request, timeout=10)
            
            return {
                'success': response.success,
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error deleting classroom: {e}")
            raise
    
    def list_classrooms(
        self,
        page: int = 1,
        page_size: int = 20,
        search_query: Optional[str] = None,
        building_ids: Optional[List[int]] = None,
        classroom_types: Optional[List[str]] = None,
        min_capacity: Optional[int] = None,
        max_capacity: Optional[int] = None,
        sort_by: str = 'name',
        sort_order: str = 'ASC'
    ) -> Dict[str, Any]:
        """List classrooms with filters"""
        try:
            request = classroom_pb2.ListClassroomsRequest(
                page=page,
                page_size=page_size,
                search_query=search_query or '',
                building_ids=building_ids or [],
                classroom_types=classroom_types or [],
                min_capacity=min_capacity or 0,
                max_capacity=max_capacity or 0,
                sort_by=sort_by,
                sort_order=sort_order
            )
            response = self.stub.ListClassrooms(request, timeout=30)
            
            return {
                'classrooms': [
                    self._classroom_to_dict(c) for c in response.classrooms
                ],
                'total_count': response.total_count,
                'page': response.page,
                'page_size': response.page_size
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error listing classrooms: {e}")
            raise
    
    def find_available_classrooms(
        self,
        day_of_week: int,
        time_slot: int,
        min_capacity: int = 1,
        need_projector: bool = False,
        need_whiteboard: bool = False,
        need_computers: bool = False,
        building_ids: Optional[List[int]] = None,
        classroom_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Find available classrooms"""
        try:
            request = classroom_pb2.FindAvailableRequest(
                day_of_week=day_of_week,
                time_slot=time_slot,
                min_capacity=min_capacity,
                need_projector=need_projector,
                need_whiteboard=need_whiteboard,
                need_computers=need_computers,
                building_ids=building_ids or [],
                classroom_types=classroom_types or []
            )
            response = self.stub.FindAvailableClassrooms(request, timeout=30)
            
            return [
                {
                    'classroom': self._classroom_to_dict(ac.classroom),
                    'utilization_score': ac.utilization_score,
                    'fully_equipped': ac.fully_equipped
                }
                for ac in response.classrooms
            ]
            
        except grpc.RpcError as e:
            logger.error(f"RPC error finding available classrooms: {e}")
            raise
    
    def check_availability(
        self, 
        classroom_id: int, 
        day_of_week: int, 
        time_slot: int
    ) -> Dict[str, Any]:
        """Check classroom availability"""
        try:
            request = classroom_pb2.CheckAvailabilityRequest(
                classroom_id=classroom_id,
                day_of_week=day_of_week,
                time_slot=time_slot
            )
            response = self.stub.CheckAvailability(request, timeout=10)
            
            return {
                'is_available': response.is_available,
                'reason': response.reason
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error checking availability: {e}")
            raise
    
    def reserve_classroom(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reserve a classroom"""
        try:
            request = classroom_pb2.ReserveRequest(**data)
            response = self.stub.ReserveClassroom(request, timeout=10)
            
            return {
                'success': response.success,
                'schedule_id': response.schedule_id,
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error reserving classroom: {e}")
            raise
    
    def get_schedule(
        self, 
        classroom_id: int, 
        days_of_week: Optional[List[int]] = None,
        week: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get classroom schedule"""
        try:
            request = classroom_pb2.GetScheduleRequest(
                classroom_id=classroom_id,
                days_of_week=days_of_week or [],
                week=week if week else 0  # 0 = все недели
            )
            response = self.stub.GetSchedule(request, timeout=10)
            
            return {
                'classroom_id': response.classroom_id,
                'slots': [
                    {
                        'day_of_week': s.day_of_week,
                        'time_slot': s.time_slot,
                        'week': s.week,
                        'discipline_name': s.discipline_name,
                        'teacher_name': s.teacher_name,
                        'group_name': s.group_name,
                        'lesson_type': s.lesson_type
                    }
                    for s in response.slots
                ],
                'total_occupied': response.total_occupied,
                'utilization_percentage': response.utilization_percentage
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error getting schedule: {e}")
            raise
    
    def get_statistics(
        self, 
        classroom_id: Optional[int] = None, 
        building_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get statistics"""
        try:
            if classroom_id:
                request = classroom_pb2.StatisticsRequest(classroom_id=classroom_id)
            elif building_id:
                request = classroom_pb2.StatisticsRequest(building_id=building_id)
            else:
                request = classroom_pb2.StatisticsRequest(all=True)
            
            response = self.stub.GetStatistics(request, timeout=10)
            
            return {
                'total_classrooms': response.total_classrooms,
                'total_capacity': response.total_capacity,
                'average_utilization': response.average_utilization,
                'by_type': dict(response.by_type)
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error getting statistics: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check service health"""
        if not self.stub or classroom_pb2 is None:
            return False
        try:
            request = classroom_pb2.HealthCheckRequest()
            response = self.stub.HealthCheck(request, timeout=5)
            return response.status == 'healthy'
        except Exception:
            return False
    
    @staticmethod
    def _classroom_to_dict(classroom) -> Dict[str, Any]:
        """Convert protobuf Classroom to dict"""
        return {
            'id': classroom.id,
            'name': classroom.name,
            'code': classroom.code,
            'building_id': classroom.building_id,
            'building_name': classroom.building_name,
            'floor': classroom.floor,
            'wing': classroom.wing,
            'capacity': classroom.capacity,
            'actual_area': classroom.actual_area,
            'classroom_type': classroom.classroom_type,
            'has_projector': classroom.has_projector,
            'has_whiteboard': classroom.has_whiteboard,
            'has_blackboard': classroom.has_blackboard,
            'has_markers': classroom.has_markers,
            'has_chalk': classroom.has_chalk,
            'has_computers': classroom.has_computers,
            'computers_count': classroom.computers_count,
            'has_audio_system': classroom.has_audio_system,
            'has_video_recording': classroom.has_video_recording,
            'has_air_conditioning': classroom.has_air_conditioning,
            'is_accessible': classroom.is_accessible,
            'has_windows': classroom.has_windows,
            'is_active': classroom.is_active,
            'description': classroom.description,
            'notes': classroom.notes,
            'created_at': classroom.created_at,
            'updated_at': classroom.updated_at
        }
    
    # ============ BUILDINGS ============
    
    def create_building(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать здание"""
        try:
            # Убираем поля, которых нет в proto
            proto_fields = {
                'name', 'short_name', 'code', 'address', 'campus',
                'latitude', 'longitude', 'total_floors', 'has_elevator'
            }
            filtered_data = {k: v for k, v in building_data.items() if k in proto_fields}
            
            logger.info(f"Creating building with filtered data: {filtered_data}")
            request = classroom_pb2.CreateBuildingRequest(**filtered_data)
            response = self.stub.CreateBuilding(request, timeout=10)
            
            if not response.building:
                raise Exception("Failed to create building: empty response")
            
            return self._building_to_dict(response.building)
            
        except grpc.RpcError as e:
            logger.error(f"RPC error creating building: {e.code()} - {e.details()}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error creating building: {e}", exc_info=True)
            raise
    
    def get_building(self, building_id: int) -> Dict[str, Any]:
        """Получить здание по ID"""
        try:
            request = classroom_pb2.GetBuildingRequest(
                building_id=building_id
            )
            response = self.stub.GetBuilding(request, timeout=10)
            
            if not response.building:
                return None
            
            return self._building_to_dict(response.building)
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            logger.error(f"RPC error getting building: {e}")
            raise
    
    def list_buildings(self) -> Dict[str, Any]:
        """Получить список зданий"""
        try:
            request = classroom_pb2.ListBuildingsRequest()
            response = self.stub.ListBuildings(request, timeout=10)
            
            buildings = [
                self._building_to_dict(b) for b in response.buildings
            ]
            
            return {
                'buildings': buildings,
                'total_count': response.total_count
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error listing buildings: {e}")
            raise
    
    def update_building(
        self,
        building_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновить здание"""
        try:
            # Build request with building_id and update fields
            request_data = {'building_id': building_id}
            request_data.update(updates)
            
            request = classroom_pb2.UpdateBuildingRequest(**request_data)
            response = self.stub.UpdateBuilding(request, timeout=10)
            
            if not response.building:
                raise Exception("Failed to update building")
            
            return self._building_to_dict(response.building)
            
        except grpc.RpcError as e:
            logger.error(f"RPC error updating building: {e}")
            raise
    
    def delete_building(self, building_id: int) -> bool:
        """Удалить здание"""
        try:
            request = classroom_pb2.DeleteBuildingRequest(
                building_id=building_id
            )
            response = self.stub.DeleteBuilding(request, timeout=10)
            
            return response.success
            
        except grpc.RpcError as e:
            logger.error(f"RPC error deleting building: {e}")
            raise
    
    def _building_to_dict(self, building) -> Dict[str, Any]:
        """Convert Building protobuf to dict"""
        return {
            'id': building.id,
            'name': building.name,
            'short_name': building.short_name,
            'code': building.code,
            'address': building.address,
            'campus': building.campus,
            'latitude': building.latitude,
            'longitude': building.longitude,
            'total_floors': building.total_floors,
            'has_elevator': building.has_elevator,
            'created_at': building.created_at,
            'updated_at': building.updated_at
        }
    
    def close(self) -> None:
        """Close gRPC channel"""
        if self.channel:
            self.channel.close()
            logger.info("gRPC channel closed")


# Singleton instance
classroom_client = ClassroomClient()

