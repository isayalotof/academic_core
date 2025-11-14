import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import BackButton from '../components/BackButton'
import { useAuthStore } from '../store/authStore'
import { useApi } from '../hooks/useApi'
import { AdminService } from '../services/adminService'
import { GroupService } from '../services/groupService'
import { StudentService } from '../services/studentService'
import { ClassroomService } from '../services/classroomService'

export default function AdminHome() {
  const navigate = useNavigate()
  const { logout } = useAuthStore()
  const api = useApi()
  const adminService = new AdminService(api)
  const groupService = new GroupService(api)
  const studentService = new StudentService(api)
  const classroomService = new ClassroomService(api)

  const [stats, setStats] = useState({
    teachers: 0,
    groups: 0,
    students: 0,
    classrooms: 0,
    buildings: 0,
  })

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [teachersData, groupsData, studentsData, classroomsData, buildingsData] = await Promise.allSettled([
        adminService.getTeachers({ page_size: 1 }),
        groupService.getGroups({ page_size: 1 }),
        studentService.getStudents({ page_size: 1 }),
        classroomService.getClassrooms({ page_size: 1 }),
        classroomService.getBuildings(),
      ])
      
      setStats({
        teachers: teachersData.status === 'fulfilled' ? teachersData.value.total_count : 0,
        groups: groupsData.status === 'fulfilled' ? groupsData.value.total_count : 0,
        students: studentsData.status === 'fulfilled' ? studentsData.value.total_count : 0,
        classrooms: classroomsData.status === 'fulfilled' ? (classroomsData.value.total_count || 0) : 0,
        buildings: buildingsData.status === 'fulfilled' ? (buildingsData.value.buildings?.length || 0) : 0,
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '100%' }}>
        <Flex direction="column" gap="24px">
          {/* Заголовок */}
          <Flex direction="column" gap="12px" style={{ width: '100%' }}>
            <Typography variant="h1" style={{ fontSize: '22px', fontWeight: '600', color: '#fff' }}>
              Панель администратора
            </Typography>
            <Flex gap="8px" wrap="wrap">
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
          </Flex>

          {/* Статистика */}
          <Panel style={{ 
            padding: '16px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            width: '100%',
          }}>
            <Typography variant="h3" style={{ marginBottom: '16px', fontSize: '16px', fontWeight: '600', color: '#333' }}>
              Статистика
            </Typography>
            <Flex direction="column" gap="12px" style={{ alignItems: 'center' }}>
              <Flex justify="space-between" align="center" style={{ padding: '12px 16px', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', borderRadius: '10px', width: '95%' }}>
                <Typography style={{ fontSize: '14px', fontWeight: '500', color: '#333' }}>Преподавателей:</Typography>
                <Typography variant="h3" style={{ fontSize: '22px', fontWeight: '700', color: '#667eea' }}>{stats.teachers}</Typography>
              </Flex>
              <Flex justify="space-between" align="center" style={{ padding: '12px 16px', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', borderRadius: '10px', width: '95%' }}>
                <Typography style={{ fontSize: '14px', fontWeight: '500', color: '#333' }}>Групп:</Typography>
                <Typography variant="h3" style={{ fontSize: '22px', fontWeight: '700', color: '#667eea' }}>{stats.groups}</Typography>
              </Flex>
              <Flex justify="space-between" align="center" style={{ padding: '12px 16px', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', borderRadius: '10px', width: '95%' }}>
                <Typography style={{ fontSize: '14px', fontWeight: '500', color: '#333' }}>Студентов:</Typography>
                <Typography variant="h3" style={{ fontSize: '22px', fontWeight: '700', color: '#667eea' }}>{stats.students}</Typography>
              </Flex>
              <Flex justify="space-between" align="center" style={{ padding: '12px 16px', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', borderRadius: '10px', width: '95%' }}>
                <Typography style={{ fontSize: '14px', fontWeight: '500', color: '#333' }}>Аудиторий:</Typography>
                <Typography variant="h3" style={{ fontSize: '22px', fontWeight: '700', color: '#667eea' }}>{stats.classrooms}</Typography>
              </Flex>
              <Flex justify="space-between" align="center" style={{ padding: '12px 16px', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', borderRadius: '10px', width: '95%' }}>
                <Typography style={{ fontSize: '14px', fontWeight: '500', color: '#333' }}>Зданий:</Typography>
                <Typography variant="h3" style={{ fontSize: '22px', fontWeight: '700', color: '#667eea' }}>{stats.buildings}</Typography>
              </Flex>
            </Flex>
          </Panel>

          {/* Управление */}
          <Panel style={{ 
            padding: '16px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            width: '100%',
          }}>
            <Typography variant="h3" style={{ marginBottom: '16px', fontSize: '16px', fontWeight: '600', color: '#333' }}>
              Управление
            </Typography>
            <Flex direction="column" gap="12px" style={{ alignItems: 'center' }}>
              {[
                { icon: '🎫', label: 'Тикеты', path: '/tickets' },
                { icon: '👨‍🏫', label: 'Преподаватели', path: '/admin/teachers' },
                { icon: '👥', label: 'Группы', path: '/admin/groups' },
                { icon: '🎓', label: 'Студенты', path: '/admin/students' },
                { icon: '🏫', label: 'Аудитории', path: '/admin/classrooms' },
                { icon: '🏢', label: 'Здания', path: '/admin/buildings' },
                { icon: '📊', label: 'Учебная нагрузка', path: '/admin/course-loads' },
                { icon: '📅', label: 'Генерация расписания', path: '/admin/schedule/generate' },
                { icon: '📋', label: 'Просмотр расписания группы', path: '/admin/schedule/group' },
              ].map((item) => (
                <Button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  style={{ 
                    width: '95%',
                    justifyContent: 'flex-start', 
                    padding: '12px 16px',
                    borderRadius: '10px',
                    border: 'none',
                    background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                    fontSize: '14px',
                    minHeight: '44px',
                    fontWeight: '500',
                    color: '#333',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
                  }}
                  onMouseEnter={(e: any) => {
                    e.currentTarget.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    e.currentTarget.style.color = '#fff'
                    e.currentTarget.style.transform = 'translateY(-2px)'
                    e.currentTarget.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.3)'
                  }}
                  onMouseLeave={(e: any) => {
                    e.currentTarget.style.background = 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
                    e.currentTarget.style.color = '#333'
                    e.currentTarget.style.transform = 'translateY(0)'
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.05)'
                  }}
                >
                  {item.icon} {item.label}
                </Button>
              ))}
            </Flex>
          </Panel>
        </Flex>
      </Container>
    </div>
  )
}

