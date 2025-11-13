"""
gRPC service implementation for ms-lms
"""
import logging
from datetime import datetime
import grpc

from proto.generated import lms_pb2, lms_pb2_grpc
from services.course_service import CourseService
from services.module_service import ModuleService
from services.material_service import MaterialService
from services.progress_service import ProgressService

logger = logging.getLogger(__name__)


class LMSServicer(lms_pb2_grpc.LMSServiceServicer):
    """gRPC servicer for LMS operations"""
    
    def __init__(self):
        self.course_service = CourseService()
        self.module_service = ModuleService()
        self.material_service = MaterialService()
        self.progress_service = ProgressService()
    
    def HealthCheck(self, request, context):
        """Health check endpoint"""
        return lms_pb2.HealthCheckResponse(
            status='healthy',
            version='1.0.0',
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    def CreateCourse(self, request, context):
        """Create a new course"""
        try:
            course = self.course_service.create_course(
                title=request.title,
                description=request.description,
                code=request.code,
                teacher_id=request.teacher_id,
                status=request.status or 'draft'
            )
            return lms_pb2.CourseResponse(course=course, message="Course created successfully")
        except Exception as e:
            logger.error(f"CreateCourse error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.CourseResponse()
    
    def GetCourse(self, request, context):
        """Get course by ID"""
        try:
            course = self.course_service.get_course(request.id)
            if not course:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Course {request.id} not found")
                return lms_pb2.CourseResponse()
            return lms_pb2.CourseResponse(course=course)
        except Exception as e:
            logger.error(f"GetCourse error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.CourseResponse()
    
    def ListCourses(self, request, context):
        """List courses"""
        try:
            courses, total = self.course_service.list_courses(
                page=request.page or 1,
                page_size=request.page_size or 50,
                teacher_id=request.teacher_id if request.teacher_id else None,
                status=request.status if request.status else None
            )
            return lms_pb2.CoursesListResponse(courses=courses, total_count=total)
        except Exception as e:
            logger.error(f"ListCourses error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.CoursesListResponse()
    
    def EnrollInCourse(self, request, context):
        """Enroll student in course"""
        try:
            success = self.course_service.enroll_student(
                course_id=request.course_id,
                student_id=request.student_id
            )
            return lms_pb2.EnrollResponse(
                success=success,
                message="Enrolled successfully" if success else "Already enrolled"
            )
        except Exception as e:
            logger.error(f"EnrollInCourse error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.EnrollResponse(success=False, message=str(e))
    
    def UpdateCourse(self, request, context):
        """Update course"""
        try:
            course = self.course_service.update_course(
                course_id=request.id,
                title=request.title if request.title else None,
                description=request.description if request.description else None,
                status=request.status if request.status else None
            )
            if not course:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Course {request.id} not found")
                return lms_pb2.CourseResponse()
            return lms_pb2.CourseResponse(course=course, message="Course updated successfully")
        except Exception as e:
            logger.error(f"UpdateCourse error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.CourseResponse()
    
    def DeleteCourse(self, request, context):
        """Delete course"""
        try:
            success = self.course_service.delete_course(request.id)
            return lms_pb2.DeleteResponse(
                success=success,
                message="Course deleted successfully" if success else "Course not found"
            )
        except Exception as e:
            logger.error(f"DeleteCourse error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.DeleteResponse(success=False, message=str(e))
    
    def CreateModule(self, request, context):
        """Create module"""
        try:
            module = self.module_service.create_module(
                course_id=request.course_id,
                title=request.title,
                description=request.description,
                order=request.order or 0
            )
            return lms_pb2.ModuleResponse(module=module, message="Module created successfully")
        except Exception as e:
            logger.error(f"CreateModule error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.ModuleResponse()
    
    def GetModule(self, request, context):
        """Get module by ID"""
        try:
            module = self.module_service.get_module(request.id)
            if not module:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Module {request.id} not found")
                return lms_pb2.ModuleResponse()
            return lms_pb2.ModuleResponse(module=module)
        except Exception as e:
            logger.error(f"GetModule error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.ModuleResponse()
    
    def ListModules(self, request, context):
        """List modules for course"""
        try:
            modules = self.module_service.list_modules(request.course_id)
            return lms_pb2.ModulesListResponse(modules=modules, total_count=len(modules))
        except Exception as e:
            logger.error(f"ListModules error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.ModulesListResponse()
    
    def UpdateModule(self, request, context):
        """Update module"""
        try:
            module = self.module_service.update_module(
                module_id=request.id,
                title=request.title if request.title else None,
                description=request.description if request.description else None,
                order=request.order if request.order else None
            )
            if not module:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Module {request.id} not found")
                return lms_pb2.ModuleResponse()
            return lms_pb2.ModuleResponse(module=module, message="Module updated successfully")
        except Exception as e:
            logger.error(f"UpdateModule error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.ModuleResponse()
    
    def DeleteModule(self, request, context):
        """Delete module"""
        try:
            success = self.module_service.delete_module(request.id)
            return lms_pb2.DeleteResponse(
                success=success,
                message="Module deleted successfully" if success else "Module not found"
            )
        except Exception as e:
            logger.error(f"DeleteModule error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.DeleteResponse(success=False, message=str(e))
    
    def AddMaterial(self, request, context):
        """Add material to module"""
        try:
            material = self.material_service.add_material(
                module_id=request.module_id,
                title=request.title,
                type=request.type,
                content=request.content or '',
                file_path=request.file_path or '',
                order=request.order or 0
            )
            return lms_pb2.MaterialResponse(material=material, message="Material added successfully")
        except Exception as e:
            logger.error(f"AddMaterial error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.MaterialResponse()
    
    def ListMaterials(self, request, context):
        """List materials for module"""
        try:
            materials = self.material_service.list_materials(request.module_id)
            return lms_pb2.MaterialsListResponse(materials=materials, total_count=len(materials))
        except Exception as e:
            logger.error(f"ListMaterials error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.MaterialsListResponse()
    
    def GetMaterial(self, request, context):
        """Get material by ID"""
        try:
            material = self.material_service.get_material(request.id)
            if not material:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Material {request.id} not found")
                return lms_pb2.MaterialResponse()
            return lms_pb2.MaterialResponse(material=material)
        except Exception as e:
            logger.error(f"GetMaterial error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.MaterialResponse()
    
    def DeleteMaterial(self, request, context):
        """Delete material"""
        try:
            success = self.material_service.delete_material(request.id)
            return lms_pb2.DeleteResponse(
                success=success,
                message="Material deleted successfully" if success else "Material not found"
            )
        except Exception as e:
            logger.error(f"DeleteMaterial error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.DeleteResponse(success=False, message=str(e))
    
    def GetProgress(self, request, context):
        """Get student progress"""
        try:
            progress = self.progress_service.get_progress(
                student_id=request.student_id,
                course_id=request.course_id
            )
            return progress or lms_pb2.ProgressResponse(overall_progress=0.0, message="No progress found")
        except Exception as e:
            logger.error(f"GetProgress error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.ProgressResponse()
    
    def UpdateProgress(self, request, context):
        """Update student progress"""
        try:
            self.progress_service.update_progress(
                student_id=request.student_id,
                course_id=request.course_id,
                module_id=request.module_id,
                completed=request.completed
            )
            return lms_pb2.ProgressResponse(overall_progress=0.0, message="Progress updated successfully")
        except Exception as e:
            logger.error(f"UpdateProgress error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.ProgressResponse()
    
    def GetStudentCourses(self, request, context):
        """Get courses for student"""
        try:
            courses, total = self.course_service.get_student_courses(request.student_id)
            return lms_pb2.CoursesListResponse(courses=courses, total_count=total)
        except Exception as e:
            logger.error(f"GetStudentCourses error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return lms_pb2.CoursesListResponse()

