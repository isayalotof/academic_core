import { AxiosInstance } from 'axios'

export interface CreateGroupRequest {
  name: string
  short_name?: string
  year: number
  semester: number
  program_code?: string
  program_name?: string
  specialization?: string
  level: 'bachelor' | 'master' | 'phd'
  curator_teacher_id?: number
}

export interface Group {
  id: number
  name: string
  short_name?: string
  year: number
  semester: number
  size: number
  level: string
  program_name?: string
  is_active: boolean
}

export class GroupService {
  constructor(private api: AxiosInstance) {}

  async createGroup(data: CreateGroupRequest) {
    const response = await this.api.post<{ success: boolean; group: Group }>(
      '/api/groups',
      data
    )
    return response.data
  }

  async getGroups(params?: {
    page?: number
    page_size?: number
    year?: number
    level?: string
    only_active?: boolean
  }) {
    const response = await this.api.get<{
      groups: Group[]
      total_count: number
      page: number
      page_size: number
    }>('/api/groups', { params })
    return response.data
  }

  async getGroup(groupId: number) {
    const response = await this.api.get<Group>(`/api/groups/${groupId}`)
    return response.data
  }

  async updateGroup(groupId: number, data: Partial<CreateGroupRequest>) {
    const response = await this.api.put(`/api/groups/${groupId}`, data)
    return response.data
  }

  async deleteGroup(groupId: number) {
    const response = await this.api.delete(`/api/groups/${groupId}`)
    return response.data
  }

  async getGroupStudents(groupId: number) {
    const response = await this.api.get<{
      group_id: number
      students: any[]
      total_count: number
    }>(`/api/groups/${groupId}/students`)
    return response.data
  }
}

