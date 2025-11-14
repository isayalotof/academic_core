import { Panel, Flex } from '@maxhub/max-ui'
import { Typography } from './ui/Typography'
import { Button } from './ui/Button'
import { Lesson } from '../services/scheduleService'

interface ScheduleCardProps {
  lesson: Lesson
  onReportIssue?: () => void
}

const TIME_SLOTS = {
  1: '08:30 - 10:00',
  2: '10:10 - 11:40',
  3: '11:50 - 13:20',
  4: '13:30 - 15:00',
  5: '15:10 - 16:40',
  6: '16:50 - 18:20',
}

const DAYS_OF_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

export default function ScheduleCard({ lesson, onReportIssue }: ScheduleCardProps) {
  const timeSlot = TIME_SLOTS[lesson.time_slot as keyof typeof TIME_SLOTS] || `${lesson.start_time} - ${lesson.end_time}`

  return (
    <Panel
      style={{
        width: '100%',
        padding: '14px',
        border: 'none',
        borderRadius: '16px',
        background: 'rgba(255, 255, 255, 0.95)',
        transition: 'all 0.3s ease',
        boxShadow: '0 6px 20px rgba(0, 0, 0, 0.15)',
      }}
      onMouseEnter={(e: any) => {
        e.currentTarget.style.transform = 'translateY(-4px)'
        e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.3)'
      }}
      onMouseLeave={(e: any) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = '0 8px 30px rgba(0, 0, 0, 0.2)'
      }}
    >
      <Flex direction="column" gap="6px">
        {/* Время и тип недели */}
        <Flex justify="space-between" align="center">
          <Typography 
            variant="h3" 
            style={{ 
              fontWeight: 'bold',
              color: '#1a1a1a',
              fontSize: '16px',
            }}
          >
            {timeSlot}
          </Typography>
          {lesson.week_type !== 'both' && (
            <Typography
              variant="body2"
              style={{
                padding: '3px 6px',
                background: lesson.week_type === 'odd' ? '#e3f2fd' : '#fff3e0',
                borderRadius: '4px',
                fontSize: '11px',
                color: lesson.week_type === 'odd' ? '#1976d2' : '#f57c00',
                fontWeight: '500',
              }}
            >
              {lesson.week_type === 'odd' ? 'Нечётная' : 'Чётная'}
            </Typography>
          )}
        </Flex>

        {/* Дисциплина */}
        <Typography 
          variant="h4" 
          style={{ 
            fontWeight: '600',
            color: '#1a1a1a',
            fontSize: '15px',
            lineHeight: '1.4',
          }}
        >
          {lesson.discipline_name || 'Дисциплина не указана'}
        </Typography>

        {/* Преподаватель */}
        <Typography 
          variant="body1" 
          style={{ 
            color: '#333',
            fontSize: '14px',
          }}
        >
          👤 {lesson.teacher_name || 'Преподаватель не указан'}
        </Typography>

        {/* Группа (для студентов) */}
        {lesson.group_name && (
          <Typography 
            variant="body1" 
            style={{ 
              color: '#333',
              fontSize: '14px',
            }}
          >
            👥 {lesson.group_name}
          </Typography>
        )}

        {/* Аудитория */}
        {lesson.classroom_name && (
          <Flex align="center" gap="4px">
            <Typography 
              variant="body1" 
              style={{ 
                color: '#333',
                fontSize: '14px',
              }}
            >
              🏫 {lesson.classroom_name}
            </Typography>
            {lesson.building_name && (
              <Typography 
                variant="body2" 
                style={{ 
                  color: '#666',
                  fontSize: '12px',
                }}
              >
                ({lesson.building_name})
              </Typography>
            )}
          </Flex>
        )}

        {/* Тип занятия */}
        <Typography
          variant="body2"
          style={{
            padding: '4px 8px',
            background: '#f5f5f5',
            borderRadius: '4px',
            display: 'inline-block',
            width: 'fit-content',
            color: '#333',
            fontSize: '12px',
            fontWeight: '500',
          }}
        >
          {lesson.lesson_type === 'lecture' || lesson.lesson_type === 'Лекция' ? 'Лекция' :
           lesson.lesson_type === 'practice' || lesson.lesson_type === 'Практика' ? 'Практика' :
           lesson.lesson_type === 'lab' || lesson.lesson_type === 'Лабораторная' ? 'Лабораторная' :
           lesson.lesson_type === 'seminar' || lesson.lesson_type === 'Семинар' ? 'Семинар' : 
           lesson.lesson_type || 'Занятие'}
        </Typography>

        {/* Кнопка сообщить о проблеме (для преподавателей) */}
        {onReportIssue && (
          <Button
            onClick={onReportIssue}
            style={{
              marginTop: '8px',
              fontSize: '13px',
              padding: '8px 16px',
              minHeight: '36px',
              color: '#7B68EE',
              borderColor: '#7B68EE',
              backgroundColor: 'transparent',
              fontWeight: '500',
            }}
            variant="outline"
          >
            Сообщить о неисправности
          </Button>
        )}
      </Flex>
    </Panel>
  )
}

