"""
⭐ Core Service Implementation - gRPC Servicer
Главный компонент ms-core
"""
import logging
from datetime import datetime

import grpc
import psycopg2.errors
from proto.generated import core_pb2, core_pb2_grpc

from services.teacher_service import TeacherService
from services.preference_service import PreferenceService
from services.group_service import GroupService
from services.student_service import StudentService
from services.load_service import LoadService
from utils.metrics import rpc_requests_total, rpc_request_duration
from utils.logger import get_logger

logger = get_logger('core_service')


class CoreServicer(core_pb2_grpc.CoreServiceServicer):
    """gRPC Servicer для CoreService"""
    
    def __init__(self):
        self.teacher_service = TeacherService()
        self.preference_service = PreferenceService()
        self.group_service = GroupService()
        self.student_service = StudentService()
        self.load_service = LoadService()
        logger.info("CoreServicer initialized")
    
    # ============ TEACHERS ============
    
    def CreateTeacher(self, request, context):
        """Создать преподавателя"""
        try:
            with rpc_request_duration.labels(method='CreateTeacher').time():
                teacher_data = {
                    'full_name': request.full_name,
                    'first_name': request.first_name or None,
                    'last_name': request.last_name or None,
                    'middle_name': request.middle_name or None,
                    'email': request.email or None,
                    'phone': request.phone or None,
                    'employment_type': request.employment_type,
                    'position': request.position or None,
                    'academic_degree': request.academic_degree or None,
                    'department': request.department or None,
                    'hire_date': request.hire_date or None,
                    'created_by': request.created_by or None
                }
                
                result = self.teacher_service.create_teacher(teacher_data)
                
                teacher = self._build_teacher_message(result)
                
                rpc_requests_total.labels(method='CreateTeacher', status='success').inc()
                
                return core_pb2.TeacherResponse(
                    teacher=teacher,
                    message="Teacher created successfully"
                )
                
        except Exception as e:
            logger.error(f"CreateTeacher error: {e}", exc_info=True)
            rpc_requests_total.labels(method='CreateTeacher', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.TeacherResponse()
    
    def GetTeacher(self, request, context):
        """Получить преподавателя"""
        try:
            with rpc_request_duration.labels(method='GetTeacher').time():
                # Определить тип идентификатора
                teacher_id = None
                email = None
                user_id = None
                
                if request.HasField('id'):
                    teacher_id = request.id
                elif request.HasField('email'):
                    email = request.email
                elif request.HasField('user_id'):
                    user_id = request.user_id
                
                result = self.teacher_service.get_teacher(
                    teacher_id=teacher_id,
                    email=email,
                    user_id=user_id,
                    include_preferences=request.include_preferences
                )
                
                if not result:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Teacher not found")
                    return core_pb2.TeacherResponse()
                
                teacher = self._build_teacher_message(result)
                
                rpc_requests_total.labels(method='GetTeacher', status='success').inc()
                
                return core_pb2.TeacherResponse(
                    teacher=teacher,
                    message="Teacher retrieved successfully"
                )
                
        except Exception as e:
            logger.error(f"GetTeacher error: {e}", exc_info=True)
            rpc_requests_total.labels(method='GetTeacher', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.TeacherResponse()
    
    def ListTeachers(self, request, context):
        """Получить список преподавателей"""
        try:
            with rpc_request_duration.labels(method='ListTeachers').time():
                result = self.teacher_service.list_teachers(
                    page=request.page or 1,
                    page_size=request.page_size or 50,
                    employment_types=list(request.employment_types) if request.employment_types else None,
                    priorities=list(request.priorities) if request.priorities else None,
                    department=request.department if request.department else None,
                    only_active=request.only_active if request.only_active else False,
                    sort_by=request.sort_by if request.sort_by else 'created_at',
                    sort_order=request.sort_order if request.sort_order else 'DESC'
                )
                
                teachers = []
                for teacher_data in result['teachers']:
                    teachers.append(self._build_teacher_message(teacher_data))
                
                rpc_requests_total.labels(method='ListTeachers', status='success').inc()
                
                return core_pb2.TeachersListResponse(
                    teachers=teachers,
                    total_count=result['total_count'],
                    page=result['page'],
                    page_size=result['page_size']
                )
                
        except Exception as e:
            logger.error(f"ListTeachers error: {e}", exc_info=True)
            rpc_requests_total.labels(method='ListTeachers', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.TeachersListResponse()
    
    # ============ PREFERENCES ⭐ KEY FEATURE! ============
    
    def GetTeacherPreferences(self, request, context):
        """Получить предпочтения преподавателя"""
        try:
            with rpc_request_duration.labels(method='GetTeacherPreferences').time():
                result = self.preference_service.get_teacher_preferences(request.teacher_id)
                
                # Build response
                preferences = []
                for pref in result['preferences']:
                    preferences.append(core_pb2.TeacherPreference(
                        id=pref['id'],
                        teacher_id=result['teacher_id'],
                        day_of_week=pref['day_of_week'],
                        time_slot=pref['time_slot'],
                        is_preferred=pref['is_preferred'],
                        preference_strength=pref.get('preference_strength', ''),
                        reason=pref.get('reason', '')
                    ))
                
                rpc_requests_total.labels(method='GetTeacherPreferences', status='success').inc()
                
                return core_pb2.PreferencesResponse(
                    teacher_id=result['teacher_id'],
                    teacher_name=result.get('teacher_name', ''),
                    teacher_priority=result.get('teacher_priority', 4),
                    preferences=preferences,
                    total_preferences=result['total_preferences'],
                    preferred_count=result['preferred_count'],
                    not_preferred_count=result['not_preferred_count'],
                    coverage_percentage=result['coverage_percentage']
                )
                
        except Exception as e:
            logger.error(f"GetTeacherPreferences error: {e}", exc_info=True)
            rpc_requests_total.labels(method='GetTeacherPreferences', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.PreferencesResponse()
    
    def SetTeacherPreferences(self, request, context):
        """⭐ Установить предпочтения преподавателя"""
        try:
            with rpc_request_duration.labels(method='SetTeacherPreferences').time():
                # Преобразовать предпочтения
                preferences = []
                for pref in request.preferences:
                    preferences.append({
                        'day_of_week': pref.day_of_week,
                        'time_slot': pref.time_slot,
                        'is_preferred': pref.is_preferred,
                        'preference_strength': pref.preference_strength or '',
                        'reason': pref.reason or ''
                    })
                
                result = self.preference_service.set_teacher_preferences(
                    teacher_id=request.teacher_id,
                    preferences=preferences,
                    replace_existing=request.replace_existing
                )
                
                rpc_requests_total.labels(method='SetTeacherPreferences', status='success').inc()
                
                return core_pb2.SetPreferencesResponse(
                    success=result['success'],
                    created_count=result['created_count'],
                    updated_count=result['updated_count'],
                    deleted_count=result['deleted_count'],
                    message=result['message']
                )
                
        except Exception as e:
            logger.error(f"SetTeacherPreferences error: {e}", exc_info=True)
            rpc_requests_total.labels(method='SetTeacherPreferences', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.SetPreferencesResponse(success=False)
    
    def GetAllPreferences(self, request, context):
        """
        ⭐⭐⭐ KEY METHOD ДЛЯ MS-AGENT!!!
        Получить ВСЕ предпочтения преподавателей для fitness-функции
        """
        try:
            with rpc_request_duration.labels(method='GetAllPreferences').time():
                logger.info(
                    f"GetAllPreferences called: semester={request.semester}, "
                    f"year={request.academic_year}, teachers={len(request.teacher_ids)}"
                )
                
                # Получить предпочтения
                result = self.preference_service.get_all_preferences(
                    semester=request.semester or None,
                    academic_year=request.academic_year or None,
                    teacher_ids=list(request.teacher_ids) if request.teacher_ids else None
                )
                
                # Build response
                preferences_sets = []
                for teacher_data in result:
                    # Преобразовать предпочтения
                    prefs = []
                    for pref in teacher_data['preferences']:
                        prefs.append(core_pb2.TeacherPreference(
                            id=pref['id'],
                            teacher_id=teacher_data['teacher_id'],
                            day_of_week=pref['day_of_week'],
                            time_slot=pref['time_slot'],
                            is_preferred=pref['is_preferred'],
                            preference_strength=pref.get('preference_strength', '')
                        ))
                    
                    # Добавить набор предпочтений преподавателя
                    preferences_sets.append(core_pb2.TeacherPreferencesSet(
                        teacher_id=teacher_data['teacher_id'],
                        teacher_name=teacher_data['teacher_name'],
                        teacher_priority=teacher_data['teacher_priority'],
                        preferences=prefs
                    ))
                
                rpc_requests_total.labels(method='GetAllPreferences', status='success').inc()
                
                logger.info(f"Returning preferences for {len(preferences_sets)} teachers")
                
                return core_pb2.AllPreferencesResponse(
                    preferences_sets=preferences_sets
                )
                
        except Exception as e:
            logger.error(f"GetAllPreferences error: {e}", exc_info=True)
            rpc_requests_total.labels(method='GetAllPreferences', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.AllPreferencesResponse()
    
    def ClearPreferences(self, request, context):
        """Очистить предпочтения преподавателя"""
        try:
            with rpc_request_duration.labels(method='ClearPreferences').time():
                result = self.preference_service.clear_preferences(request.teacher_id)
                
                rpc_requests_total.labels(method='ClearPreferences', status='success').inc()
                
                return core_pb2.ClearResponse(
                    success=result['success'],
                    deleted_count=result['deleted_count']
                )
                
        except Exception as e:
            logger.error(f"ClearPreferences error: {e}", exc_info=True)
            rpc_requests_total.labels(method='ClearPreferences', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.ClearResponse(success=False)
    
    # ============ GROUPS ============
    
    def CreateGroup(self, request, context):
        """Создать группу"""
        try:
            with rpc_request_duration.labels(method='CreateGroup').time():
                group_data = {
                    'name': request.name,
                    'short_name': request.short_name or None,
                    'year': request.year,
                    'semester': request.semester,
                    'program_code': request.program_code or None,
                    'program_name': request.program_name or None,
                    'specialization': request.specialization or None,
                    'level': request.level,
                    'curator_teacher_id': request.curator_teacher_id or None,
                    'enrollment_date': request.enrollment_date or None
                }
                
                result = self.group_service.create_group(group_data)
                
                # Получить полную информацию о группе
                group = self.group_service.get_group(group_id=result['id'])
                
                if not group:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Failed to retrieve created group")
                    return core_pb2.GroupResponse()
                
                group_message = self._build_group_message(group)
                
                rpc_requests_total.labels(method='CreateGroup', status='success').inc()
                
                return core_pb2.GroupResponse(
                    group=group_message,
                    message="Group created successfully"
                )
                
        except Exception as e:
            logger.error(f"CreateGroup error: {e}", exc_info=True)
            rpc_requests_total.labels(method='CreateGroup', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.GroupResponse()
    
    def GetGroup(self, request, context):
        """Получить группу"""
        try:
            with rpc_request_duration.labels(method='GetGroup').time():
                group_id = None
                name = None
                
                if request.HasField('id'):
                    group_id = request.id
                elif request.HasField('name'):
                    name = request.name
                else:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Must provide id or name")
                    return core_pb2.GroupResponse()
                
                result = self.group_service.get_group(group_id=group_id, name=name)
                
                if not result:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Group not found")
                    return core_pb2.GroupResponse()
                
                group_message = self._build_group_message(result)
                
                rpc_requests_total.labels(method='GetGroup', status='success').inc()
                
                return core_pb2.GroupResponse(
                    group=group_message,
                    message="Group retrieved successfully"
                )
                
        except Exception as e:
            logger.error(f"GetGroup error: {e}", exc_info=True)
            rpc_requests_total.labels(method='GetGroup', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.GroupResponse()
    
    def ListGroups(self, request, context):
        """Получить список групп"""
        try:
            with rpc_request_duration.labels(method='ListGroups').time():
                result = self.group_service.list_groups(
                    page=request.page or 1,
                    page_size=request.page_size or 50,
                    year=request.year if request.year else None,
                    level=request.level if request.level else None,
                    only_active=request.only_active if request.only_active else False,
                    sort_by=request.sort_by if request.sort_by else 'created_at',
                    sort_order='DESC'
                )
                
                groups = []
                for group_data in result['groups']:
                    groups.append(self._build_group_message(group_data))
                
                rpc_requests_total.labels(method='ListGroups', status='success').inc()
                
                return core_pb2.GroupsListResponse(
                    groups=groups,
                    total_count=result['total_count']
                )
                
        except Exception as e:
            logger.error(f"ListGroups error: {e}", exc_info=True)
            rpc_requests_total.labels(method='ListGroups', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.GroupsListResponse()
    
    # ============ STUDENTS ============
    
    def CreateStudent(self, request, context):
        """Создать студента"""
        try:
            with rpc_request_duration.labels(method='CreateStudent').time():
                student_data = {
                    'full_name': request.full_name,
                    'first_name': request.first_name or None,
                    'last_name': request.last_name or None,
                    'middle_name': request.middle_name or None,
                    'student_number': request.student_number or None,
                    'group_id': request.group_id,
                    'email': request.email or None,
                    'phone': request.phone or None,
                    'enrollment_date': request.enrollment_date or None
                }
                
                result = self.student_service.create_student(student_data)
                
                # Используем данные из результата создания
                # Добавляем недостающие поля с дефолтными значениями
                student_dict = {
                    'id': result['id'],
                    'full_name': result['full_name'],
                    'first_name': result.get('first_name', ''),
                    'last_name': result.get('last_name', ''),
                    'middle_name': result.get('middle_name', ''),
                    'student_number': result.get('student_number', ''),
                    'group_id': result['group_id'],
                    'group_name': result.get('group_name', ''),
                    'email': result.get('email', ''),
                    'phone': result.get('phone', ''),
                    'user_id': result.get('user_id', 0),
                    'status': result.get('status', 'active'),
                    'enrollment_date': result.get('enrollment_date', ''),
                    'created_at': result.get('created_at', ''),
                    'updated_at': result.get('updated_at', '')
                }
                
                student_message = self._build_student_message(student_dict)
                
                rpc_requests_total.labels(method='CreateStudent', status='success').inc()
                
                return core_pb2.StudentResponse(
                    student=student_message,
                    message="Student created successfully"
                )
                
        except psycopg2.errors.ForeignKeyViolation as e:
            logger.error(f"CreateStudent foreign key error: {e}")
            rpc_requests_total.labels(method='CreateStudent', status='error').inc()
            
            # Определить, какая foreign key нарушена
            error_msg = str(e)
            if "group_id" in error_msg:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Group with specified ID does not exist. {error_msg}")
            elif "teacher_id" in error_msg:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Teacher with specified ID does not exist. {error_msg}")
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Foreign key violation: {error_msg}")
            
            return core_pb2.StudentResponse()
        except psycopg2.errors.UniqueViolation as e:
            logger.error(f"CreateStudent unique violation: {e}")
            rpc_requests_total.labels(method='CreateStudent', status='error').inc()
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f"Student with this student_number already exists. {str(e)}")
            return core_pb2.StudentResponse()
        except Exception as e:
            logger.error(f"CreateStudent error: {e}", exc_info=True)
            rpc_requests_total.labels(method='CreateStudent', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.StudentResponse()
    
    def GetStudent(self, request, context):
        """Получить студента"""
        try:
            with rpc_request_duration.labels(method='GetStudent').time():
                student_id = None
                student_number = None
                user_id = None
                
                if request.HasField('id'):
                    student_id = request.id
                elif request.HasField('student_number'):
                    student_number = request.student_number
                elif request.HasField('user_id'):
                    user_id = request.user_id
                else:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Must provide id, student_number, or user_id")
                    return core_pb2.StudentResponse()
                
                result = self.student_service.get_student(
                    student_id=student_id,
                    student_number=student_number,
                    user_id=user_id
                )
                
                if not result:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Student not found")
                    return core_pb2.StudentResponse()
                
                student_message = self._build_student_message(result)
                
                rpc_requests_total.labels(method='GetStudent', status='success').inc()
                
                return core_pb2.StudentResponse(
                    student=student_message,
                    message="Student retrieved successfully"
                )
                
        except Exception as e:
            logger.error(f"GetStudent error: {e}", exc_info=True)
            rpc_requests_total.labels(method='GetStudent', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.StudentResponse()
    
    def ListStudents(self, request, context):
        """Получить список студентов"""
        try:
            with rpc_request_duration.labels(method='ListStudents').time():
                result = self.student_service.list_students(
                    page=request.page or 1,
                    page_size=request.page_size or 50,
                    group_id=request.group_id if request.group_id else None,
                    status=request.status if request.status else None,
                    sort_by=request.sort_by if request.sort_by else 'created_at',
                    sort_order='DESC'
                )
                
                students = []
                for student_data in result['students']:
                    students.append(self._build_student_message(student_data))
                
                rpc_requests_total.labels(method='ListStudents', status='success').inc()
                
                return core_pb2.StudentsListResponse(
                    students=students,
                    total_count=result['total_count']
                )
                
        except Exception as e:
            logger.error(f"ListStudents error: {e}", exc_info=True)
            rpc_requests_total.labels(method='ListStudents', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.StudentsListResponse()
    
    def GetGroupStudents(self, request, context):
        """Получить список студентов группы"""
        try:
            with rpc_request_duration.labels(method='GetGroupStudents').time():
                result = self.student_service.get_group_students(
                    group_id=request.group_id,
                    status=request.status if request.status else None
                )
                
                students = []
                for student_data in result['students']:
                    # Добавить недостающие поля для совместимости
                    student_dict = {
                        'id': student_data['id'],
                        'full_name': student_data['full_name'],
                        'first_name': '',
                        'last_name': '',
                        'middle_name': '',
                        'student_number': student_data.get('student_number', ''),
                        'group_id': result['group_id'],
                        'group_name': '',
                        'email': student_data.get('email', ''),
                        'phone': student_data.get('phone', ''),
                        'user_id': 0,
                        'status': student_data.get('status', 'active'),
                        'enrollment_date': student_data.get('enrollment_date', ''),
                        'created_at': student_data.get('created_at', ''),
                        'updated_at': ''
                    }
                    students.append(self._build_student_message(student_dict))
                
                rpc_requests_total.labels(method='GetGroupStudents', status='success').inc()
                
                return core_pb2.StudentsListResponse(
                    students=students,
                    total_count=result['total_count']
                )
                
        except Exception as e:
            logger.error(f"GetGroupStudents error: {e}", exc_info=True)
            rpc_requests_total.labels(method='GetGroupStudents', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.StudentsListResponse()
    
    # ============ USER LINKS ============
    
    def LinkTeacherToUser(self, request, context):
        """Связать преподавателя с пользователем из ms-auth"""
        try:
            with rpc_request_duration.labels(method='LinkTeacherToUser').time():
                success = self.teacher_service.link_teacher_to_user(
                    teacher_id=request.entity_id,
                    user_id=request.user_id
                )
                
                rpc_requests_total.labels(method='LinkTeacherToUser', status='success').inc()
                
                return core_pb2.LinkResponse(
                    success=success,
                    message="Teacher linked to user successfully"
                )
                
        except Exception as e:
            logger.error(f"LinkTeacherToUser error: {e}", exc_info=True)
            rpc_requests_total.labels(method='LinkTeacherToUser', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.LinkResponse(success=False)
    
    def LinkStudentToUser(self, request, context):
        """Связать студента с пользователем из ms-auth"""
        try:
            with rpc_request_duration.labels(method='LinkStudentToUser').time():
                success = self.student_service.link_student_to_user(
                    student_id=request.entity_id,
                    user_id=request.user_id
                )
                
                rpc_requests_total.labels(method='LinkStudentToUser', status='success').inc()
                
                return core_pb2.LinkResponse(
                    success=success,
                    message="Student linked to user successfully"
                )
                
        except Exception as e:
            logger.error(f"LinkStudentToUser error: {e}", exc_info=True)
            rpc_requests_total.labels(method='LinkStudentToUser', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.LinkResponse(success=False)
    
    # ============ HEALTH CHECK ============
    
    def HealthCheck(self, request, context):
        """Health check"""
        return core_pb2.HealthCheckResponse(
            status="healthy",
            version="1.0.0",
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    # ============ HELPER METHODS ============
    
    def _build_teacher_message(self, teacher_dict: dict) -> core_pb2.Teacher:
        """Построить Teacher message из dict"""
        teacher = core_pb2.Teacher(
            id=teacher_dict['id'],
            full_name=teacher_dict['full_name'],
            first_name=teacher_dict.get('first_name', ''),
            last_name=teacher_dict.get('last_name', ''),
            middle_name=teacher_dict.get('middle_name', ''),
            email=teacher_dict.get('email', ''),
            phone=teacher_dict.get('phone', ''),
            employment_type=teacher_dict['employment_type'],
            priority=teacher_dict['priority'],
            position=teacher_dict.get('position', ''),
            academic_degree=teacher_dict.get('academic_degree', ''),
            department=teacher_dict.get('department', ''),
            user_id=teacher_dict.get('user_id', 0),
            is_active=teacher_dict.get('is_active', True),
            hire_date=teacher_dict.get('hire_date', ''),
            termination_date=teacher_dict.get('termination_date', ''),
            created_at=teacher_dict.get('created_at', ''),
            updated_at=teacher_dict.get('updated_at', '')
        )
        
        # Добавить preferences_info если есть
        if 'preferences_info' in teacher_dict:
            pref_info = teacher_dict['preferences_info']
            teacher.preferences_info.CopyFrom(core_pb2.PreferencesInfo(
                total_preferences=pref_info['total_preferences'],
                preferred_slots=pref_info['preferred_slots'],
                preferences_coverage=pref_info['preferences_coverage']
            ))
        
        return teacher
    
    def _build_group_message(self, group_dict: dict) -> core_pb2.Group:
        """Построить Group message из dict"""
        group = core_pb2.Group(
            id=group_dict['id'],
            name=group_dict['name'],
            short_name=group_dict.get('short_name', ''),
            year=group_dict.get('year', 0),
            semester=group_dict.get('semester', 0),
            size=group_dict.get('size', 0),
            program_code=group_dict.get('program_code', ''),
            program_name=group_dict.get('program_name', ''),
            specialization=group_dict.get('specialization', ''),
            level=group_dict.get('level', ''),
            curator_teacher_id=group_dict.get('curator_teacher_id', 0),
            curator_name=group_dict.get('curator_name', ''),
            is_active=group_dict.get('is_active', True),
            enrollment_date=group_dict.get('enrollment_date', ''),
            graduation_date=group_dict.get('graduation_date', ''),
            created_at=group_dict.get('created_at', ''),
            updated_at=group_dict.get('updated_at', '')
        )
        
        return group
    
    def _build_student_message(self, student_dict: dict) -> core_pb2.Student:
        """Построить Student message из dict"""
        student = core_pb2.Student(
            id=student_dict['id'],
            full_name=student_dict['full_name'],
            first_name=student_dict.get('first_name', ''),
            last_name=student_dict.get('last_name', ''),
            middle_name=student_dict.get('middle_name', ''),
            student_number=student_dict.get('student_number', ''),
            group_id=student_dict.get('group_id', 0),
            group_name=student_dict.get('group_name', ''),
            email=student_dict.get('email', ''),
            phone=student_dict.get('phone', ''),
            user_id=student_dict.get('user_id', 0),
            status=student_dict.get('status', 'active'),
            enrollment_date=student_dict.get('enrollment_date', ''),
            created_at=student_dict.get('created_at', ''),
            updated_at=student_dict.get('updated_at', '')
        )
        
        return student
    
    # ============ COURSE LOADS ============
    
    def ListCourseLoads(self, request, context):
        """Получить список учебной нагрузки"""
        try:
            with rpc_request_duration.labels(method='ListCourseLoads').time():
                result = self.load_service.list_course_loads(
                    page=request.page or 1,
                    page_size=request.page_size or 50,
                    semester=request.semester if request.semester else None,
                    academic_year=request.academic_year if request.academic_year else None,
                    teacher_ids=list(request.teacher_ids) if request.teacher_ids else None,
                    group_ids=list(request.group_ids) if request.group_ids else None,
                    lesson_types=list(request.lesson_types) if request.lesson_types else None,
                    # Для bool полей в protobuf нет HasField(), используем значение напрямую
                    # По умолчанию only_active = True (только активные нагрузки)
                    only_active=request.only_active
                )
                
                # Преобразовать в protobuf messages
                course_load_messages = []
                for load in result['course_loads']:
                    # Обработать NULL значения: None -> 0 для protobuf
                    teacher_id = load.get('teacher_id') if load.get('teacher_id') is not None else 0
                    group_id = load.get('group_id') if load.get('group_id') is not None else 0
                    
                    course_load_messages.append(core_pb2.CourseLoad(
                        id=load['id'],
                        discipline_name=load['discipline_name'],
                        discipline_code=load.get('discipline_code', ''),
                        teacher_id=teacher_id,
                        teacher_name=load.get('teacher_name', ''),
                        teacher_priority=load.get('teacher_priority', 0),
                        group_id=group_id,
                        group_name=load.get('group_name', ''),
                        group_size=load.get('group_size', 0),
                        lesson_type=load.get('lesson_type', ''),
                        hours_per_semester=load.get('hours_per_semester', 0),
                        lessons_per_week=load.get('lessons_per_week', 0),
                        semester=load.get('semester', 0),
                        academic_year=load.get('academic_year', '')
                    ))
                
                rpc_requests_total.labels(method='ListCourseLoads', status='success').inc()
                
                return core_pb2.CourseLoadsListResponse(
                    course_loads=course_load_messages,
                    total_count=result['total_count']
                )
                
        except Exception as e:
            logger.error(f"ListCourseLoads error: {e}", exc_info=True)
            rpc_requests_total.labels(method='ListCourseLoads', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.CourseLoadsListResponse()
    
    def CreateCourseLoad(self, request, context):
        """Создать запись учебной нагрузки"""
        try:
            with rpc_request_duration.labels(method='CreateCourseLoad').time():
                # Обработать NULL значения: 0 -> None
                teacher_id = request.teacher_id if request.teacher_id > 0 else None
                group_id = request.group_id if request.group_id > 0 else None
                discipline_id = request.discipline_id if request.discipline_id > 0 else None
                
                result = self.load_service.create_course_load(
                    discipline_name=request.discipline_name,
                    discipline_code=request.discipline_code if request.discipline_code else None,
                    discipline_id=discipline_id,
                    teacher_id=teacher_id,
                    teacher_name=None,  # Будет получено из БД если teacher_id указан
                    group_id=group_id,
                    group_name=None,  # Будет получено из БД если group_id указан
                    group_size=None,
                    lesson_type=request.lesson_type,
                    hours_per_semester=request.hours_per_semester,
                    weeks_count=request.weeks_count if request.weeks_count > 0 else 16,
                    semester=request.semester,
                    academic_year=request.academic_year,
                    required_classroom_type=request.required_classroom_type if request.required_classroom_type else None,
                    min_classroom_capacity=request.min_classroom_capacity if request.min_classroom_capacity > 0 else None,
                    created_by=None
                )
                
                # Преобразовать в protobuf message
                course_load = core_pb2.CourseLoad(
                    id=result['id'],
                    discipline_id=discipline_id or 0,
                    discipline_name=result['discipline_name'],
                    discipline_code=request.discipline_code if request.discipline_code else '',
                    teacher_id=teacher_id or 0,
                    teacher_name=result['teacher_name'],
                    teacher_priority=0,
                    group_id=group_id or 0,
                    group_name=result['group_name'],
                    group_size=0,
                    lesson_type=request.lesson_type,
                    hours_per_semester=request.hours_per_semester,
                    weeks_count=request.weeks_count if request.weeks_count > 0 else 16,
                    lessons_per_week=result.get('lessons_per_week', 0),
                    semester=request.semester,
                    academic_year=request.academic_year,
                    required_classroom_type=request.required_classroom_type if request.required_classroom_type else '',
                    min_classroom_capacity=request.min_classroom_capacity if request.min_classroom_capacity > 0 else 0,
                    is_active=True,
                    source='manual',
                    import_batch_id='',
                    created_at=result.get('created_at', '')
                )
                
                rpc_requests_total.labels(method='CreateCourseLoad', status='success').inc()
                
                return core_pb2.CourseLoadResponse(
                    course_load=course_load,
                    message="Course load created successfully"
                )
                
        except Exception as e:
            logger.error(f"CreateCourseLoad error: {e}", exc_info=True)
            rpc_requests_total.labels(method='CreateCourseLoad', status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return core_pb2.CourseLoadResponse()
    
    # TODO: Добавить остальные методы (Disciplines, DeleteCourseLoad, Import)

