import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { ClassroomService, CreateClassroomRequest, Building } from '../../services/classroomService'

export default function EditClassroom() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const api = useApi()
  const classroomService = new ClassroomService(api)

  const [formData, setFormData] = useState<CreateClassroomRequest>({
    name: '',
    code: '',
    building_id: 0,
    floor: 1,
    capacity: 30,
    actual_area: 0,
    classroom_type: 'LECTURE',
    has_projector: false,
    has_whiteboard: true,
    has_computers: false,
    computers_count: 0,
    is_accessible: true,
  })
  const [buildings, setBuildings] = useState<Building[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (id) {
      loadClassroom()
      loadBuildings()
    }
  }, [id])

  const loadClassroom = async () => {
    if (!id) return
    setIsLoading(true)
    try {
      const data = await classroomService.getClassroom(Number(id))
      const classroom = data.classroom
      setFormData({
        name: classroom.name,
        code: classroom.code,
        building_id: classroom.building_id,
        floor: classroom.floor,
        capacity: classroom.capacity,
        actual_area: (classroom as any).actual_area || 0,
        classroom_type: classroom.classroom_type.toUpperCase() as any,
        has_projector: classroom.has_projector,
        has_whiteboard: true,
        has_computers: classroom.has_computers,
        computers_count: (classroom as any).computers_count || 0,
        is_accessible: classroom.is_accessible,
      })
    } catch (error) {
      setError('Не удалось загрузить данные аудитории')
    } finally {
      setIsLoading(false)
    }
  }

  const loadBuildings = async () => {
    try {
      const data = await classroomService.getBuildings()
      setBuildings(data.buildings || [])
    } catch (error) {
      console.error('Failed to load buildings:', error)
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
      // Подготовка данных для отправки
      const submitData: any = { ...formData }
      
      // Если нет компьютеров, не отправляем computers_count
      if (!submitData.has_computers) {
        delete submitData.computers_count
      }
      
      // Убеждаемся, что actual_area положительное число
      if (!submitData.actual_area || submitData.actual_area <= 0) {
        setError('Фактическая площадь должна быть положительным числом')
        setIsSaving(false)
        return
      }
      
      await classroomService.updateClassroom(Number(id), { updates: submitData })
      alert('Аудитория успешно обновлена!')
      navigate('/admin/classrooms')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при обновлении аудитории')
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
              <BackButton to="/admin/classrooms" />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Редактировать аудиторию
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
                  Название *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
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
                  Код *
                </label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => handleChange('code', e.target.value)}
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
                  Здание *
                </label>
                <select
                  value={formData.building_id}
                  onChange={(e) => handleChange('building_id', parseInt(e.target.value))}
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
                  {buildings.map((building) => (
                    <option key={building.id} value={building.id}>
                      {building.name}
                    </option>
                  ))}
                </select>
              </div>

              <Flex gap="12px">
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Этаж *
                  </label>
                  <input
                    type="number"
                    value={formData.floor}
                    onChange={(e) => handleChange('floor', parseInt(e.target.value))}
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
                      color: '#333',
                    }}
                  />
                </div>

                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Вместимость *
                  </label>
                  <input
                    type="number"
                    value={formData.capacity}
                    onChange={(e) => handleChange('capacity', parseInt(e.target.value))}
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
                      color: '#333',
                    }}
                  />
                </div>
              </Flex>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                  Тип аудитории *
                </label>
                <select
                  value={formData.classroom_type}
                  onChange={(e) => handleChange('classroom_type', e.target.value)}
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
                  <option value="LECTURE">Лекционная</option>
                  <option value="SEMINAR">Семинарская</option>
                  <option value="LABORATORY">Лаборатория</option>
                  <option value="COMPUTER_LAB">Компьютерный класс</option>
                  <option value="AUDITORIUM">Аудитория</option>
                  <option value="WORKSHOP">Мастерская</option>
                  <option value="GYM">Спортзал</option>
                  <option value="LIBRARY">Библиотека</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                  Фактическая площадь (кв.м) *
                </label>
                <input
                  type="number"
                  value={formData.actual_area || ''}
                  onChange={(e) => handleChange('actual_area', e.target.value ? parseFloat(e.target.value) : 0)}
                  required
                  min="0.01"
                  step="0.01"
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

              <Flex direction="column" gap="8px">
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={formData.has_projector}
                    onChange={(e) => handleChange('has_projector', e.target.checked)}
                  />
                  <span>Есть проектор</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={formData.has_whiteboard}
                    onChange={(e) => handleChange('has_whiteboard', e.target.checked)}
                  />
                  <span>Есть доска</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={formData.has_computers}
                    onChange={(e) => {
                      handleChange('has_computers', e.target.checked)
                      if (!e.target.checked) {
                        handleChange('computers_count', 0)
                      }
                    }}
                  />
                  <span>Есть компьютеры</span>
                </label>
                {formData.has_computers && (
                  <div style={{ marginLeft: '28px', marginTop: '8px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                      Количество компьютеров *
                    </label>
                    <input
                      type="number"
                      value={formData.computers_count || ''}
                      onChange={(e) => handleChange('computers_count', e.target.value ? parseInt(e.target.value) : 0)}
                      required={formData.has_computers}
                      min="1"
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
                )}
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={formData.is_accessible}
                    onChange={(e) => handleChange('is_accessible', e.target.checked)}
                  />
                  <span>Доступна для маломобильных</span>
                </label>
              </Flex>

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
                  onClick={() => navigate('/admin/classrooms')}
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

