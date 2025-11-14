import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { TicketService, Ticket, Comment } from '../services/ticketService'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import BackButton from '../components/BackButton'
import MenuButton from '../components/MenuButton'

const PRIORITY_LABELS: { [key: number]: string } = {
  1: 'Очень низкий',
  2: 'Низкий',
  3: 'Средний',
  4: 'Высокий',
  5: 'Критический'
}

const PRIORITY_COLORS: { [key: number]: string } = {
  1: '#9e9e9e',
  2: '#4caf50',
  3: '#2196f3',
  4: '#ff9800',
  5: '#f44336'
}

const STATUS_COLORS: { [key: string]: string } = {
  open: '#2196f3',
  in_progress: '#ff9800',
  resolved: '#4caf50',
  closed: '#9e9e9e'
}

const STATUS_LABELS: { [key: string]: string } = {
  open: 'Открыт',
  in_progress: 'В работе',
  resolved: 'Решен',
  closed: 'Закрыт'
}

const STATUS_OPTIONS = [
  { value: 'open', label: 'Открыт' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'resolved', label: 'Решен' },
  { value: 'closed', label: 'Закрыт' }
]

export default function TicketDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const api = useApi()
  const ticketService = new TicketService(api)
  const { user } = useAuthStore()

  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [comments, setComments] = useState<Comment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [commentText, setCommentText] = useState('')
  const [isSubmittingComment, setIsSubmittingComment] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)

  const isAdmin = user?.role === 'admin' || user?.role === 'staff'
  const canEdit = isAdmin || (ticket && ticket.created_by === user?.id)

  useEffect(() => {
    if (id) {
      loadTicket()
      loadComments()
    }
  }, [id])

  const loadTicket = async () => {
    if (!id) return
    setIsLoading(true)
    try {
      const data = await ticketService.getTicket(parseInt(id))
      setTicket(data)
    } catch (error: any) {
      console.error('Failed to load ticket:', error)
      alert('Ошибка загрузки тикета: ' + (error.response?.data?.detail || error.message))
      navigate('/tickets')
    } finally {
      setIsLoading(false)
    }
  }

  const loadComments = async () => {
    if (!id) return
    try {
      const data = await ticketService.listComments(parseInt(id))
      setComments(data)
    } catch (error: any) {
      console.error('Failed to load comments:', error)
    }
  }

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id || !commentText.trim()) return

    setIsSubmittingComment(true)
    try {
      const newComment = await ticketService.addComment(parseInt(id), commentText.trim())
      setComments(prev => [...prev, newComment])
      setCommentText('')
    } catch (error: any) {
      console.error('Failed to add comment:', error)
      alert('Ошибка добавления комментария: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsSubmittingComment(false)
    }
  }

  const handleUpdateStatus = async (newStatus: string) => {
    if (!id || !ticket) return

    setIsUpdating(true)
    try {
      const updated = await ticketService.updateTicket(parseInt(id), { status: newStatus })
      setTicket(updated)
    } catch (error: any) {
      console.error('Failed to update ticket:', error)
      alert('Ошибка обновления тикета: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsUpdating(false)
    }
  }

  const handleUpdatePriority = async (newPriority: number) => {
    if (!id || !ticket) return

    setIsUpdating(true)
    try {
      const updated = await ticketService.updateTicket(parseInt(id), { priority: newPriority })
      setTicket(updated)
    } catch (error: any) {
      console.error('Failed to update ticket:', error)
      alert('Ошибка обновления тикета: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsUpdating(false)
    }
  }

  const handleCloseTicket = async () => {
    if (!id || !ticket) return

    if (!confirm('Вы уверены, что хотите закрыть этот тикет?')) {
      return
    }

    setIsUpdating(true)
    try {
      const updated = await ticketService.closeTicket(parseInt(id))
      setTicket(updated)
    } catch (error: any) {
      console.error('Failed to close ticket:', error)
      alert('Ошибка закрытия тикета: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsUpdating(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Typography style={{ color: '#fff', fontSize: '18px' }}>Загрузка...</Typography>
      </div>
    )
  }

  if (!ticket) {
    return null
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '1000px' }}>
        <Flex direction="column" gap="16px">
          {/* Header */}
          <Flex justify="space-between" align="center" wrap="wrap" gap="8px">
            <Flex align="center" gap="12px">
              <BackButton />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Тикет #{ticket.id}
              </Typography>
            </Flex>
            {/* MenuButton removed - not needed on this page */}
          </Flex>

          {/* Ticket Info */}
          <Panel style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            padding: '20px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <Flex direction="column" gap="16px">
              <Flex justify="space-between" align="flex-start" wrap="wrap" gap="12px">
                <Flex direction="column" gap="8px" style={{ flex: '1 1 300px' }}>
                  <Typography variant="h2" style={{ fontSize: '20px', fontWeight: '600', color: '#333' }}>
                    {ticket.title}
                  </Typography>
                  <Flex gap="8px" wrap="wrap" align="center">
                    <span
                      style={{
                        padding: '6px 12px',
                        borderRadius: '12px',
                        fontSize: '13px',
                        fontWeight: '500',
                        background: STATUS_COLORS[ticket.status] || '#9e9e9e',
                        color: '#fff'
                      }}
                    >
                      {STATUS_LABELS[ticket.status] || ticket.status}
                    </span>
                    <span
                      style={{
                        padding: '6px 12px',
                        borderRadius: '12px',
                        fontSize: '13px',
                        fontWeight: '500',
                        background: PRIORITY_COLORS[ticket.priority] || '#9e9e9e',
                        color: '#fff'
                      }}
                    >
                      {PRIORITY_LABELS[ticket.priority] || `Приоритет ${ticket.priority}`}
                    </span>
                    <span
                      style={{
                        padding: '6px 12px',
                        borderRadius: '12px',
                        fontSize: '13px',
                        fontWeight: '500',
                        background: '#f5f5f5',
                        color: '#666'
                      }}
                    >
                      {ticket.category}
                    </span>
                  </Flex>
                </Flex>
                {canEdit && (
                  <Flex direction="column" gap="8px" style={{ minWidth: '200px' }}>
                    <label style={{ fontSize: '13px', fontWeight: '500', color: '#666' }}>
                      Статус:
                    </label>
                    <select
                      value={ticket.status}
                      onChange={(e) => handleUpdateStatus(e.target.value)}
                      disabled={isUpdating}
                      style={{
                        width: '100%',
                        padding: '8px',
                        fontSize: '14px',
                        border: '2px solid #e0e0e0',
                        borderRadius: '8px',
                        background: '#fff',
                        cursor: isUpdating ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {STATUS_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                    <label style={{ fontSize: '13px', fontWeight: '500', color: '#666', marginTop: '8px' }}>
                      Приоритет:
                    </label>
                    <select
                      value={ticket.priority}
                      onChange={(e) => handleUpdatePriority(parseInt(e.target.value))}
                      disabled={isUpdating}
                      style={{
                        width: '100%',
                        padding: '8px',
                        fontSize: '14px',
                        border: '2px solid #e0e0e0',
                        borderRadius: '8px',
                        background: '#fff',
                        cursor: isUpdating ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {[1, 2, 3, 4, 5].map(p => (
                        <option key={p} value={p}>{PRIORITY_LABELS[p]}</option>
                      ))}
                    </select>
                    {ticket.status !== 'closed' && (
                      <Button
                        onClick={handleCloseTicket}
                        disabled={isUpdating}
                        style={{
                          width: '100%',
                          padding: '10px',
                          fontSize: '14px',
                          fontWeight: '600',
                          background: '#9e9e9e',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: isUpdating ? 'not-allowed' : 'pointer',
                          opacity: isUpdating ? 0.7 : 1,
                          marginTop: '8px'
                        }}
                      >
                        {isUpdating ? 'Закрытие...' : 'Закрыть тикет'}
                      </Button>
                    )}
                  </Flex>
                )}
              </Flex>

              <div style={{
                padding: '16px',
                background: '#f9f9f9',
                borderRadius: '12px',
                border: '1px solid #e0e0e0'
              }}>
                <Typography style={{ fontSize: '15px', lineHeight: '1.6', color: '#333', whiteSpace: 'pre-wrap' }}>
                  {ticket.description}
                </Typography>
              </div>

              <Flex gap="16px" wrap="wrap" style={{ fontSize: '13px', color: '#333', paddingTop: '12px', borderTop: '1px solid #e0e0e0' }}>
                <span style={{ color: '#333' }}>Создан: <strong style={{ color: '#333' }}>{ticket.created_by_name}</strong> ({formatDate(ticket.created_at)})</span>
                {ticket.assigned_to_name && (
                  <span style={{ color: '#333' }}>Исполнитель: <strong style={{ color: '#333' }}>{ticket.assigned_to_name}</strong></span>
                )}
                <span style={{ color: '#333' }}>Обновлен: {formatDate(ticket.updated_at)}</span>
              </Flex>
            </Flex>
          </Panel>

          {/* Comments */}
          <Panel style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            padding: '20px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <style>{`
              #ticket-comments textarea::placeholder {
                color: #999 !important;
                opacity: 1;
              }
            `}</style>
            <Typography variant="h3" style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#333' }}>
              Комментарии ({comments.length})
            </Typography>

            <Flex direction="column" gap="16px" id="ticket-comments">
              {comments.length === 0 ? (
                <Typography style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
                  Комментариев пока нет
                </Typography>
              ) : (
                comments.map(comment => (
                  <div
                    key={comment.id}
                    style={{
                      padding: '16px',
                      background: comment.user_id === user?.id ? '#e3f2fd' : '#f9f9f9',
                      borderRadius: '12px',
                      border: '1px solid #e0e0e0'
                    }}
                  >
                    <Flex justify="space-between" align="flex-start" gap="12px" wrap="wrap">
                      <Flex direction="column" gap="8px" style={{ flex: '1 1 300px' }}>
                        <Flex align="center" gap="8px">
                          <Typography style={{ fontSize: '14px', fontWeight: '600', color: '#333' }}>
                            {comment.user_name}
                          </Typography>
                          {comment.user_id === ticket.created_by && (
                            <span style={{
                              padding: '2px 8px',
                              borderRadius: '8px',
                              fontSize: '11px',
                              fontWeight: '500',
                              background: '#2196f3',
                              color: '#fff'
                            }}>
                              Автор
                            </span>
                          )}
                        </Flex>
                        <Typography style={{ fontSize: '14px', lineHeight: '1.6', color: '#333', whiteSpace: 'pre-wrap' }}>
                          {comment.content}
                        </Typography>
                        <Typography style={{ fontSize: '12px', color: '#666' }}>
                          {formatDate(comment.created_at)}
                        </Typography>
                      </Flex>
                    </Flex>
                  </div>
                ))
              )}

              {/* Add Comment Form */}
              <form onSubmit={handleAddComment} style={{
                padding: '16px',
                background: '#f5f5f5',
                borderRadius: '12px',
                border: '1px solid #e0e0e0'
              }}>
                <Flex direction="column" gap="12px">
                  <Typography style={{ fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Добавить комментарий:
                  </Typography>
                  <textarea
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    placeholder="Введите ваш комментарий..."
                    rows={4}
                    required
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '14px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px',
                      background: '#fff',
                      fontFamily: 'inherit',
                      resize: 'vertical',
                      color: '#333'
                    }}
                    onFocus={(e) => {
                      e.target.style.setProperty('color', '#333', 'important')
                    }}
                  />
                  <Button
                    type="submit"
                    disabled={isSubmittingComment || !commentText.trim()}
                    style={{
                      alignSelf: 'flex-end',
                      padding: '10px 20px',
                      fontSize: '14px',
                      fontWeight: '600',
                      background: isSubmittingComment || !commentText.trim() ? '#e0e0e0' : '#4caf50',
                      color: isSubmittingComment || !commentText.trim() ? '#666' : '#fff',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: isSubmittingComment || !commentText.trim() ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {isSubmittingComment ? 'Отправка...' : 'Отправить'}
                  </Button>
                </Flex>
              </form>
            </Flex>
          </Panel>
        </Flex>
      </Container>
    </div>
  )
}

