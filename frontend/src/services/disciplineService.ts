import { AxiosInstance } from 'axios'

export interface CreateDisciplineRequest {
  name: string
  code?: string
  description?: string
  credits?: number
  hours?: number
}

export interface Discipline {
  id: number
  name: string
  code?: string
  description?: string
  credits?: number
  hours?: number
}

export class DisciplineService {
  constructor(private api: AxiosInstance) {}

  async createDiscipline(data: CreateDisciplineRequest) {
    const response = await this.api.post('/api/disciplines', data)
    return response.data
  }

  async getDisciplines(params?: {
    page?: number
    page_size?: number
    search?: string
  }) {
    const response = await this.api.get<{
      disciplines: Discipline[]
      total_count: number
    }>('/api/disciplines', { params })
    return response.data
  }

  async getDiscipline(disciplineId: number) {
    const response = await this.api.get<Discipline>(`/api/disciplines/${disciplineId}`)
    return response.data
  }

  async updateDiscipline(disciplineId: number, data: Partial<CreateDisciplineRequest>) {
    const response = await this.api.put(`/api/disciplines/${disciplineId}`, data)
    return response.data
  }

  async deleteDiscipline(disciplineId: number) {
    const response = await this.api.delete(`/api/disciplines/${disciplineId}`)
    return response.data
  }
}

