import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { StudentService, CreateStudentRequest } from '../../services/studentService'
import { GroupService } from '../../services/groupService'

export default function CreateStudent() {
  const navigate = useNavigate()
  const api = useApi()
  const studentService = new StudentService(api)
  const groupService = new GroupService(api)

  const [formData, setFormData] = useState<CreateStudentRequest>({
    full_name: '',
    student_number: '',
    group_id: 0,
    email: '',
    phone: '',
    status: 'active',
  })
  const [groups, setGroups] = useState<any[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadGroups()
  }, [])

  const loadGroups = async () => {
    try {
      const data = await groupService.getGroups({ page_size: 100 })
      setGroups(data.groups)
    } catch (error) {
      console.error('Failed to load groups:', error)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.group_id) {
      setError('Выберите группу')
      return
    }

    setError('')
    setIsSubmitting(true)

    try {
      // Сохраняем статус перед созданием
      const status = formData.status
      // Удаляем статус из данных для создания (backend его не принимает)
      const createData = { ...formData }
      delete createData.status
      
      const result = await studentService.createStudent(createData)
      
      // Если статус был указан и отличается от 'active', обновляем его
      if (status && status !== 'active' && result.student?.id) {
        try {
          await studentService.updateStudent(result.student.id, { status })
        } catch (updateErr) {
          console.warn('Failed to update student status:', updateErr)
          // Не критично, студент уже создан
        }
      }
      
      alert('Студент успешно создан!')
      navigate('/admin/students')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при создании студента')
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
          <Flex justify="space-between" align="center" style={{ width: '100%' }} wrap="wrap" gap="8px">
            <Flex align="center" gap="8px" style={{ flex: 1, minWidth: '200px' }}>
              <BackButton to="/admin/students" />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Создать студента
              </Typography>
            </Flex>
          </Flex>

          <form onSubmit={handleSubmit}>
            <Panel style={{ 
              padding: '24px',
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '20px',
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            }}>
            <Flex direction="column" gap="16px">
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                  ФИО *
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => handleChange('full_name', e.target.value)}
                  required
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      transition: 'all 0.2s',
                      color: '#333',
                    }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                  Номер студенческого билета *
                </label>
                <input
                  type="text"
                  value={formData.student_number}
                  onChange={(e) => handleChange('student_number', e.target.value)}
                  required
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      transition: 'all 0.2s',
                      color: '#333',
                    }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                  Группа *
                </label>
                <select
                  value={formData.group_id}
                  onChange={(e) => handleChange('group_id', parseInt(e.target.value))}
                  required
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      transition: 'all 0.2s',
                      color: '#333',
                    }}
                >
                  <option value="0">Выберите группу</option>
                  {groups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      transition: 'all 0.2s',
                      color: '#333',
                    }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                  Телефон
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      transition: 'all 0.2s',
                      color: '#333',
                    }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                  Статус
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => handleChange('status', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      transition: 'all 0.2s',
                      color: '#333',
                    }}
                >
                  <option value="active">Активный</option>
                  <option value="academic_leave">Академический отпуск</option>
                  <option value="expelled">Отчислен</option>
                  <option value="graduated">Выпущен</option>
                </select>
              </div>

              {error && (
                <div style={{ 
                  padding: '16px', 
                  background: 'rgba(244, 67, 54, 0.1)', 
                  borderRadius: '12px',
                  border: '1px solid rgba(244, 67, 54, 0.3)',
                }}>
                  <Typography variant="body2" style={{ color: '#c62828' }}>
                    {error}
                  </Typography>
                </div>
              )}

              <Flex gap="12px" style={{ marginTop: '8px' }}>
                <Button 
                  type="submit" 
                  disabled={isSubmitting} 
                  style={{ 
                    flex: 1,
                    padding: '16px',
                    background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                    border: 'none',
                    color: '#333',
                    borderRadius: '16px',
                    fontWeight: '600',
                    fontSize: '16px',
                    boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
                  }}
                >
                  {isSubmitting ? 'Создание...' : 'Создать'}
                </Button>
                <Button
                  type="button"
                  onClick={() => navigate('/admin/students')}
                  style={{ 
                    flex: 1,
                    padding: '16px',
                    background: 'rgba(255, 255, 255, 0.8)',
                    border: 'none',
                    color: '#666',
                    borderRadius: '16px',
                    fontWeight: '600',
                    fontSize: '16px',
                  }}
                >
                  Отмена
                </Button>
              </Flex>
            </Flex>
          </Panel>
        </form>
      </Flex>
    </Container>
    </div>
  )
}

