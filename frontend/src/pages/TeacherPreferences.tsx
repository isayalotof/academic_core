import { useState, useEffect, useCallback, useMemo } from 'react'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import BackButton from '../components/BackButton'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useApi } from '../hooks/useApi'
import { TeacherService } from '../services/teacherService'
import { AuthService } from '../services/authService'

const DAYS_OF_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
const TIME_SLOTS = 6

export default function TeacherPreferences() {
  const { user, setUser } = useAuthStore()
  const navigate = useNavigate()
  const api = useApi()
  const teacherService = useMemo(() => new TeacherService(api), [api])
  const authService = useMemo(() => new AuthService(api), [api])

  const [preferences, setPreferences] = useState<Record<string, boolean | null>>({})
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    let isMounted = true
    let teacherId = user?.teacher_id

    const loadPreferences = async () => {
      // Если teacher_id отсутствует, попробуем обновить данные пользователя
      if (!teacherId && user?.id && user?.role === 'teacher') {
        try {
          const updatedUser = await authService.getCurrentUser()
          if (updatedUser.teacher_id && isMounted) {
            setUser(updatedUser)
            teacherId = updatedUser.teacher_id
          }
        } catch (error) {
          console.error('Failed to get current user:', error)
        }
      }

      if (!teacherId) {
        if (isMounted) {
          setIsLoading(false)
        }
        return
      }

      if (isMounted) {
        setIsLoading(true)
      }
      
      try {
        const data = await teacherService.getPreferences(teacherId)
        
        if (!isMounted) return
        
        const prefsMap: Record<string, boolean | null> = {}
        
        // Инициализируем все слоты как null
        for (let day = 1; day <= 6; day++) {
          for (let slot = 1; slot <= TIME_SLOTS; slot++) {
            prefsMap[`${day}-${slot}`] = null
          }
        }

        // Заполняем существующие предпочтения
        if (data.preferences) {
          data.preferences.forEach((pref: any) => {
            prefsMap[`${pref.day_of_week}-${pref.time_slot}`] = pref.is_preferred
          })
        }

        setPreferences(prefsMap)
      } catch (error) {
        console.error('Failed to load preferences:', error)
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadPreferences()

    return () => {
      isMounted = false
    }
  }, [user?.teacher_id, user?.id, user?.role]) // Убрали setUser, teacherService, authService из зависимостей

  const togglePreference = (day: number, slot: number) => {
    const key = `${day}-${slot}`
    const current = preferences[key]
    
    setPreferences((prev) => ({
      ...prev,
      [key]: current === null ? true : current === true ? false : null,
    }))
  }

  const handleSave = async (e?: React.MouseEvent) => {
    e?.preventDefault()
    e?.stopPropagation()

    let teacherId = user?.teacher_id

    // Если teacher_id отсутствует, попробуем обновить данные пользователя
    if (!teacherId && user?.id && user?.role === 'teacher') {
      try {
        const updatedUser = await authService.getCurrentUser()
        if (updatedUser.teacher_id) {
          setUser(updatedUser)
          teacherId = updatedUser.teacher_id
        }
      } catch (error) {
        console.error('Failed to get current user:', error)
      }
    }

    if (!teacherId) {
      alert('Ошибка: не указан ID преподавателя. Пожалуйста, перезайдите в систему.')
      return
    }

    if (isSaving) {
      return // Предотвращаем двойные клики
    }

    setIsSaving(true)
    try {
      const prefsArray = Object.entries(preferences)
        .filter(([_, value]) => value !== null)
        .map(([key, value]) => {
          const [day, slot] = key.split('-').map(Number)
          if (!day || !slot) {
            console.error('Invalid preference key:', key)
            return null
          }
          return {
            day_of_week: day,
            time_slot: slot,
            is_preferred: value === true,
          }
        })
        .filter((pref): pref is { day_of_week: number; time_slot: number; is_preferred: boolean } => pref !== null)

      console.log('Saving preferences:', { teacher_id: teacherId, count: prefsArray.length, preferences: prefsArray })

      // Если нет предпочтений, все равно отправляем запрос для очистки
      const response = await teacherService.setPreferences(teacherId, {
        preferences: prefsArray,
        replace_existing: true,
      })

      console.log('Save response:', response)

      if (response.success !== false) {
        navigate('/')
      } else {
        alert('Ошибка при сохранении предпочтений: ' + (response.message || 'Неизвестная ошибка'))
      }
    } catch (error: any) {
      console.error('Failed to save preferences:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Ошибка при сохранении предпочтений'
      alert('Ошибка при сохранении предпочтений: ' + errorMessage)
    } finally {
      setIsSaving(false)
    }
  }

  const getPreferenceColor = (value: boolean | null) => {
    if (value === true) return '#4caf50' // Зелёный - удобно
    if (value === false) return '#f44336' // Красный - неудобно
    return '#e0e0e0' // Серый - не выбрано
  }

  if (isLoading) {
    return (
      <Container style={{ padding: '16px' }}>
        <Typography>Загрузка...</Typography>
      </Container>
    )
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '100%' }}>
          <Flex direction="column" gap="12px">
          <Flex justify="space-between" align="center" wrap="wrap" gap="8px">
            <Flex align="center" gap="8px" style={{ flex: 1, minWidth: '200px' }}>
              <BackButton to="/" />
              <Typography variant="h1" style={{ fontSize: '18px', fontWeight: '600', color: '#fff' }}>
                Временные предпочтения
              </Typography>
            </Flex>
          </Flex>

          <Panel style={{ 
            padding: '12px', 
            background: 'rgba(255, 243, 205, 0.95)', 
            borderRadius: '12px',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
          }}>
            <Typography variant="body2" style={{ color: '#856404', fontSize: '13px' }}>
              Постараемся учесть ваши пожелания, но это не обязательно.
            </Typography>
          </Panel>

          {/* Сетка предпочтений - вертикальный список для мобильных */}
          <Flex direction="column" gap="10px">
            {DAYS_OF_WEEK.map((dayName, dayIndex) => {
              const day = dayIndex + 1
              return (
                <Panel
                  key={day}
                  style={{
                    padding: '12px',
                    background: 'rgba(255, 255, 255, 0.95)',
                    borderRadius: '16px',
                    boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
                  }}
                >
                  <Typography
                    variant="h4"
                    style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      marginBottom: '10px',
                      color: '#333',
                    }}
                  >
                    {dayName}
                  </Typography>
                  <Flex gap="4px" wrap="wrap">
                    {Array.from({ length: TIME_SLOTS }, (_, slotIndex) => {
                      const slot = slotIndex + 1
                      const key = `${day}-${slot}`
                      const value = preferences[key]
                      return (
                        <div
                          key={slot}
                          onClick={() => togglePreference(day, slot)}
                          style={{
                            flex: '1 1 calc(16.66% - 4px)',
                            minWidth: '40px',
                            maxWidth: '60px',
                            aspectRatio: '1',
                            background: getPreferenceColor(value),
                            borderRadius: '8px',
                            cursor: 'pointer',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'all 0.2s',
                            border: '2px solid transparent',
                            position: 'relative',
                          }}
                          onMouseEnter={(e: any) => {
                            e.currentTarget.style.opacity = '0.8'
                            e.currentTarget.style.transform = 'scale(1.1)'
                            e.currentTarget.style.borderColor = '#667eea'
                            e.currentTarget.style.zIndex = '10'
                          }}
                          onMouseLeave={(e: any) => {
                            e.currentTarget.style.opacity = '1'
                            e.currentTarget.style.transform = 'scale(1)'
                            e.currentTarget.style.borderColor = 'transparent'
                            e.currentTarget.style.zIndex = '1'
                          }}
                        >
                          <div style={{ 
                            fontSize: value === null ? '11px' : '14px', 
                            fontWeight: 'bold',
                            color: value === null ? '#999' : '#fff',
                            lineHeight: '1',
                          }}>
                            {value === true ? '✓' : value === false ? '✗' : slot}
                          </div>
                        </div>
                      )
                    })}
                  </Flex>
                </Panel>
              )
            })}
          </Flex>

          {/* Легенда - компактная */}
          <Panel style={{ 
            padding: '12px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
          }}>
            <Flex gap="12px" wrap="wrap" justify="center">
              <Flex align="center" gap="6px">
                <div
                  style={{
                    width: '20px',
                    height: '20px',
                    background: '#4caf50',
                    borderRadius: '4px',
                  }}
                />
                <Typography variant="body2" style={{ color: '#333', fontSize: '12px' }}>Удобно</Typography>
              </Flex>
              <Flex align="center" gap="6px">
                <div
                  style={{
                    width: '20px',
                    height: '20px',
                    background: '#f44336',
                    borderRadius: '4px',
                  }}
                />
                <Typography variant="body2" style={{ color: '#333', fontSize: '12px' }}>Неудобно</Typography>
              </Flex>
              <Flex align="center" gap="6px">
                <div
                  style={{
                    width: '20px',
                    height: '20px',
                    background: '#e0e0e0',
                    borderRadius: '4px',
                  }}
                />
                <Typography variant="body2" style={{ color: '#333', fontSize: '12px' }}>Не выбрано</Typography>
              </Flex>
            </Flex>
          </Panel>

          <button
            onClick={handleSave}
            disabled={isSaving}
            style={{ 
              width: '100%', 
              padding: '12px 16px',
              background: isSaving 
                ? '#ccc' 
                : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
              border: 'none',
              color: '#333',
              borderRadius: '10px',
              fontWeight: '600',
              fontSize: '14px',
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
              cursor: isSaving ? 'not-allowed' : 'pointer',
              opacity: isSaving ? 0.6 : 1,
              minHeight: '44px',
            }}
          >
            {isSaving ? 'Сохранение...' : 'Сохранить предпочтения'}
          </button>
        </Flex>
      </Container>
    </div>
  )
}

