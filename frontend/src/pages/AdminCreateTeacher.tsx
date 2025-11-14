import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import BackButton from '../components/BackButton'
import { useApi } from '../hooks/useApi'
import { AdminService, CreateTeacherRequest } from '../services/adminService'

export default function AdminCreateTeacher() {
  const navigate = useNavigate()
  const api = useApi()
  const adminService = new AdminService(api)

  const [formData, setFormData] = useState<CreateTeacherRequest>({
    full_name: '',
    first_name: '',
    last_name: '',
    middle_name: '',
    email: '',
    phone: '',
    employment_type: 'external',
    position: '',
    academic_degree: '',
    department: '',
    hire_date: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.full_name.trim()) {
      setError('ФИО обязательно для заполнения')
      return
    }

    setIsSubmitting(true)
    try {
      await adminService.createTeacher(formData)
      alert('Преподаватель успешно создан!')
      navigate('/admin/teachers')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при создании преподавателя')
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
              <BackButton to="/admin/teachers" />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Создать преподавателя
              </Typography>
            </Flex>
          </Flex>

          <form onSubmit={handleSubmit}>
            <Flex direction="column" gap="16px">
              <Panel style={{ 
                padding: '24px',
                background: 'rgba(255, 255, 255, 0.95)',
                borderRadius: '20px',
                boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
              }}>
              <Typography variant="h3" style={{ marginBottom: '12px', color: '#333' }}>
                Основная информация
              </Typography>

              <Flex direction="column" gap="12px">
                <div>
                  <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', color: '#333', fontWeight: '500' }}>
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
                  <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', color: '#333', fontWeight: '500' }}>
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
                  <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', color: '#333', fontWeight: '500' }}>
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
                  <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', color: '#333', fontWeight: '500' }}>
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
                    onFocus={(e) => {
                      e.target.style.borderColor = '#667eea'
                      e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)'
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#e0e0e0'
                      e.target.style.boxShadow = 'none'
                    }}
                  >
                    <option value="external">Внешний</option>
                    <option value="graduate">Аспирант</option>
                    <option value="internal">Внутренний</option>
                    <option value="staff">Сотрудник</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', color: '#333', fontWeight: '500' }}>
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
                  <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', color: '#333', fontWeight: '500' }}>
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
              </Flex>
            </Panel>

              {error && (
                <Panel style={{ 
                  padding: '16px', 
                  background: 'rgba(244, 67, 54, 0.1)', 
                  borderRadius: '12px',
                  border: '1px solid rgba(244, 67, 54, 0.3)',
                }}>
                  <Typography variant="body2" style={{ color: '#c62828' }}>
                    {error}
                  </Typography>
                </Panel>
              )}

              <Button
                type="submit"
                disabled={isSubmitting}
                style={{ 
                  width: '100%',
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
                {isSubmitting ? 'Создание...' : 'Создать преподавателя'}
              </Button>
            </Flex>
          </form>
        </Flex>
      </Container>
    </div>
  )
}

