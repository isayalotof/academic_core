import { AxiosInstance } from 'axios'

export interface Ticket {
  id: number
  title: string
  description: string
  category: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  created_by: number
  created_by_name: string
  assigned_to?: number | null
  assigned_to_name?: string | null
  priority: number // 1-5
  created_at: string
  updated_at: string
}

export interface Comment {
  id: number
  ticket_id: number
  user_id: number
  user_name: string
  content: string
  created_at: string
}

export interface CreateTicketRequest {
  title?: string
  description?: string
  category: string
  priority?: number // 1-5, default 3
  type?: string // e.g., 'classroom_issue'
  lesson_id?: number
  issues?: string[]
}

export interface TicketsListResponse {
  success: boolean
  tickets: Ticket[]
  total_count: number
}

export interface TicketResponse {
  success: boolean
  ticket: Ticket
  message?: string
}

export interface CommentsResponse {
  success: boolean
  comments: Comment[]
  total_count: number
}

export interface CommentResponse {
  success: boolean
  comment: Comment
  message?: string
}

export class TicketService {
  constructor(private api: AxiosInstance) {}

  /**
   * Создать новый тикет
   */
  async createTicket(data: CreateTicketRequest): Promise<Ticket> {
    const response = await this.api.post<TicketResponse>('/api/tickets', data)
    console.log('Create ticket response:', response.data)
    
    // Проверяем, что ticket существует в ответе
    if (!response.data.ticket) {
      console.error('Ticket not found in response:', response.data)
      throw new Error('Тикет не найден в ответе сервера')
    }
    
    return response.data.ticket
  }

  /**
   * Получить список тикетов с фильтрацией
   */
  async listTickets(params: {
    page?: number
    page_size?: number
    created_by?: number
    assigned_to?: number
    status?: string
    category?: string
  } = {}): Promise<TicketsListResponse> {
    const response = await this.api.get<TicketsListResponse>('/api/tickets', { params })
    return response.data
  }

  /**
   * Получить тикет по ID
   */
  async getTicket(ticketId: number): Promise<Ticket> {
    const response = await this.api.get<TicketResponse>(`/api/tickets/${ticketId}`)
    return response.data.ticket
  }

  /**
   * Обновить тикет
   */
  async updateTicket(
    ticketId: number,
    updates: {
      status?: string
      assigned_to?: number
      priority?: number
    }
  ): Promise<Ticket> {
    const params = new URLSearchParams()
    if (updates.status) params.append('status', updates.status)
    if (updates.assigned_to !== undefined) params.append('assigned_to', updates.assigned_to.toString())
    if (updates.priority !== undefined) params.append('priority', updates.priority.toString())

    const response = await this.api.patch<TicketResponse>(`/api/tickets/${ticketId}?${params.toString()}`)
    return response.data.ticket
  }

  /**
   * Закрыть тикет
   */
  async closeTicket(ticketId: number): Promise<Ticket> {
    return this.updateTicket(ticketId, { status: 'closed' })
  }

  /**
   * Добавить комментарий к тикету
   */
  async addComment(ticketId: number, content: string): Promise<Comment> {
    const response = await this.api.post<CommentResponse>(`/api/tickets/${ticketId}/comments`, {
      content
    })
    return response.data.comment
  }

  /**
   * Получить список комментариев для тикета
   */
  async listComments(ticketId: number): Promise<Comment[]> {
    const response = await this.api.get<CommentsResponse>(`/api/tickets/${ticketId}/comments`)
    return response.data.comments
  }
}

