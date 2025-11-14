"""
gRPC Agent Service Implementation
"""

import grpc
import logging

try:
    from proto.generated import agent_pb2, agent_pb2_grpc
except ImportError:
    agent_pb2 = None
    agent_pb2_grpc = None

from services.agent_orchestrator import agent_orchestrator
from db.connection import db
from db.queries import (
    course_loads as load_queries,
    generation_history as gen_queries,
    schedules as schedule_queries
)
from config import config

logger = logging.getLogger(__name__)


class AgentServicer:
    """gRPC Agent Service Implementation"""
    
    def GenerateSchedule(self, request, context):
        """Запустить генерацию расписания"""
        try:
            demo_mode = True
            
            result = agent_orchestrator.start_generation(
                semester=request.semester,
                max_iterations=request.max_iterations if request.max_iterations else None,
                skip_stage1=request.skip_stage1,
                skip_stage2=request.skip_stage2,
                created_by=request.created_by if request.created_by else None,
                demo_mode=demo_mode
            )
            
            if result['success']:
                return agent_pb2.GenerateResponse(
                    success=True,
                    job_id=result['job_id'],
                    message=result['message']
                )
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(result.get('error', 'Unknown error'))
                return agent_pb2.GenerateResponse(
                    success=False,
                    message=result.get('error', 'Unknown error')
                )
                
        except Exception as e:
            logger.error(f"GenerateSchedule error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return agent_pb2.GenerateResponse(success=False, message=str(e))
    
    def GetGenerationStatus(self, request, context):
        """Получить статус генерации"""
        try:
            generation = db.execute_query(
                gen_queries.SELECT_GENERATION_BY_JOB_ID,
                {'job_id': request.job_id},
                fetch=True
            )
            
            if not generation:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Generation not found")
                return agent_pb2.StatusResponse()
            
            gen = generation[0]
            
            # Прогресс
            progress = (gen['current_iteration'] / gen['max_iterations']) * 100 if gen['max_iterations'] else 0
            
            return agent_pb2.StatusResponse(
                generation=self._build_generation_message(gen),
                progress_percentage=progress
            )
            
        except Exception as e:
            logger.error(f"GetGenerationStatus error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.StatusResponse()
    
    def GetSchedule(self, request, context):
        """Получить расписание"""
        try:
            if request.generation_id:
                schedules = db.execute_query(
                    schedule_queries.SELECT_SCHEDULES_BY_GENERATION,
                    {'generation_id': request.generation_id},
                    fetch=True
                )
            elif request.only_active:
                schedules = db.execute_query(
                    schedule_queries.SELECT_ACTIVE_SCHEDULES,
                    {},
                    fetch=True
                )
                # Добавляем недостающие поля из БД
                for s in schedules:
                    if 'week_type' not in s:
                        s['week_type'] = 'both'
                    # КРИТИЧНО: Проверяем semester и academic_year из БД
                    semester_val = s.get('semester')
                    academic_year_val = s.get('academic_year')
                    if semester_val is None or (isinstance(semester_val, str) and not semester_val.strip()):
                        logger.warning(
                            f"Schedule id={s.get('id')}: semester is None or empty in DB! "
                            f"Full record: {s}"
                        )
                    if not academic_year_val or (isinstance(academic_year_val, str) and not academic_year_val.strip()):
                        logger.warning(
                            f"Schedule id={s.get('id')}: academic_year is empty in DB! "
                            f"Full record: {s}"
                        )
                    if 'semester' not in s:
                        s['semester'] = None
                    if 'academic_year' not in s:
                        s['academic_year'] = None
            else:
                schedules = []
            
            return agent_pb2.ScheduleResponse(
                schedules=[self._build_schedule_message(s) for s in schedules],
                total_count=len(schedules)
            )
            
        except Exception as e:
            logger.error(f"GetSchedule error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.ScheduleResponse()
    
    def HealthCheck(self, request, context):
        """Health check"""
        return agent_pb2.HealthCheckResponse(
            status="healthy",
            version=config.SERVICE_VERSION
        )
    
    # ============================================================
    # GENERATION HISTORY & MANAGEMENT
    # ============================================================
    
    def GetGenerationHistory(self, request, context):
        """Get full history of generation with actions"""
        try:
            from db.queries import agent_actions as action_queries
            
            # Get generation
            generation = db.execute_query(
                gen_queries.SELECT_GENERATION_BY_JOB_ID,
                {'job_id': request.job_id},
                fetch=True
            )
            
            if not generation:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Generation not found")
                return agent_pb2.HistoryResponse()
            
            gen = generation[0]
            
            # Get all actions
            limit = request.limit if request.limit > 0 else 100
            actions = db.execute_query(
                action_queries.SELECT_ACTIONS_BY_GENERATION,
                {'generation_id': gen['id'], 'limit': limit},
                fetch=True
            )
            
            # Build action messages
            action_messages = []
            for action in actions:
                action_messages.append(agent_pb2.AgentAction(
                    id=action['id'],
                    generation_id=action['generation_id'],
                    iteration=action['iteration'],
                    action_type=action['action_type'],
                    action_params=action.get('action_params', ''),
                    success=action['success'],
                    score_before=action.get('score_before', 0) or 0,
                    score_after=action.get('score_after', 0) or 0,
                    score_delta=action.get('score_delta', 0) or 0,
                    reasoning=action.get('reasoning', '') or '',
                    created_at=str(action.get('created_at', '')),
                    execution_time_ms=action.get('execution_time_ms', 0) or 0
                ))
            
            return agent_pb2.HistoryResponse(
                generation=self._build_generation_message(gen),
                actions=action_messages
            )
            
        except Exception as e:
            logger.error(f"GetGenerationHistory error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.HistoryResponse()
    
    def StopGeneration(self, request, context):
        """Stop running generation"""
        try:
            # Get generation
            generation = db.execute_query(
                gen_queries.SELECT_GENERATION_BY_JOB_ID,
                {'job_id': request.job_id},
                fetch=True
            )
            
            if not generation:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Generation not found")
                return agent_pb2.StopResponse(
                    success=False,
                    message="Generation not found"
                )
            
            gen = generation[0]
            
            if gen['status'] != 'running':
                return agent_pb2.StopResponse(
                    success=False,
                    message=f"Generation is not running (status: {gen['status']})"
                )
            
            # Update status to 'stopped'
            db.execute_query(
                gen_queries.UPDATE_GENERATION_STATUS,
                {
                    'job_id': request.job_id,
                    'status': 'stopped',
                    'error_message': 'Stopped by user'
                },
                fetch=False
            )
            
            logger.info(f"✅ Generation stopped: {request.job_id}")
            
            return agent_pb2.StopResponse(
                success=True,
                message="Generation stopped successfully"
            )
            
        except Exception as e:
            logger.error(f"StopGeneration error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.StopResponse(
                success=False,
                message="Internal error"
            )
    
    # ============================================================
    # COURSE LOADS
    # ============================================================
    
    def GetCourseLoads(self, request, context):
        """Get course loads with filters"""
        try:
            # Default semester if not provided
            semester = request.semester if request.semester else 1
            
            # Build filters
            if request.teacher_ids:
                loads = db.execute_query(
                    load_queries.SELECT_COURSE_LOADS_FILTERED,
                    {
                        'semester': semester,
                        'teacher_ids': list(request.teacher_ids),
                        'group_ids': list(request.group_ids) if request.group_ids else None
                    },
                    fetch=True
                )
            elif request.group_ids:
                loads = db.execute_query(
                    load_queries.SELECT_COURSE_LOADS_FILTERED,
                    {
                        'semester': semester,
                        'teacher_ids': None,
                        'group_ids': list(request.group_ids)
                    },
                    fetch=True
                )
            else:
                # Get all for semester
                loads = db.execute_query(
                    load_queries.SELECT_COURSE_LOADS_BY_SEMESTER,
                    {'semester': semester},
                    fetch=True
                )
            
            # Build course load messages
            load_messages = []
            for load in loads:
                load_messages.append(agent_pb2.CourseLoad(
                    id=load['id'],
                    discipline_name=load['discipline_name'],
                    discipline_code=load.get('discipline_code', '') or '',
                    teacher_id=load['teacher_id'],
                    teacher_name=load['teacher_name'],
                    teacher_priority=load['teacher_priority'],
                    group_id=load['group_id'],
                    group_name=load['group_name'],
                    group_size=load.get('group_size', 0) or 0,
                    lesson_type=load['lesson_type'],
                    hours_per_semester=load['hours_per_semester'],
                    lessons_per_week=load['lessons_per_week'],
                    semester=load['semester'],
                    academic_year=load.get('academic_year', '')
                ))
            
            return agent_pb2.CourseLoadsResponse(
                course_loads=load_messages,
                total_count=len(load_messages)
            )
            
        except Exception as e:
            logger.error(f"GetCourseLoads error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.CourseLoadsResponse()
    
    # ============================================================
    # SCHEDULE RETRIEVAL
    # ============================================================
    
    def GetScheduleForGroup(self, request, context):
        """Get schedule for specific group"""
        try:
            # Get group schedule
            schedules = db.execute_query(
                schedule_queries.SELECT_GROUP_SCHEDULE,
                {
                    'group_id': request.group_id,
                    'day_of_week': request.day_of_week if request.day_of_week else None
                },
                fetch=True
            )
            
            return agent_pb2.ScheduleResponse(
                schedules=[self._build_schedule_message(s) for s in schedules],
                total_count=len(schedules)
            )
            
        except Exception as e:
            logger.error(f"GetScheduleForGroup error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.ScheduleResponse()
    
    def GetScheduleForTeacher(self, request, context):
        """Get schedule for specific teacher"""
        try:
            # Get teacher schedule
            schedules = db.execute_query(
                schedule_queries.SELECT_TEACHER_SCHEDULE,
                {
                    'teacher_id': request.teacher_id,
                    'day_of_week': request.day_of_week if request.day_of_week else None
                },
                fetch=True
            )
            
            return agent_pb2.ScheduleResponse(
                schedules=[self._build_schedule_message(s) for s in schedules],
                total_count=len(schedules)
            )
            
        except Exception as e:
            logger.error(f"GetScheduleForTeacher error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.ScheduleResponse()
    
    # ============================================================
    # ANALYSIS & METRICS
    # ============================================================
    
    def AnalyzeSchedule(self, request, context):
        """Analyze schedule for conflicts and metrics"""
        try:
            from services.fitness import FitnessCalculator
            from db.queries import teacher_preferences as pref_queries
            
            # Determine generation_id
            if request.HasField('generation_id'):
                generation_id = request.generation_id
            elif request.HasField('current_active'):
                # Get active schedules
                active_gen = db.execute_query(
                    """
                    SELECT DISTINCT generation_id 
                    FROM schedules 
                    WHERE is_active = true AND generation_id IS NOT NULL
                    LIMIT 1
                    """,
                    {},
                    fetch=True
                )
                if not active_gen:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("No active schedule found")
                    return agent_pb2.AnalysisResponse()
                generation_id = active_gen[0]['generation_id']
            else:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("No target specified")
                return agent_pb2.AnalysisResponse()
            
            # Get schedules
            schedules = db.execute_query(
                schedule_queries.SELECT_SCHEDULES_BY_GENERATION,
                {'generation_id': generation_id},
                fetch=True
            )
            
            if not schedules:
                return agent_pb2.AnalysisResponse(
                    total_lessons=0,
                    total_score=0
                )
            
            # Convert to list of dicts
            schedules_list = [dict(s) for s in schedules]
            
            # Get unique teacher IDs from schedules
            teacher_ids = list(set(s['teacher_id'] for s in schedules_list))
            
            # Load teacher preferences
            teacher_preferences = {}
            for teacher_id in teacher_ids:
                prefs = db.execute_query(
                    pref_queries.SELECT_TEACHER_PREFERENCES,
                    {'teacher_id': teacher_id},
                    fetch=True
                )
                if prefs:
                    teacher_preferences[teacher_id] = [dict(p) for p in prefs]
                else:
                    teacher_preferences[teacher_id] = []
            
            # Calculate fitness using full fitness function
            fitness_calc = FitnessCalculator()
            fitness_result = fitness_calc.calculate(schedules_list, teacher_preferences)
            
            # Extract metrics from fitness result
            total_score = fitness_result['total_score']
            details = fitness_result['details']
            
            # Build conflict messages from fitness details
            conflict_messages = []
            for conflict in details.get('conflicts', []):
                conflict_messages.append(agent_pb2.Conflict(
                    conflict_type=conflict['type'],
                    day_of_week=conflict.get('day', 0),
                    time_slot=conflict.get('time', 0),
                    description=f"{conflict['type'].title()} conflict"
                ))
            
            # Get isolated lessons
            isolated_lessons = details.get('isolated_lessons', [])
            
            # Get gaps info
            gaps = details.get('gaps', {})
            total_gaps = sum(len(day_gaps) for teacher_gaps in gaps.values() 
                           for day_gaps in teacher_gaps.values())
            
            # Count preference violations
            preference_violations_count = len(details.get('preference_violations', []))
            
            logger.info(f"📊 Schedule Analysis: Score={total_score}, "
                       f"Conflicts={len(conflict_messages)}, "
                       f"PrefViolations={preference_violations_count}, "
                       f"Isolated={len(isolated_lessons)}, "
                       f"Gaps={total_gaps}")
            
            return agent_pb2.AnalysisResponse(
                conflicts=conflict_messages,
                total_lessons=len(schedules_list),
                preference_violations=preference_violations_count,
                isolated_lessons=len(isolated_lessons),
                gaps_count=total_gaps,
                total_score=total_score
            )
            
        except Exception as e:
            logger.error(f"AnalyzeSchedule error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.AnalysisResponse()
    
    def GetMetrics(self, request, context):
        """Get metrics and statistics for generation"""
        try:
            from db.queries import agent_actions as action_queries
            
            # Get generation
            generation = db.execute_query(
                gen_queries.SELECT_GENERATION_BY_JOB_ID,
                {'job_id': request.job_id},
                fetch=True
            )
            
            if not generation:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Generation not found")
                return agent_pb2.MetricsResponse()
            
            gen = generation[0]
            generation_id = gen['id']
            
            # Get score history
            score_history = db.execute_query(
                action_queries.SELECT_SCORE_HISTORY,
                {'generation_id': generation_id},
                fetch=True
            )
            
            score_points = []
            for point in score_history:
                score_points.append(agent_pb2.ScorePoint(
                    iteration=point['iteration'],
                    score=point['score']
                ))
            
            # Get action type statistics
            action_stats = db.execute_query(
                action_queries.SELECT_ACTION_TYPE_STATISTICS,
                {'generation_id': generation_id},
                fetch=True
            )
            
            action_summaries = []
            for stat in action_stats:
                action_summaries.append(agent_pb2.ActionSummary(
                    action_type=stat['action_type'],
                    count=stat['total_count'],
                    avg_score_delta=int(stat.get('avg_score_delta', 0))
                ))
            
            return agent_pb2.MetricsResponse(
                score_history=score_points,
                top_actions=action_summaries
            )
            
        except Exception as e:
            logger.error(f"GetMetrics error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_pb2.MetricsResponse()
    
    def _build_generation_message(self, gen: dict):
        """Build protobuf GenerationHistory message"""
        if agent_pb2 is None:
            return None
        
        return agent_pb2.GenerationHistory(
            id=gen['id'],
            job_id=gen['job_id'],
            stage=gen['stage'],
            stage_name=gen.get('stage_name', ''),
            status=gen['status'],
            current_iteration=gen.get('current_iteration', 0),
            max_iterations=gen.get('max_iterations', 0),
            initial_score=gen.get('initial_score', 0) or 0,
            current_score=gen.get('current_score', 0) or 0,
            best_score=gen.get('best_score', 0) or 0,
            last_reasoning=gen.get('last_reasoning', ''),
            total_actions=gen.get('total_actions', 0),
            started_at=str(gen.get('started_at', '')),
            completed_at=str(gen.get('completed_at', '') or ''),
            duration_seconds=gen.get('duration_seconds', 0) or 0,
            error_message=gen.get('error_message', '') or ''
        )
    
    def _build_schedule_message(self, s: dict):
        """Build protobuf Schedule message"""
        if agent_pb2 is None:
            return None
        
        # Логируем для отладки первые несколько записей
        if s.get('id', 0) <= 110:  # Логируем первые записи
            logger.info(f"_build_schedule_message: id={s.get('id')}, group_id from DB={s.get('group_id')}, type={type(s.get('group_id'))}")
        
        # Проверяем наличие полей в protobuf (могут отсутствовать в старых версиях)
        # Важно: group_id может быть None в БД, нужно обработать это
        group_id = s.get('group_id')
        if group_id is None:
            group_id = 0
        elif isinstance(group_id, str):
            try:
                group_id = int(group_id)
            except (ValueError, TypeError):
                group_id = 0
        
        schedule_kwargs = {
            'id': s['id'],
            'course_load_id': s.get('course_load_id', 0) or 0,
            'day_of_week': s['day_of_week'],
            'time_slot': s['time_slot'],
            'classroom_id': s.get('classroom_id', 0) or 0,
            'classroom_name': s.get('classroom_name', '') or '',
            'teacher_id': s['teacher_id'],
            'teacher_name': s.get('teacher_name', '') or '',
            'group_id': group_id,
            'group_name': s.get('group_name', '') or '',
            'discipline_name': s.get('discipline_name', '') or '',
            'lesson_type': s.get('lesson_type', '') or '',
            'generation_id': s.get('generation_id', 0) or 0,
            'is_active': s.get('is_active', False)
        }
        
        # Добавляем опциональные поля, если они есть в protobuf
        if hasattr(agent_pb2.Schedule, 'week_type'):
            schedule_kwargs['week_type'] = s.get('week_type', 'both') or 'both'
        
        # КРИТИЧНО: Добавляем semester и academic_year
        # Эти поля теперь есть в обновленном protobuf определении (field 15 и 16)
        schedule_semester = s.get('semester')
        if schedule_semester is not None and schedule_semester > 0:
            schedule_kwargs['semester'] = schedule_semester
        else:
            # Если semester отсутствует или равен 0/None, используем значение по умолчанию
            logger.warning(f"Schedule id={s.get('id')}: semester is None/0 in DB ({schedule_semester}), using default 1")
            schedule_kwargs['semester'] = 1
        
        academic_year_val = s.get('academic_year', '') or ''
        if academic_year_val and academic_year_val.strip():
            schedule_kwargs['academic_year'] = academic_year_val.strip()
        else:
            # Если academic_year отсутствует, используем значение по умолчанию
            logger.warning(f"Schedule id={s.get('id')}: academic_year is empty in DB ('{academic_year_val}'), using default 2025/2026")
            schedule_kwargs['academic_year'] = '2025/2026'
        
        # Добавляем week_type, если его нет
        if 'week_type' not in schedule_kwargs:
            schedule_kwargs['week_type'] = s.get('week_type', 'both') or 'both'
        
        # Логируем для отладки первые несколько записей
        if s.get('id') and s.get('id') <= 1300:
            logger.info(f"_build_schedule_message: id={s.get('id')}, semester={schedule_kwargs.get('semester')}, academic_year={schedule_kwargs.get('academic_year')}")
        
        # Создаем protobuf сообщение
        schedule_msg = agent_pb2.Schedule(**schedule_kwargs)
        
        # Логируем для отладки первые несколько записей
        if schedule_msg.id <= 110:
            logger.info(f"_build_schedule_message result: id={schedule_msg.id}, group_id={schedule_msg.group_id}, teacher_id={schedule_msg.teacher_id}")
        
        return schedule_msg

