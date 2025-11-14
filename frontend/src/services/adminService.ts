import { AxiosInstance } from 'axios'

export interface CreateTeacherRequest {
  full_name: string
  first_name?: string
  last_name?: string
  middle_name?: string
  email?: string
  phone?: string
  employment_type: 'external' | 'graduate' | 'internal' | 'staff'
  position?: string
  academic_degree?: string
  department?: string
  hire_date?: string
}

export interface Teacher {
  id: number
  full_name: string
  email?: string
  phone?: string
  employment_type: string
  priority: number
  position?: string
  department?: string
  user_id?: number | null
  is_active: boolean
}

export class AdminService {
  constructor(private api: AxiosInstance) {}

  async createTeacher(data: CreateTeacherRequest) {
    const response = await this.api.post<{ success: boolean; teacher: Teacher }>(
      '/api/teachers',
      data
    )
    return response.data
  }

  async getTeachers(params?: {
    page?: number
    page_size?: number
    employment_type?: string
    department?: string
    only_active?: boolean
  }) {
    const response = await this.api.get<{
      teachers: Teacher[]
      total_count: number
      page: number
      page_size: number
    }>('/api/teachers', { params })
    return response.data
  }

  async getTeacher(teacherId: number) {
    // Добавляем timestamp для предотвращения кэширования браузером
    const response = await this.api.get<Teacher>(`/api/teachers/${teacherId}`, {
      params: { _t: Date.now() }
    })
    return response.data
  }

  async updateTeacher(teacherId: number, data: Partial<CreateTeacherRequest>) {
    const response = await this.api.put(`/api/teachers/${teacherId}`, data)
    return response.data
  }

  async deleteTeacher(teacherId: number) {
    const response = await this.api.delete(`/api/teachers/${teacherId}`)
    return response.data
  }
}

