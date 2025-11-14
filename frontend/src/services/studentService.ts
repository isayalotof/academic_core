import { AxiosInstance } from 'axios'

export interface CreateStudentRequest {
  full_name: string
  first_name?: string
  last_name?: string
  student_number: string
  group_id: number
  email?: string
  phone?: string
  status?: 'active' | 'academic_leave' | 'expelled' | 'graduated'
}

export interface Student {
  id: number
  full_name: string
  student_number: string
  group_id: number
  group_name?: string
  email?: string
  status: string
}

export class StudentService {
  constructor(private api: AxiosInstance) {}

  async createStudent(data: CreateStudentRequest) {
    const response = await this.api.post<{ success: boolean; student: Student }>(
      '/api/students',
      data
    )
    return response.data
  }

  async getStudents(params?: {
    page?: number
    page_size?: number
    group_id?: number
    status?: string
  }) {
    const response = await this.api.get<{
      students: Student[]
      total_count: number
    }>('/api/students', { params })
    return response.data
  }

  async getStudent(studentId: number) {
    const response = await this.api.get<Student>(`/api/students/${studentId}`)
    return response.data
  }

  async updateStudent(studentId: number, data: Partial<CreateStudentRequest>) {
    const response = await this.api.put(`/api/students/${studentId}`, data)
    return response.data
  }

  async deleteStudent(studentId: number) {
    const response = await this.api.delete(`/api/students/${studentId}`)
    return response.data
  }

  async searchStudents(query: string, limit: number = 20) {
    const response = await this.api.get<{
      students: Student[]
      query: string
      total_found: number
    }>('/api/students/search', {
      params: { q: query, limit },
    })
    return response.data
  }
}

