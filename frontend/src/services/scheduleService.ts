import { AxiosInstance } from 'axios'

export interface Lesson {
  id: number
  day_of_week: number
  time_slot: number
  week_type: 'odd' | 'even' | 'both'
  start_time: string
  end_time: string
  discipline_name: string
  teacher_name: string
  group_id?: number  // КРИТИЧНО: Добавляем group_id для фильтрации дубликатов
  group_name: string
  classroom_name?: string
  building_name?: string
  lesson_type: string
  semester: number
  academic_year: string
  is_active: boolean
}

export interface ScheduleResponse {
  success: boolean
  lessons: Lesson[]
  total_count: number
}

export class ScheduleService {
  constructor(private api: AxiosInstance) {}

  async getGroupSchedule(
    groupId: number,
    semester: number,
    academicYear: string,
    dayOfWeek?: number,
    weekType?: 'odd' | 'even' | 'both'
  ): Promise<Lesson[]> {
    const params: any = {
      semester,
      academic_year: academicYear,
    }
    
    // КРИТИЧНО: dayOfWeek может быть 0 (понедельник), поэтому проверяем на undefined, а не на truthy!
    if (dayOfWeek !== undefined && dayOfWeek !== null) {
      params.day_of_week = dayOfWeek
      console.log(`📤 ScheduleService: Adding day_of_week=${dayOfWeek} to params`)
    } else {
      console.log(`📤 ScheduleService: day_of_week is undefined/null, not adding to params`)
    }
    
    if (weekType) params.week_type = weekType

    console.log(`📤 ScheduleService: API call params:`, params)
    
    const response = await this.api.get<ScheduleResponse>(
      `/api/schedule/group/${groupId}`,
      { params }
    )
    
    return response.data.lessons || []
  }

  async getTeacherSchedule(
    teacherId: number,
    semester: number,
    academicYear: string,
    dayOfWeek?: number,
    weekType?: 'odd' | 'even' | 'both'
  ): Promise<Lesson[]> {
    const params: any = {
      semester,
      academic_year: academicYear,
    }
    
    // КРИТИЧНО: dayOfWeek может быть 0 (понедельник), поэтому проверяем на undefined, а не на truthy!
    if (dayOfWeek !== undefined && dayOfWeek !== null) {
      params.day_of_week = dayOfWeek
      console.log(`📤 ScheduleService.getTeacherSchedule: Adding day_of_week=${dayOfWeek} to params`)
    } else {
      console.log(`📤 ScheduleService.getTeacherSchedule: day_of_week is undefined/null, not adding to params`)
    }
    
    if (weekType) params.week_type = weekType

    console.log(`📤 ScheduleService.getTeacherSchedule: API call params:`, params)

    const response = await this.api.get<ScheduleResponse>(
      `/api/schedule/teacher/${teacherId}`,
      { params }
    )
    
    return response.data.lessons || []
  }

  async getClassroomSchedule(
    classroomId: number,
    semester: number,
    academicYear: string,
    dayOfWeek?: number
  ): Promise<Lesson[]> {
    const params: any = {
      semester,
      academic_year: academicYear,
    }
    
    if (dayOfWeek) params.day_of_week = dayOfWeek

    const response = await this.api.get<ScheduleResponse>(
      `/api/schedule/classroom/${classroomId}`,
      { params }
    )
    
    return response.data.lessons || []
  }

  async searchSchedule(
    query: string,
    semester: number,
    academicYear: string,
    limit: number = 50
  ): Promise<Lesson[]> {
    const response = await this.api.get<ScheduleResponse>(
      '/api/schedule/search',
      {
        params: {
          query,
          semester,
          academic_year: academicYear,
          limit,
        },
      }
    )
    
    return response.data.lessons || []
  }
}

