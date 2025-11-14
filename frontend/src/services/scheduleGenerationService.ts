import { AxiosInstance } from 'axios'

export interface GenerateScheduleRequest {
  semester: number
  max_iterations?: number
  skip_stage1?: boolean
  skip_stage2?: boolean
}

export interface GenerateScheduleResponse {
  success: boolean
  job_id: string
  message: string
}

export interface GenerationStatus {
  job_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  stage?: string
  current_iteration?: number
  max_iterations?: number
  current_score?: number
  best_score?: number
  progress_percentage?: number
  last_reasoning?: string
}

export class ScheduleGenerationService {
  constructor(private api: AxiosInstance) {}

  async generateSchedule(data: GenerateScheduleRequest): Promise<GenerateScheduleResponse> {
    const response = await this.api.post<GenerateScheduleResponse>('/api/agent/generate', data)
    return response.data
  }

  async getGenerationStatus(jobId: string): Promise<{ success: boolean; generation: GenerationStatus }> {
    const response = await this.api.get<{ success: boolean; generation: GenerationStatus }>(
      `/api/agent/status/${jobId}`
    )
    return response.data
  }
}

