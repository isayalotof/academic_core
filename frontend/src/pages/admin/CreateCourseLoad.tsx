import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { CourseLoadService, CreateCourseLoadRequest } from '../../services/courseLoadService'
import { AdminService } from '../../services/adminService'
import { GroupService } from '../../services/groupService'

const LESSON_TYPES = ['Лекция', 'Практика', 'Лабораторная', 'Семинар', 'Консультация', 'Экзамен', 'Зачет']

export default function CreateCourseLoad() {
  const navigate = useNavigate()
  const api = useApi()
  const courseLoadService = new CourseLoadService(api)
  const adminService = new AdminService(api)
  const groupService = new GroupService(api)

  const currentDate = new Date()
  const currentYear = currentDate.getFullYear()
  const defaultAcademicYear = `${currentYear}/${currentYear + 1}`

  const [formData, setFormData] = useState<CreateCourseLoadRequest>({
    discipline_name: '',
    discipline_code: '',
    teacher_id: undefined,
    group_id: undefined,
    semester: 1,
    academic_year: defaultAcademicYear,
    hours_per_semester: 0,
    lesson_type: 'Лекция',
    classroom_requirements: '',
  })

  const [teachers, setTeachers] = useState<any[]>([])
  const [groups, setGroups] = useState<any[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadTeachers()
    loadGroups()
  }, [])

  const loadTeachers = async () => {
    try {
      const data = await adminService.getTeachers({ page_size: 100, only_active: true })
      setTeachers(data.teachers)
    } catch (error) {
      console.error('Failed to load teachers:', error)
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
    setError('')
    setIsSubmitting(true)

    try {
      // Удаляем пустые опциональные поля
      const submitData: any = { ...formData }
      if (!submitData.teacher_id) delete submitData.teacher_id
      if (!submitData.group_id) delete submitData.group_id
      if (!submitData.discipline_code) delete submitData.discipline_code
      if (!submitData.classroom_requirements) delete submitData.classroom_requirements

      await courseLoadService.createCourseLoad(submitData)
      alert('Учебная нагрузка успешно создана!')
      navigate('/admin/course-loads')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при создании учебной нагрузки')
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
              <BackButton to="/admin/course-loads" />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Создать учебную нагрузку
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
                    Название дисциплины *
                  </label>
                  <input
                    type="text"
                    value={formData.discipline_name}
                    onChange={(e) => handleChange('discipline_name', e.target.value)}
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
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Код дисциплины
                  </label>
                  <input
                    type="text"
                    value={formData.discipline_code || ''}
                    onChange={(e) => handleChange('discipline_code', e.target.value || undefined)}
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

                <Flex gap="12px" wrap="wrap">
                  <div style={{ flex: 1, minWidth: '200px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                      Преподаватель
                    </label>
                    <select
                      value={formData.teacher_id || ''}
                      onChange={(e) => handleChange('teacher_id', e.target.value ? parseInt(e.target.value) : undefined)}
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '16px',
                        border: '2px solid #e0e0e0',
                        borderRadius: '12px',
                        background: '#fff',
                        transition: 'all 0.2s',
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
                      <option value="">Не выбрано</option>
                      {teachers.map((teacher) => (
                        <option key={teacher.id} value={teacher.id}>
                          {teacher.full_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div style={{ flex: 1, minWidth: '200px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                      Группа
                    </label>
                    <select
                      value={formData.group_id || ''}
                      onChange={(e) => handleChange('group_id', e.target.value ? parseInt(e.target.value) : undefined)}
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '16px',
                        border: '2px solid #e0e0e0',
                        borderRadius: '12px',
                        background: '#fff',
                        transition: 'all 0.2s',
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
                      <option value="">Не выбрано</option>
                      {groups.map((group) => (
                        <option key={group.id} value={group.id}>
                          {group.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </Flex>

                <Flex gap="12px" wrap="wrap">
                  <div style={{ flex: 1, minWidth: '150px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                      Семестр *
                    </label>
                    <select
                      value={formData.semester}
                      onChange={(e) => handleChange('semester', parseInt(e.target.value))}
                      required
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '16px',
                        border: '2px solid #e0e0e0',
                        borderRadius: '12px',
                        background: '#fff',
                        transition: 'all 0.2s',
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
                      {Array.from({ length: 12 }, (_, i) => i + 1).map((sem) => (
                        <option key={sem} value={sem}>
                          Семестр {sem}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div style={{ flex: 1, minWidth: '150px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                      Учебный год *
                    </label>
                    <input
                      type="text"
                      value={formData.academic_year}
                      onChange={(e) => handleChange('academic_year', e.target.value)}
                      required
                      placeholder="2025/2026"
                      pattern="\d{4}/\d{4}"
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '16px',
                        border: '2px solid #e0e0e0',
                        borderRadius: '12px',
                        background: '#fff',
                        transition: 'all 0.2s',
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

                <Flex gap="12px" wrap="wrap">
                  <div style={{ flex: 1, minWidth: '150px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                      Часов в семестр *
                    </label>
                    <input
                      type="number"
                      value={formData.hours_per_semester || ''}
                      onChange={(e) => handleChange('hours_per_semester', e.target.value ? parseInt(e.target.value) : 0)}
                      required
                      min="1"
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '16px',
                        border: '2px solid #e0e0e0',
                        borderRadius: '12px',
                        background: '#fff',
                        transition: 'all 0.2s',
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

                  <div style={{ flex: 1, minWidth: '150px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                      Тип занятия *
                    </label>
                    <select
                      value={formData.lesson_type}
                      onChange={(e) => handleChange('lesson_type', e.target.value)}
                      required
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '16px',
                        border: '2px solid #e0e0e0',
                        borderRadius: '12px',
                        background: '#fff',
                        transition: 'all 0.2s',
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
                      {LESSON_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>
                </Flex>

                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Требования к аудитории
                  </label>
                  <textarea
                    value={formData.classroom_requirements || ''}
                    onChange={(e) => handleChange('classroom_requirements', e.target.value || undefined)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      transition: 'all 0.2s',
                      resize: 'vertical',
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
                    onClick={() => navigate('/admin/course-loads')}
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

