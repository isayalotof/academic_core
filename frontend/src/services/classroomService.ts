import { AxiosInstance } from 'axios'

export interface CreateClassroomRequest {
  name: string
  code: string
  building_id: number
  floor: number
  wing?: string
  capacity: number
  actual_area?: number
  classroom_type: 'LECTURE' | 'SEMINAR' | 'COMPUTER_LAB' | 'LABORATORY' | 'WORKSHOP' | 'AUDITORIUM' | 'GYM' | 'LIBRARY'
  has_projector?: boolean
  has_whiteboard?: boolean
  has_computers?: boolean
  computers_count?: number
  is_accessible?: boolean
  description?: string
}

export interface Classroom {
  id: number
  name: string
  code: string
  building_id: number
  building_name?: string
  floor: number
  capacity: number
  classroom_type: string
  has_projector: boolean
  has_computers: boolean
  is_accessible: boolean
}

export interface CreateBuildingRequest {
  name: string
  address?: string
  description?: string
  code?: string
  short_name?: string
  campus?: string
  latitude?: number
  longitude?: number
  total_floors?: number
  has_elevator?: boolean
}

export interface Building {
  id: number
  name: string
  address?: string
  description?: string
}

export class ClassroomService {
  constructor(private api: AxiosInstance) {}

  // Classrooms
  async createClassroom(data: CreateClassroomRequest) {
    const response = await this.api.post<{ success: boolean; classroom: Classroom }>(
      '/api/classrooms',
      data
    )
    return response.data
  }

  async getClassrooms(params?: {
    page?: number
    page_size?: number
    search?: string
    building_ids?: string
    classroom_types?: string
    min_capacity?: number
    max_capacity?: number
    sort_by?: string
    sort_order?: 'ASC' | 'DESC'
  }) {
    const response = await this.api.get<{
      success: boolean
      classrooms: Classroom[]
      total_count: number
      page: number
      page_size: number
    }>('/api/classrooms', { params })
    return response.data
  }

  async getClassroom(classroomId: number) {
    const response = await this.api.get<{ success: boolean; classroom: Classroom }>(
      `/api/classrooms/${classroomId}`
    )
    return response.data
  }

  async updateClassroom(classroomId: number, data: { updates: Partial<CreateClassroomRequest> }) {
    const response = await this.api.put(`/api/classrooms/${classroomId}`, data)
    return response.data
  }

  async deleteClassroom(classroomId: number, hardDelete: boolean = false) {
    const response = await this.api.delete(`/api/classrooms/${classroomId}`, {
      params: { hard_delete: hardDelete },
    })
    return response.data
  }

  // Buildings
  async createBuilding(data: CreateBuildingRequest) {
    // Нужно проверить, есть ли такой эндпоинт в API
    const response = await this.api.post('/api/buildings', data)
    return response.data
  }

  async getBuildings() {
    const response = await this.api.get<{ buildings: Building[] }>('/api/buildings')
    return response.data
  }

  async getBuilding(buildingId: number) {
    const response = await this.api.get<Building>(`/api/buildings/${buildingId}`)
    return response.data
  }

  async updateBuilding(buildingId: number, data: Partial<CreateBuildingRequest>) {
    const response = await this.api.put(`/api/buildings/${buildingId}`, data)
    return response.data
  }

  async deleteBuilding(buildingId: number) {
    const response = await this.api.delete(`/api/buildings/${buildingId}`)
    return response.data
  }
}

