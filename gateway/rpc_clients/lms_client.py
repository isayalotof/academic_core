"""
LMS RPC Client для Gateway
Подключение к ms-lms
"""
import grpc
import logging
from typing import Optional, Dict, Any, List
import os

try:
    from rpc_clients.generated import lms_pb2, lms_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    lms_pb2 = None
    lms_pb2_grpc = None

logger = logging.getLogger(__name__)


class LMSClient:
    """RPC клиент для ms-lms"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.getenv('MS_LMS_HOST', 'localhost')
        self.port = port or int(os.getenv('MS_LMS_PORT', 50061))
        self.address = f'{self.host}:{self.port}'
        
        self.channel = grpc.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ]
        )
        
        if lms_pb2_grpc:
            self.stub = lms_pb2_grpc.LMSServiceStub(self.channel)
            logger.info(f"LMSClient initialized: {self.address}")
        else:
            self.stub = None
            logger.warning("Proto files not available")
    
    def list_courses(self, page: int = 1, page_size: int = 50,
                    teacher_id: Optional[int] = None,
                    status: Optional[str] = None) -> Dict[str, Any]:
        """Список курсов"""
        if not self.stub:
            raise Exception("LMS service not available")
        
        request = lms_pb2.ListCoursesRequest(
            page=page,
            page_size=page_size,
            teacher_id=teacher_id or 0,
            status=status or ''
        )
        
        response = self.stub.ListCourses(request, timeout=10)
        
        courses = []
        for course in response.courses:
            courses.append({
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'code': course.code,
                'teacher_id': course.teacher_id or 0,
                'teacher_name': course.teacher_name,
                'status': course.status,
                'enrolled_count': course.enrolled_count,
                'created_at': course.created_at,
                'updated_at': course.updated_at
            })
        
        return {
            'courses': courses,
            'total_count': response.total_count
        }
    
    def get_course(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Получить курс по ID"""
        if not self.stub:
            raise Exception("LMS service not available")
        
        request = lms_pb2.GetCourseRequest(id=course_id)
        response = self.stub.GetCourse(request, timeout=10)
        
        if not response.course.id:
            return None
        
        return {
            'id': response.course.id,
            'title': response.course.title,
            'description': response.course.description,
            'code': response.course.code,
            'teacher_id': response.course.teacher_id or 0,
            'teacher_name': response.course.teacher_name,
            'status': response.course.status,
            'enrolled_count': response.course.enrolled_count,
            'created_at': response.course.created_at,
            'updated_at': response.course.updated_at
        }
    
    def enroll_in_course(self, course_id: int, student_id: int) -> Dict[str, Any]:
        """Записаться на курс"""
        if not self.stub:
            raise Exception("LMS service not available")
        
        request = lms_pb2.EnrollRequest(course_id=course_id, student_id=student_id)
        response = self.stub.EnrollInCourse(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message
        }
    
    def list_modules(self, course_id: int) -> List[Dict[str, Any]]:
        """Список модулей курса"""
        if not self.stub:
            raise Exception("LMS service not available")
        
        request = lms_pb2.ListModulesRequest(course_id=course_id)
        response = self.stub.ListModules(request, timeout=10)
        
        modules = []
        for module in response.modules:
            modules.append({
                'id': module.id,
                'course_id': module.course_id,
                'title': module.title,
                'description': module.description,
                'order': module.order,
                'created_at': module.created_at,
                'updated_at': module.updated_at
            })
        
        return modules
    
    def list_materials(self, module_id: int) -> List[Dict[str, Any]]:
        """Список материалов модуля"""
        if not self.stub:
            raise Exception("LMS service not available")
        
        request = lms_pb2.ListMaterialsRequest(module_id=module_id)
        response = self.stub.ListMaterials(request, timeout=10)
        
        materials = []
        for material in response.materials:
            materials.append({
                'id': material.id,
                'module_id': material.module_id,
                'title': material.title,
                'type': material.type,
                'content': material.content,
                'file_path': material.file_path,
                'order': material.order,
                'created_at': material.created_at
            })
        
        return materials
    
    def get_progress(self, student_id: int, course_id: int) -> Dict[str, Any]:
        """Получить прогресс студента"""
        if not self.stub:
            raise Exception("LMS service not available")
        
        request = lms_pb2.GetProgressRequest(student_id=student_id, course_id=course_id)
        response = self.stub.GetProgress(request, timeout=10)
        
        return {
            'overall_progress': response.overall_progress,
            'message': response.message
        }
    
    def get_student_courses(self, student_id: int) -> Dict[str, Any]:
        """Получить курсы студента"""
        if not self.stub:
            raise Exception("LMS service not available")
        
        request = lms_pb2.GetStudentCoursesRequest(student_id=student_id)
        response = self.stub.GetStudentCourses(request, timeout=10)
        
        courses = []
        for course in response.courses:
            courses.append({
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'code': course.code,
                'teacher_id': course.teacher_id or 0,
                'teacher_name': course.teacher_name,
                'status': course.status,
                'enrolled_count': course.enrolled_count,
                'created_at': course.created_at,
                'updated_at': course.updated_at
            })
        
        return {
            'courses': courses,
            'total_count': response.total_count
        }


_lms_client: Optional[LMSClient] = None


def get_lms_client() -> LMSClient:
    """Get singleton LMS client"""
    global _lms_client
    if _lms_client is None:
        _lms_client = LMSClient()
    return _lms_client

