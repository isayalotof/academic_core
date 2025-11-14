import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { GroupService } from '../../services/groupService'
import { ScheduleService, Lesson } from '../../services/scheduleService'
import ScheduleCard from '../../components/ScheduleCard'
import { format, addDays, isToday, isYesterday, isTomorrow } from 'date-fns'
import { ru } from 'date-fns/locale'

const DAYS_OF_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
const TIME_SLOTS = [
  { slot: 1, start: '08:00', end: '09:30' },
  { slot: 2, start: '09:45', end: '11:15' },
  { slot: 3, start: '11:30', end: '13:00' },
  { slot: 4, start: '13:45', end: '15:15' },
  { slot: 5, start: '15:30', end: '17:00' },
  { slot: 6, start: '17:15', end: '18:45' },
]

export default function ViewGroupSchedule() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const api = useApi()
  const groupService = new GroupService(api)
  const scheduleService = new ScheduleService(api)

  const [groups, setGroups] = useState<any[]>([])
  const [selectedGroupId, setSelectedGroupId] = useState<number | null>(null)
  const [selectedGroup, setSelectedGroup] = useState<any | null>(null)
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingSchedule, setIsLoadingSchedule] = useState(false)
  const [currentDayOfWeek, setCurrentDayOfWeek] = useState(new Date().getDay() || 7)

  // Получаем текущий семестр и учебный год
  const currentDate = new Date()
  const semester = currentDate.getMonth() >= 8 ? 1 : 2
  const academicYear = `${currentDate.getFullYear()}/${currentDate.getFullYear() + 1}`

  useEffect(() => {
    loadGroups()
    // Если передан group_id в URL, загружаем его расписание
    const groupIdParam = searchParams.get('group_id')
    if (groupIdParam) {
      const groupId = parseInt(groupIdParam)
      if (!isNaN(groupId)) {
        setSelectedGroupId(groupId)
      }
    }
  }, [])

  useEffect(() => {
    if (selectedGroupId) {
      loadSchedule()
    }
  }, [selectedDate, selectedGroupId])

  const loadGroups = async () => {
    setIsLoading(true)
    try {
      const data = await groupService.getGroups({ page_size: 100, only_active: true })
      setGroups(data.groups || [])
      
      // Если есть group_id в URL, находим группу и загружаем расписание
      const groupIdParam = searchParams.get('group_id')
      if (groupIdParam) {
        const groupId = parseInt(groupIdParam)
        const group = data.groups?.find((g: any) => g.id === groupId)
        if (group) {
          setSelectedGroup(group)
          setSelectedGroupId(groupId)
        }
      }
    } catch (error) {
      console.error('Failed to load groups:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadSchedule = async () => {
    if (!selectedGroupId) return

    setIsLoadingSchedule(true)
    try {
      const dayOfWeek = selectedDate.getDay()  // 0=воскресенье, 1=понедельник, ..., 6=суббота
      
      // КРИТИЧНО: Воскресенье (day 0) не показываем - это выходной день!
      if (dayOfWeek === 0) {
        console.log('🛑 Sunday selected - no schedule (выходной день)')
        setLessons([])
        setIsLoadingSchedule(false)
        return
      }
      
      // Преобразуем: 1 (пн) -> 0 (API), 2 (вт) -> 1 (API), ..., 6 (сб) -> 5 (API)
      const apiDayOfWeek = dayOfWeek - 1
      
      console.log(`📅 Loading schedule for day ${dayOfWeek} (API: ${apiDayOfWeek})`)
      console.log(`📡 API Request: /api/schedule/group/${selectedGroupId}?semester=${semester}&academic_year=${academicYear}&day_of_week=${apiDayOfWeek}`)
      
      const schedule = await scheduleService.getGroupSchedule(
        selectedGroupId,
        semester,
        academicYear,
        apiDayOfWeek  // 0-5 для API (понедельник-суббота)
      )
      
      console.log(`📥 API Response: received ${schedule.length} lessons`)
      
      console.log(`📊 Received ${schedule.length} lessons from API`)
      
      // КРИТИЧЕСКАЯ ПРОВЕРКА: Фильтруем дубликаты и воскресенье перед отображением
      // Дубликаты - это занятия с одинаковым (time_slot, day_of_week, group_id)
      // В один слот в один день для одной группы может быть только одна пара!
      // Также фильтруем воскресенье (day_of_week = 0 или 7)
      const seen = new Set<string>()
      const uniqueSchedule = schedule.filter((lesson) => {
        // Проверка на воскресенье
        if (lesson.day_of_week === 0 || lesson.day_of_week === 7 || lesson.day_of_week < 1 || lesson.day_of_week > 6) {
          console.error(
            `❌ SUNDAY OR INVALID DAY DETECTED in API response! ` +
            `ID=${lesson.id}, day_of_week=${lesson.day_of_week}, ` +
            `discipline: ${lesson.discipline_name}`
          )
          return false
        }
        
        // Проверка на дубликаты по (time_slot, day_of_week, group_id)
        // В один слот в один день для одной группы может быть только одна пара!
        const groupId = lesson.group_id || 'unknown'
        const key = `${lesson.time_slot}-${lesson.day_of_week}-${groupId}`
        if (seen.has(key)) {
          console.error(
            `❌ DUPLICATE DETECTED in API response! ` +
            `Slot ${lesson.time_slot}, day ${lesson.day_of_week}, group ${groupId}, ` +
            `discipline: ${lesson.discipline_name}, id: ${lesson.id}`
          )
          return false
        }
        seen.add(key)
        return true
      })
      
      console.log(`✅ After filtering: ${uniqueSchedule.length} unique lessons`)
      
      // ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Вывести все занятия по слотам для отладки
      const lessonsBySlotDebug: { [key: number]: typeof uniqueSchedule } = {}
      uniqueSchedule.forEach(lesson => {
        if (!lessonsBySlotDebug[lesson.time_slot]) {
          lessonsBySlotDebug[lesson.time_slot] = []
        }
        lessonsBySlotDebug[lesson.time_slot].push(lesson)
      })
      
      // Проверить, есть ли слоты с несколькими занятиями
      Object.keys(lessonsBySlotDebug).forEach(slotStr => {
        const slot = parseInt(slotStr)
        const slotLessons = lessonsBySlotDebug[slot]
        if (slotLessons.length > 1) {
          console.error(
            `❌ CRITICAL: Slot ${slot} has ${slotLessons.length} lessons! ` +
            `Lessons: ${slotLessons.map(l => 
              `id=${l.id}, day=${l.day_of_week}, discipline="${l.discipline_name}"`
            ).join('; ')}`
          )
        }
      })
      
      setLessons(uniqueSchedule)
    } catch (error) {
      console.error('Failed to load schedule:', error)
      setLessons([])
    } finally {
      setIsLoadingSchedule(false)
    }
  }

  const handleGroupChange = (groupId: number) => {
    setSelectedGroupId(groupId)
    const group = groups.find((g) => g.id === groupId)
    setSelectedGroup(group || null)
  }

  const handleDateChange = (days: number) => {
    const newDate = addDays(selectedDate, days)
    setSelectedDate(newDate)
    setCurrentDayOfWeek(newDate.getDay() || 7)
  }

  const getDateLabel = (date: Date) => {
    if (isToday(date)) return 'Сегодня'
    if (isYesterday(date)) return 'Вчера'
    if (isTomorrow(date)) return 'Завтра'
    return format(date, 'd MMMM', { locale: ru })
  }

  // КРИТИЧНО: Правильно преобразуем day_of_week для отображения
  // Date.getDay() возвращает: 0=воскресенье, 1=понедельник, ..., 6=суббота
  // DAYS_OF_WEEK: ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'] (индексы 0-5)
  // Если воскресенье (currentDayOfWeek = 0 или 7), не показываем расписание
  let dayOfWeekName = ''
  if (currentDayOfWeek >= 1 && currentDayOfWeek <= 6) {
    dayOfWeekName = DAYS_OF_WEEK[currentDayOfWeek - 1] || ''
  }

  // КРИТИЧНО: Группируем уроки по парам, проверяя на дубликаты
  const lessonsBySlot = TIME_SLOTS.map((timeSlot) => {
    const slotLessons = lessons.filter(
      (lesson) => lesson.time_slot === timeSlot.slot
    )
    
    // ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ: Вывести все занятия в этом слоте
    if (slotLessons.length > 0) {
      console.log(
        `🔍 Slot ${timeSlot.slot}: ${slotLessons.length} lessons before filtering. ` +
        `Details: ${slotLessons.map(l => 
          `id=${l.id}, day=${l.day_of_week}, group=${l.group_id || 'unknown'}, ` +
          `discipline="${l.discipline_name}"`
        ).join('; ')}`
      )
    }
    
    // КРИТИЧЕСКАЯ ПРОВЕРКА: Проверить дубликаты в слоте и воскресенье
    // В один слот может быть только одна пара!
    // Также проверяем, что день не воскресенье (0 или 7)
    const seen = new Set<string>()
    const uniqueLessons = slotLessons.filter((lesson) => {
      // Проверка на воскресенье
      if (lesson.day_of_week === 0 || lesson.day_of_week === 7 || lesson.day_of_week < 1 || lesson.day_of_week > 6) {
        console.error(
          `❌ SUNDAY OR INVALID DAY DETECTED! Slot ${timeSlot.slot}, day ${lesson.day_of_week}, ` +
          `discipline: ${lesson.discipline_name}, id: ${lesson.id}`
        )
        return false
      }
      
      // Проверка на дубликаты по (day_of_week, group_id)
      // В один слот может быть только одна пара для одной группы!
      const groupId = lesson.group_id || 'unknown'
      const key = `${lesson.day_of_week || 'unknown'}-${groupId}`
      if (seen.has(key)) {
        console.error(
          `❌ DUPLICATE DETECTED on frontend! Slot ${timeSlot.slot}, day ${lesson.day_of_week || 'unknown'}, ` +
          `group ${groupId}, discipline: ${lesson.discipline_name}, id: ${lesson.id}`
        )
        return false  // Пропускаем дубликат
      }
      seen.add(key)
      return true
    })
    
    if (uniqueLessons.length > 1) {
      console.error(
        `❌ CRITICAL: Slot ${timeSlot.slot} has ${uniqueLessons.length} lessons AFTER filtering! ` +
        `This should not happen! Lessons: ${uniqueLessons.map(l => 
          `id=${l.id}, day=${l.day_of_week}, group=${l.group_id || 'unknown'}, ` +
          `discipline="${l.discipline_name}"`
        ).join('; ')}`
      )
      // Оставляем только первое занятие
      console.warn(`⚠️ Keeping only first lesson in slot ${timeSlot.slot}`)
      return {
        ...timeSlot,
        lessons: [uniqueLessons[0]],
      }
    }
    
    return {
      ...timeSlot,
      lessons: uniqueLessons,
    }
  })

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '100%' }}>
        <Flex direction="column" gap="24px">
          {/* Заголовок */}
          <Flex align="center" gap="12px">
            <BackButton />
            <Typography variant="h1" style={{ fontSize: '22px', fontWeight: '600', color: '#fff', flex: 1 }}>
              Расписание группы
            </Typography>
          </Flex>

          {/* Выбор группы */}
          <Panel style={{ 
            padding: '20px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            width: '100%',
          }}>
            <Typography variant="h3" style={{ marginBottom: '16px', fontSize: '18px', fontWeight: '600', color: '#333' }}>
              Выберите группу
            </Typography>
            {isLoading ? (
              <Typography style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
                Загрузка групп...
              </Typography>
            ) : (
              <select
                value={selectedGroupId || ''}
                onChange={(e) => handleGroupChange(parseInt(e.target.value))}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  fontSize: '16px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '12px',
                  background: '#fff',
                  color: '#333',
                  fontWeight: '500',
                  minHeight: '48px',
                }}
              >
                <option value="">-- Выберите группу --</option>
                {groups.map((group) => (
                  <option key={group.id} value={group.id}>
                    {group.name} {group.short_name ? `(${group.short_name})` : ''} - {group.year} курс
                  </option>
                ))}
              </select>
            )}
            {selectedGroup && (
              <div style={{ marginTop: '16px', padding: '12px', background: '#f5f7fa', borderRadius: '10px' }}>
                <Typography style={{ fontSize: '14px', color: '#666', marginBottom: '4px' }}>Выбранная группа</Typography>
                <Typography style={{ fontSize: '16px', fontWeight: '600', color: '#333' }}>
                  {selectedGroup.name} {selectedGroup.short_name ? `(${selectedGroup.short_name})` : ''}
                </Typography>
                <Typography style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
                  {selectedGroup.year} курс, {selectedGroup.level === 'bachelor' ? 'Бакалавриат' : 
                  selectedGroup.level === 'master' ? 'Магистратура' : 
                  selectedGroup.level === 'phd' ? 'Аспирантура' : selectedGroup.level}
                </Typography>
              </div>
            )}
          </Panel>

          {/* Расписание */}
          {selectedGroupId && (
            <>
              {/* Навигация по датам */}
              <Panel style={{ 
                padding: '16px',
                background: 'rgba(255, 255, 255, 0.95)',
                borderRadius: '16px',
                boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
                width: '100%',
              }}>
                <Flex justify="space-between" align="center" wrap="wrap" gap="12px">
                  <Button
                    onClick={() => handleDateChange(-1)}
                    style={{
                      padding: '10px 16px',
                      borderRadius: '10px',
                      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                      border: 'none',
                      color: '#333',
                      fontSize: '14px',
                      fontWeight: '500',
                      minHeight: '40px',
                    }}
                  >
                    ← Назад
                  </Button>
                  <Flex direction="column" align="center" gap="4px">
                    <Typography style={{ fontSize: '16px', fontWeight: '600', color: '#333' }}>
                      {getDateLabel(selectedDate)}
                    </Typography>
                    <Typography style={{ fontSize: '14px', color: '#666' }}>
                      {dayOfWeekName}
                    </Typography>
                  </Flex>
                  <Button
                    onClick={() => handleDateChange(1)}
                    style={{
                      padding: '10px 16px',
                      borderRadius: '10px',
                      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                      border: 'none',
                      color: '#333',
                      fontSize: '14px',
                      fontWeight: '500',
                      minHeight: '40px',
                    }}
                  >
                    Вперёд →
                  </Button>
                </Flex>
              </Panel>

              {/* Список уроков */}
              {isLoadingSchedule ? (
                <Panel style={{ 
                  padding: '40px',
                  background: 'rgba(255, 255, 255, 0.95)',
                  borderRadius: '16px',
                  boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
                  width: '100%',
                  textAlign: 'center',
                }}>
                  <Typography style={{ color: '#666' }}>Загрузка расписания...</Typography>
                </Panel>
              ) : lessons.length === 0 ? (
                <Panel style={{ 
                  padding: '40px',
                  background: 'rgba(255, 255, 255, 0.95)',
                  borderRadius: '16px',
                  boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
                  width: '100%',
                  textAlign: 'center',
                }}>
                  <Typography style={{ color: '#666', fontSize: '16px' }}>
                    На этот день расписания нет
                  </Typography>
                </Panel>
              ) : (
                <Flex direction="column" gap="12px">
                  {lessonsBySlot.map((slot) => (
                    slot.lessons.length > 0 && (
                      <Panel key={slot.slot} style={{ 
                        padding: '16px',
                        background: 'rgba(255, 255, 255, 0.95)',
                        borderRadius: '16px',
                        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
                        width: '100%',
                      }}>
                        <Flex align="center" gap="12px" style={{ marginBottom: '12px' }}>
                          <div style={{
                            padding: '8px 12px',
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            borderRadius: '8px',
                            color: '#fff',
                            fontWeight: '600',
                            fontSize: '14px',
                            minWidth: '80px',
                            textAlign: 'center',
                          }}>
                            {slot.start} - {slot.end}
                          </div>
                          <Typography style={{ fontSize: '14px', color: '#666' }}>
                            {slot.slot} пара
                          </Typography>
                        </Flex>
                        <Flex direction="column" gap="8px">
                          {slot.lessons.map((lesson) => (
                            <ScheduleCard
                              key={lesson.id}
                              lesson={lesson}
                              onReportIssue={() => {}}
                            />
                          ))}
                        </Flex>
                      </Panel>
                    )
                  ))}
                </Flex>
              )}
            </>
          )}
        </Flex>
      </Container>
    </div>
  )
}

