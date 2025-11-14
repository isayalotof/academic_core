import { AxiosInstance } from 'axios'
import { User } from '../store/authStore'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name: string
  primary_role: 'student' | 'teacher' | 'staff' | 'admin'
  teacher_id?: number
  student_group_id?: number
}

export interface AuthResponse {
  success: boolean
  user: User
  tokens: {
    access_token: string
    refresh_token: string
    expires_in: number
    token_type: string
  }
  message?: string
}

export class AuthService {
  constructor(private api: AxiosInstance) {}

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>(
      '/api/auth/login',
      credentials
    )
    return response.data
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>(
      '/api/auth/register',
      data
    )
    return response.data
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<{ success: boolean; user: User }>(
      '/api/auth/me'
    )
    return response.data.user
  }

  async validateToken(): Promise<boolean> {
    try {
      await this.api.post('/api/auth/validate')
      return true
    } catch {
      return false
    }
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>(
      '/api/auth/refresh',
      { refresh_token: refreshToken }
    )
    return response.data
  }
}

