import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import { useApi } from '../hooks/useApi'
import { TeacherService } from '../services/teacherService'
import BackButton from '../components/BackButton'

const STANDARD_ISSUES = [
  'Проектор не работает',
  'Маркеры отсутствуют/не пишут',
  'Недостаточно посадочных мест',
  'Другое',
]

export default function ClassroomIssueReport() {
  const { lessonId } = useParams<{ lessonId: string }>()
  const navigate = useNavigate()
  const api = useApi()
  const teacherService = new TeacherService(api)

  const [selectedIssues, setSelectedIssues] = useState<string[]>([])
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const toggleIssue = (issue: string) => {
    setSelectedIssues((prev) =>
      prev.includes(issue)
        ? prev.filter((i) => i !== issue)
        : [...prev, issue]
    )
  }

  const handleSubmit = async () => {
    if (selectedIssues.length === 0 && !description.trim()) {
      alert('Выберите хотя бы одну проблему или опишите её')
      return
    }

    if (!lessonId) {
      alert('Ошибка: не указан ID занятия')
      return
    }

    setIsSubmitting(true)
    try {
      const response = await teacherService.reportClassroomIssue(Number(lessonId), {
        issues: selectedIssues,
        description: description.trim() || undefined,
      })

      // Перенаправляем на созданный тикет
      if (response?.ticket?.id) {
        navigate(`/tickets/${response.ticket.id}`)
      } else {
        alert('Сообщение о неисправности отправлено')
        navigate('/tickets')
      }
    } catch (error: any) {
      console.error('Failed to report issue:', error)
      alert('Ошибка при отправке сообщения: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '100%' }}>
        <Flex direction="column" gap="16px">
          <Flex justify="space-between" align="center" wrap="wrap" gap="8px">
            <Flex align="center" gap="8px" style={{ flex: 1, minWidth: '200px' }}>
              <BackButton to="/" />
              <Typography variant="h1" style={{ fontSize: '18px', fontWeight: '600', color: '#fff' }}>
                Сообщить о неисправности
              </Typography>
            </Flex>
          </Flex>

          <Panel style={{ 
            padding: '16px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
          }}>
          <Typography variant="h3" style={{ marginBottom: '16px', fontSize: '16px', fontWeight: '600', color: '#333' }}>
            Выберите проблемы:
          </Typography>

          <Flex direction="column" gap="12px">
            {STANDARD_ISSUES.map((issue) => (
              <Flex
                key={issue}
                align="center"
                gap="12px"
                onClick={() => toggleIssue(issue)}
                style={{
                  padding: '12px 16px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  background: selectedIssues.includes(issue) ? '#e3f2fd' : '#fff',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e: any) => {
                  e.currentTarget.style.borderColor = '#667eea'
                  e.currentTarget.style.transform = 'translateY(-2px)'
                }}
                onMouseLeave={(e: any) => {
                  e.currentTarget.style.borderColor = '#e0e0e0'
                  e.currentTarget.style.transform = 'translateY(0)'
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedIssues.includes(issue)}
                  onChange={() => toggleIssue(issue)}
                  style={{ width: '20px', height: '20px', cursor: 'pointer' }}
                />
                <Typography variant="body1" style={{ fontSize: '14px', color: '#333', fontWeight: '500' }}>{issue}</Typography>
              </Flex>
            ))}
          </Flex>
        </Panel>

          <Panel style={{ 
            padding: '16px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
          }}>
            <Typography variant="h3" style={{ marginBottom: '12px', fontSize: '16px', fontWeight: '600', color: '#333' }}>
              Дополнительное описание:
            </Typography>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Опишите проблему подробнее..."
              style={{
                width: '100%',
                minHeight: '100px',
                padding: '12px',
                fontSize: '14px',
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                fontFamily: 'inherit',
                resize: 'vertical',
                transition: 'all 0.2s',
                color: '#333',
                background: '#fff'
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
          </Panel>

          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || (selectedIssues.length === 0 && !description.trim())}
            style={{ 
              width: '100%',
              padding: '12px 16px',
              background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
              border: 'none',
              color: '#333',
              borderRadius: '10px',
              fontWeight: '600',
              fontSize: '14px',
              minHeight: '44px',
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
            }}
          >
            {isSubmitting ? 'Отправка...' : 'Отправить'}
          </Button>
        </Flex>
      </Container>
    </div>
  )
}

