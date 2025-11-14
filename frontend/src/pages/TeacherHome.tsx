import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import { useAuthStore } from '../store/authStore'
import { useApi } from '../hooks/useApi'
import { AuthService } from '../services/authService'
import { ScheduleService, Lesson } from '../services/scheduleService'
import { format, addDays, isToday } from 'date-fns'
import { ru } from 'date-fns/locale'
import ScheduleCard from '../components/ScheduleCard'
import MenuButton from '../components/MenuButton'
import BackButton from '../components/BackButton'

const DAYS_OF_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

export default function TeacherHome() {
  const { user, setUser } = useAuthStore()
  const navigate = useNavigate()
  const api = useApi()
  const authService = new AuthService(api)
  const scheduleService = new ScheduleService(api)

  const [lessons, setLessons] = useState<Lesson[]>([])
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [isLoading, setIsLoading] = useState(true)

  const currentDate = new Date()
  const semester = currentDate.getMonth() >= 8 ? 1 : 2
  const academicYear = `${currentDate.getFullYear()}/${currentDate.getFullYear() + 1}`

  useEffect(() => {
    console.log('📅 TeacherHome useEffect triggered:', { 
      teacher_id: user?.teacher_id, 
      user_id: user?.id,
      role: user?.role,
      selectedDate: selectedDate.toISOString(),
      user_full: user 
    })
    
    // Если teacher_id отсутствует, но пользователь - преподаватель, попробуем обновить данные
    if (!user?.teacher_id && user?.id && user?.role === 'teacher') {
      console.log('⚠️ Teacher ID missing, attempting to refresh user data...')
      authService.getCurrentUser()
        .then(updatedUser => {
          console.log('✅ Refreshed user data:', updatedUser)
          if (updatedUser.teacher_id) {
            console.log(`✅ Setting teacher_id to ${updatedUser.teacher_id}`)
            setUser(updatedUser)
            // После обновления пользователя, loadSchedule будет вызван автоматически через useEffect
          } else {
            console.warn('⚠️ Refreshed user data still has no teacher_id:', updatedUser)
          }
        })
        .catch(error => {
          console.error('❌ Failed to refresh user data:', error)
        })
      // Не вызываем loadSchedule сразу, так как teacher_id отсутствует
      setIsLoading(false)
      return
    }
    
    // Загружаем расписание только если teacher_id есть
    if (user?.teacher_id) {
      loadSchedule()
    } else {
      console.log('⏸️ Skipping schedule load - no teacher_id')
      setIsLoading(false)
    }
  }, [selectedDate, user?.teacher_id, user?.id, user?.role])

  const loadSchedule = async () => {
    console.log('📋 loadSchedule called:', { 
      teacher_id: user?.teacher_id, 
      user_id: user?.id,
      role: user?.role,
      user_full: user 
    })
    
    if (!user?.teacher_id) {
      console.log('⏸️ No teacher_id, skipping schedule load')
      setLessons([])
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    try {
      const dayOfWeek = selectedDate.getDay() || 7
      
      // КРИТИЧНО: Воскресенье (day 0) - выходной день, не показываем расписание!
      if (dayOfWeek === 0) {
        console.log('🛑 Sunday selected - no schedule (выходной день)')
        setLessons([])
        setIsLoading(false)
        return
      }
      
      // Преобразуем: 1 (пн) -> 0 (API), 2 (вт) -> 1 (API), ..., 6 (сб) -> 5 (API)
      const apiDayOfWeek = dayOfWeek - 1
      
      console.log('📡 Loading schedule for teacher:', {
        teacher_id: user.teacher_id,
        semester,
        academicYear,
        dayOfWeek,
        apiDayOfWeek,
        apiUrl: `/api/schedule/teacher/${user.teacher_id}?semester=${semester}&academic_year=${academicYear}&day_of_week=${apiDayOfWeek}`
      })
      
      const schedule = await scheduleService.getTeacherSchedule(
        user.teacher_id,
        semester,
        academicYear,
        apiDayOfWeek
      )
      
      console.log(`✅ Schedule loaded: ${schedule.length} lessons`, schedule)
      setLessons(schedule)
    } catch (error: any) {
      console.error('❌ Failed to load schedule:', error)
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      setLessons([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleDateChange = (days: number) => {
    setSelectedDate(addDays(selectedDate, days))
  }

  const getDateLabel = (date: Date) => {
    if (isToday(date)) return 'Сегодня'
    return format(date, 'd MMMM', { locale: ru })
  }

  const dayOfWeek = selectedDate.getDay() // 0=воскресенье, 1=понедельник, ..., 6=суббота
  const dayOfWeekName = dayOfWeek === 0 ? 'Воскресенье' : (DAYS_OF_WEEK[dayOfWeek - 1] || '')

  const { logout } = useAuthStore()

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '100%' }}>
        <Flex direction="column" gap="16px">
          {/* Заголовок */}
          <Flex justify="space-between" align="center" wrap="wrap" gap="8px">
            <Typography variant="h1" style={{ fontSize: '18px', fontWeight: '600', color: '#fff' }}>
              Моё расписание
            </Typography>
            <Flex direction="column" gap="8px" style={{ width: '100%' }}>
              <Flex gap="8px" wrap="wrap">
                <Button
                  onClick={() => navigate('/tickets/create')}
                  variant="outline"
                  style={{
                    padding: '8px 12px',
                    fontSize: '12px',
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    color: '#fff',
                    borderRadius: '10px',
                    minHeight: '36px',
                  }}
                >
                  🎫 Создать обращение
                </Button>
                <Button
                  onClick={() => navigate('/profile')}
                  variant="outline"
                  style={{
                    padding: '8px 12px',
                    fontSize: '12px',
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    color: '#fff',
                    borderRadius: '10px',
                    minHeight: '36px',
                  }}
                >
                  👤 Профиль
                </Button>
                <Button
                  onClick={logout}
                  variant="outline"
                  style={{
                    padding: '8px 12px',
                    fontSize: '12px',
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    color: '#fff',
                    borderRadius: '10px',
                    minHeight: '36px',
                  }}
                >
                  Выйти
                </Button>
              </Flex>
              <Button
                onClick={() => navigate('/preferences')}
                variant="outline"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  fontSize: '12px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  color: '#fff',
                  borderRadius: '10px',
                  minHeight: '36px',
                }}
              >
                Временные предпочтения
              </Button>
            </Flex>
          </Flex>

          {/* Навигация по датам */}
          <Flex gap="8px" wrap="wrap">
            <Button 
              onClick={() => handleDateChange(-1)} 
              style={{ 
                flex: 1,
                minWidth: '50px',
                padding: '12px 16px',
                borderRadius: '10px',
                border: 'none',
                background: 'rgba(255, 255, 255, 0.95)',
                color: '#333',
                fontSize: '16px',
                fontWeight: '600',
                transition: 'all 0.2s',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
                minHeight: '44px',
              }}
              onMouseEnter={(e: any) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.15)'
              }}
              onMouseLeave={(e: any) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.1)'
              }}
            >
              ←
            </Button>
            <Panel style={{ 
              flex: 2, 
              minWidth: '180px',
              width: '100%',
              padding: '16px', 
              textAlign: 'center',
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '16px',
              boxShadow: '0 6px 20px rgba(0, 0, 0, 0.15)',
            }}>
              <Typography variant="h3" style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px', color: '#333' }}>
                {getDateLabel(selectedDate)}
              </Typography>
              <Typography variant="body2" style={{ color: '#666', fontSize: '12px' }}>
                {dayOfWeekName}
              </Typography>
            </Panel>
            <Button 
              onClick={() => handleDateChange(1)} 
              style={{ 
                flex: 1,
                minWidth: '50px',
                padding: '12px 16px',
                borderRadius: '10px',
                border: 'none',
                background: 'rgba(255, 255, 255, 0.95)',
                color: '#333',
                fontSize: '16px',
                fontWeight: '600',
                transition: 'all 0.2s',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
                minHeight: '44px',
              }}
              onMouseEnter={(e: any) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.15)'
              }}
              onMouseLeave={(e: any) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.1)'
              }}
            >
              →
            </Button>
          </Flex>

          {/* Расписание */}
          {isLoading ? (
            <Panel style={{ 
              width: '100%',
              padding: '24px 16px', 
              textAlign: 'center',
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '16px',
              boxShadow: '0 6px 20px rgba(0, 0, 0, 0.15)',
            }}>
              <Typography style={{ color: '#666', fontSize: '14px' }}>Загрузка...</Typography>
            </Panel>
          ) : lessons.length === 0 ? (
            <Panel style={{ 
              width: '100%',
              padding: '24px 16px', 
              textAlign: 'center',
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '16px',
              boxShadow: '0 6px 20px rgba(0, 0, 0, 0.15)',
            }}>
              <Typography style={{ color: '#666', fontSize: '14px' }}>На этот день занятий нет</Typography>
            </Panel>
          ) : (
            <Flex direction="column" gap="12px" style={{ width: '100%' }}>
              {lessons.map((lesson) => (
                <div key={lesson.id} style={{ width: '100%' }}>
                  <ScheduleCard
                    lesson={lesson}
                    onReportIssue={() => navigate('/tickets/create', { state: { lesson } })}
                  />
                </div>
              ))}
            </Flex>
          )}
        </Flex>
      </Container>
    </div>
  )
}

