"""
Agent RPC Client
gRPC клиент для взаимодействия с ms-agent
"""

import grpc
import logging
from typing import Optional, Dict, Any

# Import generated protobuf files from local directory
try:
    from rpc_clients.generated import agent_pb2, agent_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    agent_pb2 = None
    agent_pb2_grpc = None

from config import config

logger = logging.getLogger(__name__)


class AgentClient:
    """gRPC client for agent microservice"""
    
    def __init__(self):
        """Initialize gRPC channel and stub"""
        self.address = f'{config.MS_AGENT_HOST}:{config.MS_AGENT_PORT}'
        self.channel = None
        self.stub = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to gRPC service"""
        try:
            self.channel = grpc.insecure_channel(
                self.address,
                options=[
                    ('grpc.max_send_message_length', 100 * 1024 * 1024),
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),
                ]
            )
            
            if agent_pb2_grpc is not None:
                self.stub = agent_pb2_grpc.AgentServiceStub(self.channel)
                logger.info(f"Connected to ms-agent at {self.address}")
            else:
                logger.error("Protobuf files not found")
                
        except Exception as e:
            logger.error(f"Failed to connect to ms-agent: {e}")
            raise
    
    def generate_schedule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start schedule generation"""
        try:
            request = agent_pb2.GenerateRequest(
                semester=data['semester'],
                max_iterations=data.get('max_iterations', 100),
                skip_stage1=data.get('skip_stage1', False),
                skip_stage2=data.get('skip_stage2', False),
                created_by=data.get('created_by', 0)
            )
            response = self.stub.GenerateSchedule(request, timeout=10)
            
            if not response.success:
                return {
                    'success': False,
                    'error': response.message,
                    'job_id': response.job_id if response.job_id else ''
                }
            
            return {
                'success': response.success,
                'job_id': response.job_id,
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error generating schedule: {e}")
            raise
    
    def get_generation_status(self, job_id: str) -> Dict[str, Any]:
        """Get generation status"""
        try:
            request = agent_pb2.StatusRequest(job_id=job_id)
            response = self.stub.GetGenerationStatus(request, timeout=5)
            
            if not response.generation.job_id:
                return {'found': False}
            
            return {
                'found': True,
                'job_id': response.generation.job_id,
                'status': response.generation.status,
                'stage': response.generation.stage,
                'current_iteration': response.generation.current_iteration,
                'max_iterations': response.generation.max_iterations,
                'current_score': response.generation.current_score,
                'best_score': response.generation.best_score,
                'progress_percentage': response.progress_percentage,
                'last_reasoning': response.generation.last_reasoning
            }
            
        except grpc.RpcError as e:
            logger.error(f"RPC error getting status: {e}")
            raise
    
    def get_schedule(self, generation_id: Optional[int] = None, only_active: bool = False) -> list:
        """Get schedule"""
        try:
            request = agent_pb2.GetScheduleRequest(
                generation_id=generation_id or 0,
                only_active=only_active
            )
            response = self.stub.GetSchedule(request, timeout=10)
            
            return [self._schedule_to_dict(s) for s in response.schedules]
            
        except grpc.RpcError as e:
            logger.error(f"RPC error getting schedule: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check service health"""
        if not self.stub or agent_pb2 is None:
            return False
        try:
            request = agent_pb2.HealthCheckRequest()
            response = self.stub.HealthCheck(request, timeout=5)
            return response.status == 'healthy'
        except Exception:
            return False
    
    @staticmethod
    def _schedule_to_dict(s) -> Dict:
        """Convert protobuf Schedule to dict"""
        return {
            'id': s.id,
            'course_load_id': s.course_load_id,
            'day_of_week': s.day_of_week,
            'time_slot': s.time_slot,
            'classroom_id': s.classroom_id if s.classroom_id else None,
            'classroom_name': s.classroom_name,
            'teacher_id': s.teacher_id,
            'teacher_name': s.teacher_name,
            'group_id': s.group_id,
            'group_name': s.group_name,
            'discipline_name': s.discipline_name,
            'lesson_type': s.lesson_type
        }
    
    def close(self) -> None:
        """Close gRPC channel"""
        if self.channel:
            self.channel.close()
            logger.info("gRPC channel closed")


# Singleton instance
agent_client = AgentClient()

