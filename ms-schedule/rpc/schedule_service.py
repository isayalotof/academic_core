"""
gRPC Schedule Service Implementation
Реализация ScheduleService из protobuf
"""

import grpc
from concurrent import futures
import logging
from typing import Dict

# Import generated protobuf code (will be generated)
# from proto.generated import schedule_pb2
# from proto.generated import schedule_pb2_grpc

from services.view_service import view_service
from services.export_service import export_service
from utils.metrics import schedule_operations_total
from datetime import datetime

logger = logging.getLogger(__name__)


class ScheduleServicer:
    """
    gRPC ScheduleService implementation
    
    NOTE: This is a template. After proto generation, uncomment imports and inherit from:
          schedule_pb2_grpc.ScheduleServiceServicer
    """
    
    def __init__(self):
        """Initialize Schedule servicer"""
        logger.info("ScheduleServicer initialized")
    
    # ============ VIEW METHODS ============
    
    def GetScheduleForGroup(self, request, context):
        """Get schedule for group"""
        try:
            logger.info(f"GetScheduleForGroup: group_id={request.group_id}")
            
            lessons = view_service.get_group_schedule(
                group_id=request.group_id,
                semester=request.semester,
                academic_year=request.academic_year,
                day_of_week=request.day_of_week if request.day_of_week else None,
                week_type=request.week_type if request.week_type else None,
                only_active=request.only_active if request.HasField('only_active') else True
            )
            
            # Convert to protobuf (after generation)
            # return self._build_schedule_response(lessons)
            
            return {'lessons': lessons, 'total_count': len(lessons)}
            
        except Exception as e:
            logger.error(f"GetScheduleForGroup error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None
    
    def GetScheduleForTeacher(self, request, context):
        """Get schedule for teacher"""
        try:
            logger.info(f"GetScheduleForTeacher: teacher_id={request.teacher_id}")
            
            lessons = view_service.get_teacher_schedule(
                teacher_id=request.teacher_id,
                semester=request.semester,
                academic_year=request.academic_year,
                day_of_week=request.day_of_week if request.day_of_week else None,
                week_type=request.week_type if request.week_type else None,
                only_active=request.only_active if request.HasField('only_active') else True
            )
            
            return {'lessons': lessons, 'total_count': len(lessons)}
            
        except Exception as e:
            logger.error(f"GetScheduleForTeacher error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None
    
    def GetScheduleForClassroom(self, request, context):
        """Get schedule for classroom"""
        try:
            logger.info(f"GetScheduleForClassroom: classroom_id={request.classroom_id}")
            
            lessons = view_service.get_classroom_schedule(
                classroom_id=request.classroom_id,
                semester=request.semester,
                academic_year=request.academic_year,
                day_of_week=request.day_of_week if request.day_of_week else None,
                week_type=request.week_type if request.week_type else None,
                only_active=request.only_active if request.HasField('only_active') else True
            )
            
            return {'lessons': lessons, 'total_count': len(lessons)}
            
        except Exception as e:
            logger.error(f"GetScheduleForClassroom error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None
    
    # ============ EXPORT METHODS ============
    
    def ExportToExcel(self, request, context):
        """Export schedule to Excel"""
        try:
            logger.info("ExportToExcel request")
            
            # Determine entity type
            if request.HasField('group_id'):
                file_bytes, filename = export_service.export_group_to_excel(
                    group_id=request.group_id,
                    group_name=f"Group_{request.group_id}",  # Should get from DB
                    semester=request.semester,
                    academic_year=request.academic_year
                )
            elif request.HasField('teacher_id'):
                file_bytes, filename = export_service.export_teacher_to_excel(
                    teacher_id=request.teacher_id,
                    teacher_name=f"Teacher_{request.teacher_id}",
                    semester=request.semester,
                    academic_year=request.academic_year
                )
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Either group_id or teacher_id must be specified")
                return None
            
            return {
                'success': True,
                'file_data': file_bytes,
                'filename': filename,
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            
        except Exception as e:
            logger.error(f"ExportToExcel error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None
    
    def ExportToPDF(self, request, context):
        """Export schedule to PDF"""
        try:
            logger.info("ExportToPDF request")
            
            if request.HasField('group_id'):
                file_bytes, filename = export_service.export_group_to_pdf(
                    group_id=request.group_id,
                    group_name=f"Group_{request.group_id}",
                    semester=request.semester,
                    academic_year=request.academic_year
                )
            elif request.HasField('teacher_id'):
                file_bytes, filename = export_service.export_teacher_to_pdf(
                    teacher_id=request.teacher_id,
                    teacher_name=f"Teacher_{request.teacher_id}",
                    semester=request.semester,
                    academic_year=request.academic_year
                )
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Either group_id or teacher_id must be specified")
                return None
            
            return {
                'success': True,
                'file_data': file_bytes,
                'filename': filename,
                'content_type': 'application/pdf'
            }
            
        except Exception as e:
            logger.error(f"ExportToPDF error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None
    
    def ExportToICal(self, request, context):
        """Export schedule to iCal"""
        try:
            logger.info("ExportToICal request")
            
            # Determine entity
            if request.HasField('group_id'):
                entity_type = 'group'
                entity_id = request.group_id
                entity_name = f"Group_{request.group_id}"
            elif request.HasField('teacher_id'):
                entity_type = 'teacher'
                entity_id = request.teacher_id
                entity_name = f"Teacher_{request.teacher_id}"
            elif request.HasField('classroom_id'):
                entity_type = 'classroom'
                entity_id = request.classroom_id
                entity_name = f"Classroom_{request.classroom_id}"
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Entity ID must be specified")
                return None
            
            # For now, use fixed dates (should be passed in request or from config)
            start_date = datetime(2024, 9, 1)
            end_date = datetime(2024, 12, 31)
            
            file_bytes, filename = export_service.export_to_ical(
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name,
                semester=request.semester,
                academic_year=request.academic_year,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                'success': True,
                'file_data': file_bytes,
                'filename': filename,
                'content_type': 'text/calendar'
            }
            
        except Exception as e:
            logger.error(f"ExportToICal error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None
    
    # ============ SEARCH ============
    
    def SearchSchedule(self, request, context):
        """Search schedule"""
        try:
            logger.info(f"SearchSchedule: query='{request.query}'")
            
            results = view_service.search_schedule(
                query=request.query,
                semester=request.semester,
                academic_year=request.academic_year,
                limit=request.limit if request.limit else 50
            )
            
            return {'lessons': results, 'total_count': len(results)}
            
        except Exception as e:
            logger.error(f"SearchSchedule error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None
    
    # ============ HEALTH CHECK ============
    
    def HealthCheck(self, request, context):
        """Health check"""
        from config import config
        
        return {
            'status': 'healthy',
            'version': config.SERVICE_VERSION
        }
    
    # ============ HELPER METHODS ============
    
    def _build_lesson_message(self, lesson: Dict):
        """Convert DB lesson to protobuf message"""
        # After proto generation, build actual message
        # return schedule_pb2.Lesson(...)
        return lesson
    
    def _build_schedule_response(self, lessons: list):
        """Build ScheduleResponse"""
        # After proto generation
        # return schedule_pb2.ScheduleResponse(
        #     lessons=[self._build_lesson_message(l) for l in lessons],
        #     total_count=len(lessons)
        # )
        return {'lessons': lessons, 'total_count': len(lessons)}


# Global servicer instance
schedule_servicer = ScheduleServicer()

