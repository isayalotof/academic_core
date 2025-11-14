import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Container, Flex } from '@maxhub/max-ui'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import { useAuthStore } from '../store/authStore'
import { useApi } from '../hooks/useApi'
import { AuthService } from '../services/authService'

interface Group {
  id: number
  name: string
  short_name?: string
  year?: number
  level?: string
}

interface Teacher {
  id: number
  full_name: string
  email?: string
  position?: string
  department?: string
}

export default function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    primary_role: 'student' as 'student' | 'teacher' | 'staff' | 'admin',
    teacher_id: '',
    student_group_id: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [groups, setGroups] = useState<Group[]>([])
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [isLoadingLists, setIsLoadingLists] = useState(false)
  
  const navigate = useNavigate()
  const { setUser, setTokens } = useAuthStore()
  const api = useApi()
  const authService = new AuthService(api)

  useEffect(() => {
    loadLists()
  }, [])

  const loadLists = async () => {
    setIsLoadingLists(true)
    try {
      // Загрузить группы
      const groupsResponse = await api.get('/api/auth/register/groups')
      console.log('Groups response:', groupsResponse.data)
      if (groupsResponse.data && groupsResponse.data.success) {
        const groupsList = groupsResponse.data.groups || []
        console.log(`Loaded ${groupsList.length} groups`)
        setGroups(groupsList)
      } else {
        console.warn('Groups response does not have success flag')
        setGroups([])
      }

      // Загрузить преподавателей
      const teachersResponse = await api.get('/api/auth/register/teachers')
      console.log('Teachers response:', teachersResponse.data)
      if (teachersResponse.data && teachersResponse.data.success) {
        const teachersList = teachersResponse.data.teachers || []
        console.log(`Loaded ${teachersList.length} teachers`)
        setTeachers(teachersList)
      } else {
        console.warn('Teachers response does not have success flag')
        setTeachers([])
      }
    } catch (err: any) {
      console.error('Error loading lists:', err)
      console.error('Error details:', err.response?.data || err.message)
      // Устанавливаем пустые массивы при ошибке
      setGroups([])
      setTeachers([])
    } finally {
      setIsLoadingLists(false)
    }
  }

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const registerData: any = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        primary_role: formData.primary_role,
      }

      if (formData.primary_role === 'teacher' && formData.teacher_id) {
        registerData.teacher_id = parseInt(formData.teacher_id)
      }
      if (formData.primary_role === 'student' && formData.student_group_id) {
        registerData.student_group_id = parseInt(formData.student_group_id)
      }

      const response = await authService.register(registerData)

      if (response.success) {
        setTokens(
          response.tokens.access_token,
          response.tokens.refresh_token,
          response.tokens.expires_in
        )
        
        // После регистрации обновляем данные пользователя с сервера,
        // чтобы получить актуальный teacher_id или student_group_id после связывания
        try {
          const updatedUser = await authService.getCurrentUser()
          console.log('Updated user after registration:', updatedUser)
          setUser(updatedUser)
        } catch (err) {
          console.warn('Failed to fetch updated user, using response user:', err)
          // Если не удалось обновить, используем данные из ответа
          setUser(response.user)
        }
        
        navigate('/')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка регистрации')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Container
      style={{
        padding: '16px',
        width: '100%',
        maxWidth: '100%',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <div
        style={{
          background: '#ffffff',
          borderRadius: '16px',
          padding: '24px 20px',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.25)',
        }}
      >
        <Typography variant="h1" style={{ marginBottom: '6px', textAlign: 'center', color: '#333', fontSize: '20px' }}>
          Регистрация
        </Typography>
        <Typography variant="body2" style={{ marginBottom: '24px', textAlign: 'center', color: '#666', fontSize: '13px' }}>
          Создайте аккаунт для доступа к системе
        </Typography>

        <form onSubmit={handleSubmit}>
          <Flex direction="column" gap="14px">
            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: '500', color: '#333' }}>
                ФИО *
              </label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => handleChange('full_name', e.target.value)}
                required
                placeholder="Иванов Иван Иванович"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    fontSize: '14px',
                    minHeight: '44px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '10px',
                    transition: 'border-color 0.3s',
                    color: '#333',
                  }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: '500', color: '#333' }}>
                Имя пользователя *
              </label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                required
                placeholder="username"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    fontSize: '14px',
                    minHeight: '44px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '10px',
                    transition: 'border-color 0.3s',
                    color: '#333',
                  }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: '500', color: '#333' }}>
                Email *
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                required
                placeholder="email@example.com"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    fontSize: '14px',
                    minHeight: '44px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '10px',
                    transition: 'border-color 0.3s',
                    color: '#333',
                  }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: '500', color: '#333' }}>
                Пароль *
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                required
                placeholder="Минимум 8 символов"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    fontSize: '14px',
                    minHeight: '44px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '10px',
                    transition: 'border-color 0.3s',
                    color: '#333',
                  }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: '500', color: '#333' }}>
                Роль *
              </label>
              <select
                value={formData.primary_role}
                onChange={(e) => handleChange('primary_role', e.target.value)}
                required
                style={{
                    width: '100%',
                    padding: '10px 12px',
                    fontSize: '14px',
                    minHeight: '44px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '10px',
                    background: '#fff',
                    transition: 'border-color 0.3s',
                    color: '#333',
                  }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
              >
                <option value="student">Студент</option>
                <option value="teacher">Преподаватель</option>
                <option value="staff">Сотрудник</option>
                <option value="admin">Администратор</option>
              </select>
            </div>

            {formData.primary_role === 'teacher' && (
              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: '500', color: '#333' }}>
                  Преподаватель (опционально)
                </label>
                <select
                  value={formData.teacher_id}
                  onChange={(e) => handleChange('teacher_id', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    fontSize: '14px',
                    minHeight: '44px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '10px',
                    background: '#fff',
                    transition: 'border-color 0.3s',
                    color: '#333',
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
                >
                  <option value="">Выберите преподавателя...</option>
                  {isLoadingLists ? (
                    <option value="">Загрузка...</option>
                  ) : (
                    teachers.map((teacher) => (
                      <option key={teacher.id} value={teacher.id.toString()}>
                        {teacher.full_name}
                        {teacher.department && ` - ${teacher.department}`}
                        {teacher.position && ` (${teacher.position})`}
                      </option>
                    ))
                  )}
                </select>
              </div>
            )}

            {formData.primary_role === 'student' && (
              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: '500', color: '#333' }}>
                  Группа (опционально)
                </label>
                <select
                  value={formData.student_group_id}
                  onChange={(e) => handleChange('student_group_id', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    fontSize: '14px',
                    minHeight: '44px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '10px',
                    background: '#fff',
                    transition: 'border-color 0.3s',
                    color: '#333',
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
                >
                  <option value="">Выберите группу...</option>
                  {isLoadingLists ? (
                    <option value="">Загрузка...</option>
                  ) : (
                    groups.map((group) => (
                      <option key={group.id} value={group.id.toString()}>
                        {group.name}
                        {group.short_name && ` (${group.short_name})`}
                        {group.year && ` - ${group.year} курс`}
                        {group.level && ` [${group.level}]`}
                      </option>
                    ))
                  )}
                </select>
              </div>
            )}

            {error && (
              <div
                style={{
                  padding: '12px',
                  background: '#ffebee',
                  borderRadius: '8px',
                  border: '1px solid #f44336',
                }}
              >
                <Typography variant="body2" style={{ color: '#c62828' }}>
                  {error}
                </Typography>
              </div>
            )}

            <Button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                marginTop: '4px',
                padding: '12px 16px',
                fontSize: '14px',
                fontWeight: '600',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                color: '#fff',
                borderRadius: '10px',
                minHeight: '44px',
              }}
            >
              {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
            </Button>

            <div style={{ textAlign: 'center', marginTop: '16px' }}>
              <Typography variant="body2" style={{ color: '#666' }}>
                Уже есть аккаунт?{' '}
                <Link
                  to="/login"
                  style={{
                    color: '#667eea',
                    textDecoration: 'none',
                    fontWeight: '600',
                  }}
                >
                  Войти
                </Link>
              </Typography>
            </div>
          </Flex>
        </form>
      </div>
    </Container>
  )
}

