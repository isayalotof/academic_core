import { AxiosInstance } from 'axios'

export interface CreateCourseLoadRequest {
  teacher_id?: number
  group_id?: number
  discipline_id?: number
  discipline_name: string
  discipline_code?: string
  semester: number
  academic_year: string
  hours_per_semester: number
  lesson_type: string
  classroom_requirements?: string
}

export interface CourseLoad {
  id: number
  discipline_name: string
  discipline_code?: string
  teacher_id?: number
  teacher_name?: string
  group_id?: number
  group_name?: string
  lesson_type: string
  hours_per_semester: number
  lessons_per_week?: number
  semester: number
  academic_year: string
  classroom_requirements?: string
  created_at?: string
}

export class CourseLoadService {
  constructor(private api: AxiosInstance) {}

  async createCourseLoad(data: CreateCourseLoadRequest) {
    const response = await this.api.post<{
      success: boolean
      course_load: CourseLoad
      message: string
    }>('/api/course-loads', data)
    return response.data
  }

  async getCourseLoads(params?: {
    page?: number
    page_size?: number
    semester?: number
    academic_year?: string
    teacher_id?: number
    group_id?: number
  }) {
    const response = await this.api.get<{
      success: boolean
      course_loads: CourseLoad[]
      total_count: number
      page: number
      page_size: number
    }>('/api/course-loads', { params })
    return response.data
  }

  async deleteCourseLoad(loadId: number) {
    const response = await this.api.delete<{
      success: boolean
      message: string
    }>(`/api/course-loads/${loadId}`)
    return response.data
  }
}

