import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { AdminService, CreateTeacherRequest } from '../../services/adminService'

export default function EditTeacher() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const api = useApi()
  const adminService = new AdminService(api)

  const [formData, setFormData] = useState<CreateTeacherRequest>({
    full_name: '',
    email: '',
    phone: '',
    employment_type: 'external',
    position: '',
    department: '',
  })
  const [teacher, setTeacher] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (id) {
      loadTeacher()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])
  
  // Перезагружаем данные при возвращении на страницу (например, из браузерного кэша)
  useEffect(() => {
    const handleFocus = () => {
      if (id && !isLoading) {
        console.log('🔄 Page focused, reloading teacher data...')
        loadTeacher()
      }
    }
    
    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, isLoading])

  const loadTeacher = async () => {
    if (!id) return
    setIsLoading(true)
    try {
      const teacherData = await adminService.getTeacher(Number(id))
      setTeacher(teacherData) // Сохраняем полные данные преподавателя
      setFormData({
        full_name: teacherData.full_name,
        email: teacherData.email || '',
        phone: teacherData.phone || '',
        employment_type: teacherData.employment_type as any,
        position: teacherData.position || '',
        department: teacherData.department || '',
      })
    } catch (error) {
      setError('Не удалось загрузить данные преподавателя')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return

    setError('')
    setIsSaving(true)
    try {
      await adminService.updateTeacher(Number(id), formData)
      alert('Преподаватель успешно обновлён!')
      navigate('/admin/teachers')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при обновлении преподавателя')
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
              <BackButton to="/admin/teachers" />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Редактировать преподавателя
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
                  Тип занятости *
                </label>
                <select
                  value={formData.employment_type}
                  onChange={(e) => handleChange('employment_type', e.target.value)}
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
                  <option value="external">Внешний</option>
                  <option value="graduate">Аспирант</option>
                  <option value="internal">Внутренний</option>
                  <option value="staff">Сотрудник</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                  Должность
                </label>
                <input
                  type="text"
                  value={formData.position}
                  onChange={(e) => handleChange('position', e.target.value)}
                  placeholder="Например: Профессор"
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
                  Кафедра
                </label>
                <input
                  type="text"
                  value={formData.department}
                  onChange={(e) => handleChange('department', e.target.value)}
                  placeholder="Например: Кафедра ПИвКД"
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
                  ID пользователя (user_id)
                </label>
                <input
                  type="text"
                  value={teacher?.user_id || 'Не связан'}
                  disabled
                  style={{
                    width: '100%',
                    padding: '12px',
                    fontSize: '16px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '12px',
                    background: '#f5f5f5',
                    color: teacher?.user_id ? '#333' : '#999',
                    cursor: 'not-allowed',
                  }}
                />
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
                  onClick={() => navigate('/admin/teachers')}
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

