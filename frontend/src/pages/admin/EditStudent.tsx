import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { StudentService, CreateStudentRequest } from '../../services/studentService'
import { GroupService } from '../../services/groupService'

export default function EditStudent() {
  const { id } = useParams<{ id: string }>()
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
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (id) {
      loadStudent()
      loadGroups()
    }
  }, [id])

  const loadStudent = async () => {
    if (!id) return
    setIsLoading(true)
    try {
      const student = await studentService.getStudent(Number(id))
      setFormData({
        full_name: student.full_name,
        student_number: student.student_number,
        group_id: student.group_id,
        email: student.email || '',
        status: student.status as any,
      })
    } catch (error) {
      setError('Не удалось загрузить данные студента')
    } finally {
      setIsLoading(false)
    }
  }

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
    if (!id) return

    setError('')
    setIsSaving(true)
    try {
      await studentService.updateStudent(Number(id), formData)
      alert('Студент успешно обновлён!')
      navigate('/admin/students')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при обновлении студента')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <Panel style={{ 
          padding: '32px', 
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '20px',
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
        }}>
          <Typography style={{ color: '#666' }}>Загрузка...</Typography>
        </Panel>
      </div>
    )
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
                Редактировать студента
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
                  disabled={isSaving} 
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
                  {isSaving ? 'Сохранение...' : 'Сохранить'}
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

