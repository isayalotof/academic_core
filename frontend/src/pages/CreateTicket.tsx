import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { TicketService, CreateTicketRequest } from '../services/ticketService'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import BackButton from '../components/BackButton'
import MenuButton from '../components/MenuButton'
import { Lesson } from '../services/scheduleService'

const CATEGORIES = [
  'technical',
  'schedule',
  'classroom',
  'other'
]

const PRIORITY_OPTIONS = [
  { value: 1, label: 'Очень низкий' },
  { value: 2, label: 'Низкий' },
  { value: 3, label: 'Средний' },
  { value: 4, label: 'Высокий' },
  { value: 5, label: 'Критический' }
]

const TIME_SLOTS: { [key: number]: string } = {
  1: '08:30 - 10:00',
  2: '10:10 - 11:40',
  3: '11:50 - 13:20',
  4: '13:30 - 15:00',
  5: '15:10 - 16:40',
  6: '16:50 - 18:20',
}

export default function CreateTicket() {
  const navigate = useNavigate()
  const location = useLocation()
  const api = useApi()
  const ticketService = new TicketService(api)
  const { user } = useAuthStore()

  // Получить данные о занятии из state (если переходим из расписания)
  const lesson = location.state?.lesson as Lesson | undefined

  const [formData, setFormData] = useState<CreateTicketRequest>({
    title: '',
    description: '',
    category: lesson ? 'classroom' : 'technical',
    priority: 3
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string>('')
  const [errorMessage, setErrorMessage] = useState<string>('')

  // Предзаполнить форму данными о занятии, если они переданы
  useEffect(() => {
    if (lesson) {
      const timeSlot = TIME_SLOTS[lesson.time_slot as keyof typeof TIME_SLOTS] || `${lesson.time_slot} пара`
      const classroomInfo = lesson.classroom_name 
        ? (lesson.building_name ? `Аудитория: ${lesson.classroom_name} (${lesson.building_name})` : `Аудитория: ${lesson.classroom_name}`)
        : ''
      const disciplineInfo = lesson.discipline_name ? `Дисциплина: ${lesson.discipline_name}` : ''
      const timeInfo = `Время: ${timeSlot}`
      const teacherInfo = lesson.teacher_name ? `Преподаватель: ${lesson.teacher_name}` : ''
      
      const descriptionParts = [
        `Проблема с аудиторией во время занятия:`,
        '',
        timeInfo,
        disciplineInfo,
        teacherInfo,
        classroomInfo,
        '',
        'Опишите проблему:'
      ].filter(Boolean)
      
      setFormData(prev => ({
        ...prev,
        category: 'classroom',
        title: lesson.classroom_name 
          ? `Проблема в аудитории ${lesson.classroom_name}`
          : 'Проблема с аудиторией',
        description: descriptionParts.join('\n')
      }))
    }
  }, [lesson])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.category) {
      setErrorMessage('Пожалуйста, выберите категорию')
      return
    }

    if (!formData.description && !formData.title) {
      setErrorMessage('Пожалуйста, укажите название или описание')
      return
    }

    setIsSubmitting(true)
    setErrorMessage('')
    setSuccessMessage('')
    
    try {
      const ticket = await ticketService.createTicket(formData)
      console.log('Ticket created successfully:', ticket)
      
      if (!ticket || !ticket.id) {
        console.error('Ticket creation failed: ticket is invalid', ticket)
        setErrorMessage('Тикет не был создан. Попробуйте еще раз.')
        setIsSubmitting(false)
        return
      }
      
      // Показываем сообщение об успехе
      setSuccessMessage(`Тикет #${ticket.id} успешно создан!`)
      setIsSubmitting(false)
      
      // Перенаправляем на главную страницу через 2 секунды
      // (так как просмотр тикетов доступен только админам и стаффу)
      setTimeout(() => {
        navigate('/')
      }, 2000)
    } catch (error: any) {
      console.error('Failed to create ticket:', error)
      console.error('Error response:', error.response)
      const errMsg = error.response?.data?.detail || error.message || 'Неизвестная ошибка'
      setErrorMessage('Ошибка создания тикета: ' + errMsg)
      setIsSubmitting(false)
    }
  }

  const handleChange = (field: keyof CreateTicketRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '800px' }}>
        <Flex direction="column" gap="16px">
          {/* Header */}
          <Flex justify="space-between" align="center" wrap="wrap" gap="8px">
            <Flex align="center" gap="12px">
              <BackButton />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Создать тикет
              </Typography>
            </Flex>
            {/* MenuButton removed - not needed on this page */}
          </Flex>

          {/* Информация о занятии, если передана */}
          {lesson && (
            <Panel style={{
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '16px',
              padding: '16px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              border: '2px solid #667eea'
            }}>
              <Typography variant="h3" style={{ marginBottom: '12px', fontSize: '16px', fontWeight: '600', color: '#333' }}>
                Информация о занятии:
              </Typography>
              <Flex direction="column" gap="8px" style={{ fontSize: '14px', color: '#666' }}>
                {lesson.discipline_name && (
                  <Typography style={{ color: '#333' }}>Дисциплина: <strong>{lesson.discipline_name}</strong></Typography>
                )}
                {lesson.classroom_name && (
                  <Typography style={{ color: '#333' }}>
                    Аудитория: <strong>{lesson.classroom_name}</strong>
                    {lesson.building_name && <span> ({lesson.building_name})</span>}
                  </Typography>
                )}
                {lesson.teacher_name && (
                  <Typography style={{ color: '#333' }}>Преподаватель: <strong>{lesson.teacher_name}</strong></Typography>
                )}
                {TIME_SLOTS[lesson.time_slot as keyof typeof TIME_SLOTS] && (
                  <Typography style={{ color: '#333' }}>Время: <strong>{TIME_SLOTS[lesson.time_slot as keyof typeof TIME_SLOTS]}</strong></Typography>
                )}
              </Flex>
            </Panel>
          )}

          {/* Сообщение об успехе */}
          {successMessage && (
            <Panel style={{
              background: 'rgba(76, 175, 80, 0.1)',
              borderRadius: '16px',
              padding: '16px',
              border: '2px solid rgba(76, 175, 80, 0.5)',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
            }}>
              <Typography variant="body1" style={{ color: '#2e7d32', fontSize: '16px', fontWeight: '500', textAlign: 'center' }}>
                ✅ {successMessage}
              </Typography>
            </Panel>
          )}

          {/* Сообщение об ошибке */}
          {errorMessage && (
            <Panel style={{
              background: 'rgba(244, 67, 54, 0.1)',
              borderRadius: '16px',
              padding: '16px',
              border: '2px solid rgba(244, 67, 54, 0.5)',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
            }}>
              <Typography variant="body1" style={{ color: '#c62828', fontSize: '16px', fontWeight: '500', textAlign: 'center' }}>
                ❌ {errorMessage}
              </Typography>
            </Panel>
          )}

          {/* Form */}
          <Panel style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            padding: '20px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <form onSubmit={handleSubmit}>
              <Flex direction="column" gap="16px">
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Название <span style={{ color: '#999' }}>(необязательно)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.title || ''}
                    onChange={(e) => handleChange('title', e.target.value)}
                    placeholder="Краткое описание проблемы"
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      color: '#333'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#667eea'
                      e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)'
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#e0e0e0'
                      e.target.style.boxShadow = 'none'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Описание <span style={{ color: '#f44336' }}>*</span>
                  </label>
                  <textarea
                    value={formData.description || ''}
                    onChange={(e) => handleChange('description', e.target.value)}
                    placeholder="Подробное описание проблемы или запроса"
                    required
                    rows={6}
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      fontFamily: 'inherit',
                      resize: 'vertical',
                      color: '#333'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#667eea'
                      e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)'
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#e0e0e0'
                      e.target.style.boxShadow = 'none'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Категория <span style={{ color: '#f44336' }}>*</span>
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => handleChange('category', e.target.value)}
                    required
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff'
                    }}
                  >
                    {CATEGORIES.map(cat => (
                      <option key={cat} value={cat}>
                        {cat === 'technical' ? 'Техническая проблема' :
                         cat === 'schedule' ? 'Расписание' :
                         cat === 'classroom' ? 'Аудитория' :
                         'Другое'}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Приоритет
                  </label>
                  <select
                    value={formData.priority || 3}
                    onChange={(e) => handleChange('priority', parseInt(e.target.value))}
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff'
                    }}
                  >
                    {PRIORITY_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <Flex gap="12px" style={{ marginTop: '8px' }}>
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    style={{
                      flex: 1,
                      padding: '14px',
                      fontSize: '16px',
                      fontWeight: '600',
                      background: '#4caf50',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '12px',
                      cursor: isSubmitting ? 'not-allowed' : 'pointer',
                      opacity: isSubmitting ? 0.7 : 1
                    }}
                  >
                    {isSubmitting ? 'Создание...' : 'Создать тикет'}
                  </Button>
                  <Button
                    type="button"
                    onClick={() => navigate('/')}
                    style={{
                      flex: 1,
                      padding: '14px',
                      fontSize: '16px',
                      fontWeight: '600',
                      background: '#f5f5f5',
                      color: '#666',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    Отмена
                  </Button>
                </Flex>
              </Flex>
            </form>
          </Panel>
        </Flex>
      </Container>
    </div>
  )
}

