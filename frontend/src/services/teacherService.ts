import { AxiosInstance } from 'axios'

export interface TeacherPreference {
  id?: number
  teacher_id: number
  day_of_week: number
  time_slot: number
  is_preferred: boolean
  preference_strength?: 'strong' | 'medium' | 'weak'
  reason?: string
}

export interface SetPreferencesRequest {
  preferences: Omit<TeacherPreference, 'id' | 'teacher_id'>[]
  replace_existing?: boolean
}

export class TeacherService {
  constructor(private api: AxiosInstance) {}

  async getPreferences(teacherId: number) {
    const response = await this.api.get(
      `/api/teachers/${teacherId}/preferences`
    )
    return response.data
  }

  async setPreferences(teacherId: number, data: SetPreferencesRequest) {
    const response = await this.api.post(
      `/api/teachers/${teacherId}/preferences`,
      data
    )
    return response.data
  }

  async clearPreferences(teacherId: number) {
    const response = await this.api.delete(
      `/api/teachers/${teacherId}/preferences`
    )
    return response.data
  }

  async reportClassroomIssue(lessonId: number, issueData: {
    issues: string[]
    description?: string
  }) {
    const response = await this.api.post('/api/tickets', {
      type: 'classroom_issue',
      lesson_id: lessonId,
      category: 'classroom_issue',
      description: issueData.description || '',
      issues: issueData.issues,
      priority: 3, // Средний приоритет
    })
    return response.data
  }
}

