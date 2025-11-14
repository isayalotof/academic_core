import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { TicketService, Ticket } from '../services/ticketService'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import BackButton from '../components/BackButton'
import MenuButton from '../components/MenuButton'

const STATUS_OPTIONS = [
  { value: '', label: 'Все статусы' },
  { value: 'open', label: 'Открыт' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'resolved', label: 'Решен' },
  { value: 'closed', label: 'Закрыт' }
]

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

export default function TicketsList() {
  const navigate = useNavigate()
  const api = useApi()
  const ticketService = new TicketService(api)
  const { user, logout } = useAuthStore()

  const [tickets, setTickets] = useState<Ticket[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    created_by: undefined as number | undefined,  // По умолчанию показываем все тикеты
    assigned_to: undefined as number | undefined
  })
  const [page, setPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const pageSize = 20

  useEffect(() => {
    loadTickets()
  }, [page, filters])

  const loadTickets = async () => {
    setIsLoading(true)
    try {
      const params: any = {
        page,
        page_size: pageSize,
        ...filters
      }
      
      // Удаляем пустые фильтры
      if (!params.status) delete params.status
      if (!params.category) delete params.category
      if (!params.created_by) delete params.created_by
      if (!params.assigned_to) delete params.assigned_to

      const response = await ticketService.listTickets(params)
      setTickets(response.tickets)
      setTotalCount(response.total_count)
    } catch (error: any) {
      console.error('Failed to load tickets:', error)
      alert('Ошибка загрузки тикетов: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsLoading(false)
    }
  }

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1)
  }

  const handleTicketClick = (ticketId: number) => {
    navigate(`/tickets/${ticketId}`)
  }

  const handleCreateTicket = () => {
    navigate('/tickets/create')
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

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '1200px' }}>
        <Flex direction="column" gap="16px">
          {/* Header */}
          <Flex justify="space-between" align="center" wrap="wrap" gap="8px">
            <Flex align="center" gap="12px">
              <BackButton />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Тикеты
              </Typography>
            </Flex>
            <Flex gap="8px" wrap="wrap">
              <Button
                onClick={handleCreateTicket}
                style={{
                  padding: '10px 16px',
                  fontSize: '14px',
                  background: '#4caf50',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '12px',
                  fontWeight: '500',
                  cursor: 'pointer'
                }}
              >
                ➕ Создать тикет
              </Button>
              {/* MenuButton removed - not needed on this page */}
            </Flex>
          </Flex>

          {/* Filters */}
          <Panel style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            padding: '16px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <Flex direction="column" gap="12px">
              <Typography variant="h3" style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px', color: '#333' }}>
                Фильтры
              </Typography>
              <Flex gap="12px" wrap="wrap">
                <div style={{ flex: '1 1 200px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Статус
                  </label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px',
                      fontSize: '14px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px',
                      background: '#fff'
                    }}
                  >
                    {STATUS_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div style={{ flex: '1 1 200px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Категория
                  </label>
                  <input
                    type="text"
                    value={filters.category}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                    placeholder="Все категории"
                    style={{
                      width: '100%',
                      padding: '10px',
                      fontSize: '14px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px'
                    }}
                  />
                </div>
                {user?.role === 'admin' || user?.role === 'staff' ? (
                  <>
                    <div style={{ flex: '1 1 200px' }}>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                        Создатель (ID)
                      </label>
                      <input
                        type="number"
                        value={filters.created_by || ''}
                        onChange={(e) => handleFilterChange('created_by', e.target.value ? parseInt(e.target.value) : undefined)}
                        placeholder="Все"
                        style={{
                          width: '100%',
                          padding: '10px',
                          fontSize: '14px',
                          border: '2px solid #e0e0e0',
                          borderRadius: '8px'
                        }}
                      />
                    </div>
                    <div style={{ flex: '1 1 200px' }}>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                        Исполнитель (ID)
                      </label>
                      <input
                        type="number"
                        value={filters.assigned_to || ''}
                        onChange={(e) => handleFilterChange('assigned_to', e.target.value ? parseInt(e.target.value) : undefined)}
                        placeholder="Все"
                        style={{
                          width: '100%',
                          padding: '10px',
                          fontSize: '14px',
                          border: '2px solid #e0e0e0',
                          borderRadius: '8px'
                        }}
                      />
                    </div>
                  </>
                ) : null}
              </Flex>
            </Flex>
          </Panel>

          {/* Tickets List */}
          <Panel style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            padding: '16px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            {isLoading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Typography style={{ color: '#666', fontSize: '16px' }}>Загрузка...</Typography>
              </div>
            ) : tickets.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Typography style={{ color: '#666', fontSize: '16px' }}>Тикетов не найдено</Typography>
              </div>
            ) : (
              <Flex direction="column" gap="12px">
                {tickets.map(ticket => (
                  <div
                    key={ticket.id}
                    onClick={() => handleTicketClick(ticket.id)}
                    style={{
                      padding: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      background: '#fff'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#667eea'
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.2)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e0e0e0'
                      e.currentTarget.style.boxShadow = 'none'
                    }}
                  >
                    <Flex justify="space-between" align="flex-start" wrap="wrap" gap="12px">
                      <Flex direction="column" gap="8px" style={{ flex: '1 1 300px' }}>
                        <Flex align="center" gap="8px" wrap="wrap">
                          <Typography variant="h3" style={{ fontSize: '16px', fontWeight: '600', color: '#333' }}>
                            #{ticket.id}: {ticket.title}
                          </Typography>
                          <span
                            style={{
                              padding: '4px 12px',
                              borderRadius: '12px',
                              fontSize: '12px',
                              fontWeight: '500',
                              background: STATUS_COLORS[ticket.status] || '#9e9e9e',
                              color: '#fff'
                            }}
                          >
                            {STATUS_LABELS[ticket.status] || ticket.status}
                          </span>
                          <span
                            style={{
                              padding: '4px 12px',
                              borderRadius: '12px',
                              fontSize: '12px',
                              fontWeight: '500',
                              background: PRIORITY_COLORS[ticket.priority] || '#9e9e9e',
                              color: '#fff'
                            }}
                          >
                            {PRIORITY_LABELS[ticket.priority] || `Приоритет ${ticket.priority}`}
                          </span>
                        </Flex>
                        <Typography style={{ fontSize: '14px', color: '#555', lineHeight: '1.5' }}>
                          {ticket.description && ticket.description.length > 150 
                            ? `${ticket.description.substring(0, 150)}...` 
                            : (ticket.description || 'Нет описания')}
                        </Typography>
                        <Flex gap="16px" wrap="wrap" style={{ fontSize: '12px', color: '#666' }}>
                          <span style={{ color: '#666' }}>Категория: <strong style={{ color: '#333' }}>{ticket.category}</strong></span>
                          <span style={{ color: '#666' }}>Создан: <span style={{ color: '#333' }}>{ticket.created_by_name || 'Неизвестно'}</span> ({formatDate(ticket.created_at)})</span>
                          {ticket.assigned_to_name && (
                            <span style={{ color: '#666' }}>Исполнитель: <span style={{ color: '#333' }}>{ticket.assigned_to_name}</span></span>
                          )}
                        </Flex>
                      </Flex>
                    </Flex>
                  </div>
                ))}
              </Flex>
            )}

            {/* Pagination */}
            {totalCount > pageSize && (
              <Flex justify="space-between" align="center" style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #e0e0e0' }}>
                <Typography style={{ fontSize: '14px', color: '#666' }}>
                  Показано {((page - 1) * pageSize) + 1}-{Math.min(page * pageSize, totalCount)} из {totalCount}
                </Typography>
                <Flex gap="8px">
                  <Button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    style={{
                      padding: '8px 16px',
                      fontSize: '14px',
                      background: page === 1 ? '#e0e0e0' : '#667eea',
                      color: page === 1 ? '#999' : '#fff',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: page === 1 ? 'not-allowed' : 'pointer'
                    }}
                  >
                    ← Назад
                  </Button>
                  <Button
                    onClick={() => setPage(p => p + 1)}
                    disabled={page * pageSize >= totalCount}
                    style={{
                      padding: '8px 16px',
                      fontSize: '14px',
                      background: page * pageSize >= totalCount ? '#e0e0e0' : '#667eea',
                      color: page * pageSize >= totalCount ? '#999' : '#fff',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: page * pageSize >= totalCount ? 'not-allowed' : 'pointer'
                    }}
                  >
                    Вперед →
                  </Button>
                </Flex>
              </Flex>
            )}
          </Panel>
        </Flex>
      </Container>
    </div>
  )
}

