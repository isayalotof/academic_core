"""
Core RPC Client для Gateway
Подключение к ms-core
"""
import grpc
import logging
from typing import Optional, Dict, Any, List
import os

# Import generated protobuf files from local directory
try:
    from rpc_clients.generated import core_pb2, core_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
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
        self.host = host or os.getenv('MS_CORE_HOST', 'localhost')
        self.port = port or int(os.getenv('MS_CORE_PORT', 50054))
        self.address = f'{self.host}:{self.port}'
        
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
            logger.warning("Proto files not available")
    
    def create_teacher(self, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать преподавателя"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.CreateTeacherRequest(**teacher_data)
        response = self.stub.CreateTeacher(request, timeout=10)
        
        return {
            'id': response.teacher.id,
            'full_name': response.teacher.full_name,
            'email': response.teacher.email,
            'employment_type': response.teacher.employment_type,
            'priority': response.teacher.priority,
            'message': response.message
        }
    
    def get_teacher(self, teacher_id: int) -> Optional[Dict[str, Any]]:
        """Получить преподавателя"""
        if not self.stub:
            return None
        
        request = core_pb2.GetTeacherRequest(id=teacher_id, include_preferences=True)
        response = self.stub.GetTeacher(request, timeout=10)
        
        if not response.teacher:
            return None
        
        teacher = response.teacher
        result = {
            'id': teacher.id,
            'full_name': teacher.full_name,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'middle_name': teacher.middle_name,
            'email': teacher.email,
            'phone': teacher.phone,
            'employment_type': teacher.employment_type,
            'priority': teacher.priority,
            'position': teacher.position,
            'academic_degree': teacher.academic_degree,
            'department': teacher.department,
            'user_id': teacher.user_id if teacher.user_id and teacher.user_id > 0 else None,
            'is_active': teacher.is_active,
            'hire_date': teacher.hire_date if teacher.hire_date else None,
            'termination_date': teacher.termination_date if teacher.termination_date else None,
            'created_at': teacher.created_at,
            'updated_at': teacher.updated_at
        }
        
        if teacher.HasField('preferences_info'):
            result['preferences_info'] = {
                'total_preferences': teacher.preferences_info.total_preferences,
                'preferred_slots': teacher.preferences_info.preferred_slots,
                'preferences_coverage': teacher.preferences_info.preferences_coverage
            }
        
        return result
    
    def list_teachers(
        self,
        page: int = 1,
        page_size: int = 50,
        employment_type: Optional[str] = None,
        department: Optional[str] = None,
        only_active: bool = True
    ) -> Dict[str, Any]:
        """Получить список преподавателей"""
        if not self.stub:
            return {
                "teachers": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
        
        request = core_pb2.ListTeachersRequest(
            page=page,
            page_size=page_size,
            employment_types=[employment_type] if employment_type else [],
            department=department if department else "",
            only_active=only_active
        )
        
        response = self.stub.ListTeachers(request, timeout=10)
        
        teachers = []
        for teacher in response.teachers:
            teachers.append({
                'id': teacher.id,
                'full_name': teacher.full_name,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'email': teacher.email,
                'phone': teacher.phone,
                'employment_type': teacher.employment_type,
                'priority': teacher.priority,
                'position': teacher.position,
                'academic_degree': teacher.academic_degree,
                'department': teacher.department,
                'user_id': teacher.user_id if teacher.user_id and teacher.user_id > 0 else None,
                'is_active': teacher.is_active,
                'created_at': teacher.created_at
            })
        
        total_pages = (response.total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        return {
            "teachers": teachers,
            "total_count": response.total_count,
            "page": response.page,
            "page_size": response.page_size,
            "total_pages": total_pages
        }
    
    def create_group(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать группу"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.CreateGroupRequest(**group_data)
        response = self.stub.CreateGroup(request, timeout=10)
        
        if not response.group:
            raise Exception("Failed to create group")
        
        group = response.group
        return {
            'id': group.id,
            'name': group.name,
            'short_name': group.short_name,
            'year': group.year,
            'semester': group.semester,
            'size': group.size,
            'program_code': group.program_code,
            'program_name': group.program_name,
            'specialization': group.specialization,
            'level': group.level,
            'curator_teacher_id': group.curator_teacher_id,
            'is_active': group.is_active,
            'message': response.message
        }
    
    def get_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Получить группу"""
        if not self.stub:
            return None
        
        request = core_pb2.GetGroupRequest(id=group_id)
        response = self.stub.GetGroup(request, timeout=10)
        
        if not response.group:
            return None
        
        group = response.group
        return {
            'id': group.id,
            'name': group.name,
            'short_name': group.short_name,
            'year': group.year,
            'semester': group.semester,
            'size': group.size,
            'program_code': group.program_code,
            'program_name': group.program_name,
            'specialization': group.specialization,
            'level': group.level,
            'curator_teacher_id': group.curator_teacher_id,
            'curator_name': group.curator_name,
            'is_active': group.is_active,
            'enrollment_date': group.enrollment_date,
            'graduation_date': group.graduation_date,
            'created_at': group.created_at,
            'updated_at': group.updated_at
        }
    
    def list_groups(
        self,
        page: int = 1,
        page_size: int = 50,
        year: Optional[int] = None,
        level: Optional[str] = None,
        only_active: bool = True
    ) -> Dict[str, Any]:
        """Получить список групп"""
        if not self.stub:
            return {
                "groups": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
        
        request = core_pb2.ListGroupsRequest(
            page=page,
            page_size=page_size,
            year=year if year else 0,
            level=level if level else "",
            only_active=only_active
        )
        
        response = self.stub.ListGroups(request, timeout=10)
        
        groups = []
        for group in response.groups:
            groups.append({
                'id': group.id,
                'name': group.name,
                'short_name': group.short_name,
                'year': group.year,
                'semester': group.semester,
                'size': group.size,
                'program_code': group.program_code,
                'program_name': group.program_name,
                'level': group.level,
                'curator_teacher_id': group.curator_teacher_id,
                'curator_name': group.curator_name,
                'is_active': group.is_active,
                'created_at': group.created_at
            })
        
        total_pages = (response.total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        return {
            "groups": groups,
            "total_count": response.total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать студента"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.CreateStudentRequest(**student_data)
        response = self.stub.CreateStudent(request, timeout=10)
        
        if not response.student:
            raise Exception("Failed to create student")
        
        student = response.student
        return {
            'id': student.id,
            'full_name': student.full_name,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'middle_name': student.middle_name,
            'student_number': student.student_number,
            'group_id': student.group_id,
            'group_name': student.group_name,
            'email': student.email,
            'phone': student.phone,
            'user_id': student.user_id,
            'status': student.status,
            'enrollment_date': student.enrollment_date,
            'message': response.message
        }
    
    def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Получить студента"""
        if not self.stub:
            return None
        
        request = core_pb2.GetStudentRequest(id=student_id)
        response = self.stub.GetStudent(request, timeout=10)
        
        if not response.student:
            return None
        
        student = response.student
        return {
            'id': student.id,
            'full_name': student.full_name,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'middle_name': student.middle_name,
            'student_number': student.student_number,
            'group_id': student.group_id,
            'group_name': student.group_name,
            'email': student.email,
            'phone': student.phone,
            'user_id': student.user_id,
            'status': student.status,
            'enrollment_date': student.enrollment_date,
            'created_at': student.created_at,
            'updated_at': student.updated_at
        }
    
    def list_students(
        self,
        page: int = 1,
        page_size: int = 50,
        group_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получить список студентов"""
        if not self.stub:
            return {
                "students": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
        
        request = core_pb2.ListStudentsRequest(
            page=page,
            page_size=page_size,
            group_id=group_id if group_id else 0,
            status=status if status else ""
        )
        
        response = self.stub.ListStudents(request, timeout=10)
        
        students = []
        for student in response.students:
            students.append({
                'id': student.id,
                'full_name': student.full_name,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'middle_name': student.middle_name,
                'student_number': student.student_number,
                'group_id': student.group_id,
                'group_name': student.group_name,
                'email': student.email,
                'phone': student.phone,
                'user_id': student.user_id,
                'status': student.status,
                'enrollment_date': student.enrollment_date,
                'created_at': student.created_at
            })
        
        total_pages = (response.total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        return {
            "students": students,
            "total_count": response.total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def get_group_students(
        self,
        group_id: int,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получить список студентов группы"""
        if not self.stub:
            return {
                "group_id": group_id,
                "students": [],
                "total_count": 0
            }
        
        request = core_pb2.GroupStudentsRequest(
            group_id=group_id,
            status=status if status else ""
        )
        
        response = self.stub.GetGroupStudents(request, timeout=10)
        
        students = []
        for student in response.students:
            students.append({
                'id': student.id,
                'full_name': student.full_name,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'middle_name': student.middle_name,
                'student_number': student.student_number,
                'group_id': student.group_id,
                'group_name': student.group_name,
                'email': student.email,
                'phone': student.phone,
                'user_id': student.user_id,
                'status': student.status,
                'enrollment_date': student.enrollment_date,
                'created_at': student.created_at
            })
        
        return {
            "group_id": group_id,
            "students": students,
            "total_count": response.total_count
        }
    
    def get_teacher_preferences(self, teacher_id: int) -> Dict[str, Any]:
        """⭐ Получить предпочтения преподавателя"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.GetPreferencesRequest(teacher_id=teacher_id)
        response = self.stub.GetTeacherPreferences(request, timeout=10)
        
        preferences = []
        for pref in response.preferences:
            preferences.append({
                'id': pref.id,
                'day_of_week': pref.day_of_week,
                'time_slot': pref.time_slot,
                'is_preferred': pref.is_preferred,
                'preference_strength': pref.preference_strength,
                'reason': pref.reason
            })
        
        return {
            'teacher_id': response.teacher_id,
            'teacher_name': response.teacher_name,
            'teacher_priority': response.teacher_priority,
            'preferences': preferences,
            'total_preferences': response.total_preferences,
            'preferred_count': response.preferred_count,
            'not_preferred_count': response.not_preferred_count,
            'coverage_percentage': response.coverage_percentage
        }
    
    def set_teacher_preferences(
        self,
        teacher_id: int,
        preferences: List[Dict[str, Any]],
        replace_existing: bool = False
    ) -> Dict[str, Any]:
        """⭐ Установить предпочтения преподавателя"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        pref_items = []
        for pref in preferences:
            pref_items.append(core_pb2.PreferenceItem(
                day_of_week=pref['day_of_week'],
                time_slot=pref['time_slot'],
                is_preferred=pref['is_preferred'],
                preference_strength=pref.get('preference_strength', ''),
                reason=pref.get('reason', '')
            ))
        
        request = core_pb2.SetPreferencesRequest(
            teacher_id=teacher_id,
            preferences=pref_items,
            replace_existing=replace_existing
        )
        
        response = self.stub.SetTeacherPreferences(request, timeout=30)
        
        return {
            'success': response.success,
            'created_count': response.created_count,
            'updated_count': response.updated_count,
            'deleted_count': response.deleted_count,
            'message': response.message
        }
    
    def update_teacher(
        self,
        teacher_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновить преподавателя"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        # Proto3 не передает пустые строки, поэтому используем HasField или передаем только непустые значения
        # Но в Python gRPC можно передать пустую строку, она будет проигнорирована если поле optional
        request = core_pb2.UpdateTeacherRequest(
            id=teacher_id,
            updated_by=update_data.get('updated_by', 0)
        )
        
        # Устанавливаем только те поля, которые были переданы (не None)
        if 'full_name' in update_data:
            request.full_name = update_data['full_name']
        if 'email' in update_data:
            request.email = update_data['email']
        if 'phone' in update_data:
            request.phone = update_data['phone']
        if 'employment_type' in update_data:
            request.employment_type = update_data['employment_type']
        if 'position' in update_data:
            request.position = update_data['position']
        if 'department' in update_data:
            request.department = update_data['department']
        if 'is_active' in update_data:
            request.is_active = update_data['is_active']
        
        response = self.stub.UpdateTeacher(request, timeout=10)
        
        if not response.teacher:
            raise Exception("Failed to update teacher")
        
        teacher = response.teacher
        return {
            'id': teacher.id,
            'full_name': teacher.full_name,
            'email': teacher.email,
            'phone': teacher.phone,
            'employment_type': teacher.employment_type,
            'priority': teacher.priority,
            'position': teacher.position,
            'department': teacher.department,
            'is_active': teacher.is_active,
            'message': response.message
        }
    
    def delete_teacher(
        self,
        teacher_id: int,
        hard_delete: bool = False
    ) -> Dict[str, Any]:
        """Удалить преподавателя (мягкое удаление по умолчанию)"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.DeleteTeacherRequest(
            id=teacher_id,
            hard_delete=hard_delete
        )
        
        response = self.stub.DeleteTeacher(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message
        }
    
    def search_teachers(
        self,
        query: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Поиск преподавателей"""
        if not self.stub:
            return {
                "teachers": [],
                "total_count": 0,
                "query": query
            }
        
        request = core_pb2.SearchRequest(
            query=query,
            limit=limit
        )
        
        response = self.stub.SearchTeachers(request, timeout=10)
        
        teachers = []
        for teacher in response.teachers:
            teachers.append({
                'id': teacher.id,
                'full_name': teacher.full_name,
                'email': teacher.email,
                'phone': teacher.phone,
                'employment_type': teacher.employment_type,
                'priority': teacher.priority,
                'position': teacher.position,
                'department': teacher.department,
                'is_active': teacher.is_active
            })
        
        return {
            "teachers": teachers,
            "total_count": response.total_count,
            "query": query
        }
    
    def update_group(
        self,
        group_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновить группу"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.UpdateGroupRequest(id=group_id)
        
        # Устанавливаем только те поля, которые были переданы
        if 'name' in update_data:
            request.name = update_data['name']
        if 'semester' in update_data:
            request.semester = update_data['semester']
        if 'curator_teacher_id' in update_data:
            request.curator_teacher_id = update_data['curator_teacher_id']
        if 'is_active' in update_data:
            request.is_active = update_data['is_active']
        
        response = self.stub.UpdateGroup(request, timeout=10)
        
        if not response.group:
            raise Exception("Failed to update group")
        
        group = response.group
        return {
            'id': group.id,
            'name': group.name,
            'short_name': group.short_name,
            'year': group.year,
            'semester': group.semester,
            'size': group.size,
            'is_active': group.is_active,
            'message': response.message
        }
    
    def delete_group(
        self,
        group_id: int
    ) -> Dict[str, Any]:
        """Удалить группу (мягкое удаление)"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.DeleteGroupRequest(id=group_id)
        response = self.stub.DeleteGroup(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message
        }
    
    def update_student(
        self,
        student_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновить студента"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.UpdateStudentRequest(id=student_id)
        
        # Устанавливаем только те поля, которые были переданы
        if 'full_name' in update_data:
            request.full_name = update_data['full_name']
        if 'group_id' in update_data:
            request.group_id = update_data['group_id']
        if 'email' in update_data:
            request.email = update_data['email']
        if 'phone' in update_data:
            request.phone = update_data['phone']
        if 'status' in update_data:
            request.status = update_data['status']
        
        response = self.stub.UpdateStudent(request, timeout=10)
        
        if not response.student:
            raise Exception("Failed to update student")
        
        student = response.student
        return {
            'id': student.id,
            'full_name': student.full_name,
            'student_number': student.student_number,
            'group_id': student.group_id,
            'group_name': student.group_name,
            'email': student.email,
            'phone': student.phone,
            'status': student.status,
            'message': response.message
        }
    
    def delete_student(
        self,
        student_id: int
    ) -> Dict[str, Any]:
        """Удалить студента"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.DeleteStudentRequest(id=student_id)
        response = self.stub.DeleteStudent(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message
        }
    
    def search_students(
        self,
        query: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Поиск студентов"""
        if not self.stub:
            return {
                "students": [],
                "total_count": 0,
                "query": query
            }
        
        # Используем ListStudents с фильтрацией по query через поиск в БД
        # В реальной реализации должен быть отдельный SearchStudents метод
        # Пока используем существующий метод list_students
        # TODO: Добавить SearchStudents в proto если его нет
        
        # Временная реализация через list_students
        # В реальности нужен отдельный SearchStudents RPC
        return {
            "students": [],
            "total_count": 0,
            "query": query,
            "message": "Search students requires SearchStudents RPC method"
        }
    
    def list_course_loads(
        self,
        page: int = 1,
        page_size: int = 50,
        semester: Optional[int] = None,
        academic_year: Optional[str] = None,
        teacher_ids: Optional[List[int]] = None,
        group_ids: Optional[List[int]] = None,
        only_active: bool = True
    ) -> Dict[str, Any]:
        """Получить список учебной нагрузки"""
        if not self.stub:
            return {
                "course_loads": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
        
        request = core_pb2.ListCourseLoadsRequest(
            page=page,
            page_size=page_size,
            semester=semester if semester else 0,
            academic_year=academic_year if academic_year else "",
            teacher_ids=teacher_ids if teacher_ids else [],
            group_ids=group_ids if group_ids else [],
            only_active=only_active
        )
        
        response = self.stub.ListCourseLoads(request, timeout=10)
        
        course_loads = []
        for load in response.course_loads:
            course_loads.append({
                'id': load.id,
                'discipline_name': load.discipline_name,
                'discipline_code': load.discipline_code,
                'teacher_id': load.teacher_id,
                'teacher_name': load.teacher_name,
                'teacher_priority': load.teacher_priority,
                'group_id': load.group_id,
                'group_name': load.group_name,
                'group_size': load.group_size,
                'lesson_type': load.lesson_type,
                'hours_per_semester': load.hours_per_semester,
                'lessons_per_week': load.lessons_per_week,
                'semester': load.semester,
                'academic_year': load.academic_year,
                'is_active': load.is_active
            })
        
        total_pages = (response.total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        return {
            "course_loads": course_loads,
            "total_count": response.total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def delete_course_load(
        self,
        load_id: int
    ) -> Dict[str, Any]:
        """Удалить учебную нагрузку"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.DeleteCourseLoadRequest(id=load_id)
        response = self.stub.DeleteCourseLoad(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message
        }
    
    def import_course_loads(
        self,
        file_data: bytes,
        filename: str,
        semester: int,
        academic_year: str,
        imported_by: int,
        validate_only: bool = False
    ) -> Dict[str, Any]:
        """Импортировать учебную нагрузку из Excel"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.ImportRequest(
            file_data=file_data,
            filename=filename,
            semester=semester,
            academic_year=academic_year,
            validate_only=validate_only,
            imported_by=imported_by
        )
        
        response = self.stub.ImportCourseLoads(request, timeout=60)
        
        return {
            'success': response.success,
            'batch_id': response.batch_id,
            'total_rows': response.total_rows,
            'successful_rows': response.successful_rows,
            'failed_rows': response.failed_rows,
            'errors': list(response.errors),
            'message': response.message
        }
    
    def get_import_status(
        self,
        batch_id: str
    ) -> Dict[str, Any]:
        """Получить статус импорта"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.ImportStatusRequest(batch_id=batch_id)
        response = self.stub.GetImportStatus(request, timeout=10)
        
        if not response.batch:
            return {
                'batch_id': batch_id,
                'status': 'not_found',
                'message': 'Batch not found'
            }
        
        batch = response.batch
        return {
            'batch_id': batch.batch_id,
            'status': batch.status,
            'total_rows': batch.total_rows,
            'successful_rows': batch.successful_rows,
            'failed_rows': batch.failed_rows,
            'errors': list(batch.errors),
            'started_at': batch.started_at,
            'completed_at': batch.completed_at,
            'filename': batch.filename
        }
    
    def get_course_loads_summary(
        self,
        semester: int,
        academic_year: str
    ) -> Dict[str, Any]:
        """Получить сводку по учебной нагрузке"""
        if not self.stub:
            return {
                'semester': semester,
                'academic_year': academic_year,
                'total_hours': 0,
                'teachers_count': 0,
                'groups_count': 0,
                'disciplines_count': 0,
                'by_lesson_type': {}
            }
        
        # Получаем все нагрузки для подсчета статистики
        loads = self.list_course_loads(
            page=1,
            page_size=10000,  # Большой размер для получения всех
            semester=semester,
            academic_year=academic_year,
            only_active=True
        )
        
        course_loads = loads.get('course_loads', [])
        
        # Подсчет статистики
        total_hours = sum(load.get('hours_per_semester', 0) for load in course_loads)
        teachers = set(load.get('teacher_id', 0) for load in course_loads if load.get('teacher_id', 0) > 0)
        groups = set(load.get('group_id', 0) for load in course_loads if load.get('group_id', 0) > 0)
        disciplines = set(load.get('discipline_name', '') for load in course_loads if load.get('discipline_name'))
        
        by_lesson_type = {}
        for load in course_loads:
            lesson_type = load.get('lesson_type', 'unknown')
            by_lesson_type[lesson_type] = by_lesson_type.get(lesson_type, 0) + 1
        
        return {
            'semester': semester,
            'academic_year': academic_year,
            'total_hours': total_hours,
            'teachers_count': len(teachers),
            'groups_count': len(groups),
            'disciplines_count': len(disciplines),
            'by_lesson_type': by_lesson_type
        }
    
    def clear_teacher_preferences(
        self,
        teacher_id: int
    ) -> Dict[str, Any]:
        """Очистить все предпочтения преподавателя"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.ClearPreferencesRequest(teacher_id=teacher_id)
        response = self.stub.ClearPreferences(request, timeout=10)
        
        return {
            'success': response.success,
            'deleted_count': response.deleted_count,
            'message': f'Cleared {response.deleted_count} preferences'
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Проверить доступность ms-core"""
        if not self.stub:
            return {'status': 'unavailable'}
        
        try:
            request = core_pb2.HealthCheckRequest()
            response = self.stub.HealthCheck(request, timeout=5)
            return {
                'status': response.status,
                'version': response.version
            }
        except:
            return {'status': 'unhealthy'}
    
    def create_course_load(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать запись учебной нагрузки"""
        if not self.stub:
            raise Exception("Core service not available")
        
        # Обработать NULL значения: None -> 0 для protobuf
        teacher_id = data.get('teacher_id') if data.get('teacher_id') else 0
        group_id = data.get('group_id') if data.get('group_id') else 0
        discipline_id = data.get('discipline_id') if data.get('discipline_id') else 0
        
        request = core_pb2.CreateCourseLoadRequest(
            discipline_name=data['discipline_name'],
            discipline_code=data.get('discipline_code', ''),
            discipline_id=discipline_id,
            teacher_id=teacher_id,
            group_id=group_id,
            lesson_type=data['lesson_type'],
            hours_per_semester=data['hours_per_semester'],
            weeks_count=data.get('weeks_count', 16),
            semester=data['semester'],
            academic_year=data['academic_year'],
            required_classroom_type=data.get('required_classroom_type', ''),
            min_classroom_capacity=data.get('min_classroom_capacity', 0)
        )
        
        response = self.stub.CreateCourseLoad(request, timeout=10)
        
        if not response.course_load.id:
            raise Exception(response.message or "Failed to create course load")
        
        return {
            'id': response.course_load.id,
            'discipline_id': response.course_load.discipline_id,
            'discipline_name': response.course_load.discipline_name,
            'discipline_code': response.course_load.discipline_code,
            'teacher_id': response.course_load.teacher_id if response.course_load.teacher_id > 0 else None,
            'teacher_name': response.course_load.teacher_name,
            'teacher_priority': response.course_load.teacher_priority,
            'group_id': response.course_load.group_id if response.course_load.group_id > 0 else None,
            'group_name': response.course_load.group_name,
            'group_size': response.course_load.group_size,
            'lesson_type': response.course_load.lesson_type,
            'hours_per_semester': response.course_load.hours_per_semester,
            'weeks_count': response.course_load.weeks_count,
            'lessons_per_week': response.course_load.lessons_per_week,
            'semester': response.course_load.semester,
            'academic_year': response.course_load.academic_year,
            'required_classroom_type': response.course_load.required_classroom_type if response.course_load.required_classroom_type else None,
            'min_classroom_capacity': response.course_load.min_classroom_capacity if response.course_load.min_classroom_capacity > 0 else None,
            'is_active': response.course_load.is_active,
            'source': response.course_load.source,
            'created_at': response.course_load.created_at
        }
    
    def link_student_to_user(self, student_id: int, user_id: int) -> Dict[str, Any]:
        """Связать студента с пользователем из ms-auth"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.LinkRequest(
            entity_id=student_id,
            user_id=user_id
        )
        
        response = self.stub.LinkStudentToUser(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message
        }
    
    def get_teacher_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить преподавателя по user_id"""
        if not self.stub:
            return None
        
        request = core_pb2.UserIdRequest(user_id=user_id)
        response = self.stub.GetTeacherByUserId(request, timeout=10)
        
        if not response.teacher:
            return None
        
        teacher = response.teacher
        return {
            'id': teacher.id,
            'full_name': teacher.full_name,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'middle_name': teacher.middle_name,
            'email': teacher.email,
            'phone': teacher.phone,
            'position': teacher.position,
            'academic_degree': teacher.academic_degree,
            'department': teacher.department,
            'user_id': teacher.user_id,
            'priority': teacher.priority,
            'is_active': teacher.is_active
        }
    
    def get_student_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить студента по user_id"""
        if not self.stub:
            return None
        
        request = core_pb2.UserIdRequest(user_id=user_id)
        response = self.stub.GetStudentByUserId(request, timeout=10)
        
        if not response.student:
            return None
        
        student = response.student
        return {
            'id': student.id,
            'full_name': student.full_name,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'middle_name': student.middle_name,
            'student_number': student.student_number,
            'group_id': student.group_id,
            'group_name': student.group_name,
            'email': student.email,
            'phone': student.phone,
            'user_id': student.user_id,
            'status': student.status,
            'enrollment_date': student.enrollment_date
        }
    
    def link_teacher_to_user(self, teacher_id: int, user_id: int) -> Dict[str, Any]:
        """Связать преподавателя с пользователем из ms-auth"""
        if not self.stub:
            raise Exception("CoreClient not initialized")
        
        request = core_pb2.LinkRequest(
            entity_id=teacher_id,
            user_id=user_id
        )
        
        response = self.stub.LinkTeacherToUser(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message
        }
    
    def close(self):
        """Закрыть соединение"""
        if self.channel:
            self.channel.close()


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

