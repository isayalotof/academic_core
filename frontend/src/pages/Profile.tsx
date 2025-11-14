import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import BackButton from '../components/BackButton'
import { useAuthStore } from '../store/authStore'
import { useApi } from '../hooks/useApi'
import { AuthService } from '../services/authService'

export default function Profile() {
  const { user, setUser, logout, devRole, setDevRole, clearDevRole } = useAuthStore()
  const navigate = useNavigate()
  const api = useApi()
  const authService = new AuthService(api)
  
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefreshUser = async () => {
    setIsRefreshing(true)
    try {
      const updatedUser = await authService.getCurrentUser()
      clearDevRole() // Сбросить dev-роль при обновлении
      setUser(updatedUser)
    } catch (error) {
      console.error('Failed to refresh user:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleDevRoleChange = (newRole: 'student' | 'teacher' | 'staff' | 'admin') => {
    if (!user) return
    
    // Устанавливаем dev-роль в store (она автоматически применится к пользователю)
    setDevRole(newRole)
    
    // Перезагружаем страницу для применения новой роли в роутинге
    setTimeout(() => {
      window.location.href = '/'
    }, 200)
  }

  if (!user) {
    return null
  }

  const isAdmin = user.role === 'admin' || user.roles?.includes('admin')
  const currentRole = devRole || user.role

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
              Профиль
            </Typography>
          </Flex>

          {/* Информация о пользователе */}
          <Panel style={{ 
            padding: '20px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            width: '100%',
          }}>
            <Typography variant="h3" style={{ marginBottom: '16px', fontSize: '18px', fontWeight: '600', color: '#333' }}>
              Информация о пользователе
            </Typography>
            <Flex direction="column" gap="12px">
              <div style={{ padding: '12px', background: '#f5f7fa', borderRadius: '10px' }}>
                <Typography style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Имя пользователя</Typography>
                <Typography style={{ fontSize: '16px', fontWeight: '500', color: '#333' }}>{user.username}</Typography>
              </div>
              <div style={{ padding: '12px', background: '#f5f7fa', borderRadius: '10px' }}>
                <Typography style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>ФИО</Typography>
                <Typography style={{ fontSize: '16px', fontWeight: '500', color: '#333' }}>{user.full_name}</Typography>
              </div>
              <div style={{ padding: '12px', background: '#f5f7fa', borderRadius: '10px' }}>
                <Typography style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Email</Typography>
                <Typography style={{ fontSize: '16px', fontWeight: '500', color: '#333' }}>{user.email}</Typography>
              </div>
              <div style={{ padding: '12px', background: '#f5f7fa', borderRadius: '10px' }}>
                <Typography style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Роль</Typography>
                <Typography style={{ fontSize: '16px', fontWeight: '500', color: '#333' }}>
                  {currentRole === 'student' ? '👨‍🎓 Студент' :
                   currentRole === 'teacher' ? '👨‍🏫 Преподаватель' :
                   currentRole === 'staff' ? '👔 Сотрудник' :
                   currentRole === 'admin' ? '👑 Администратор' : currentRole}
                  {devRole && (
                    <span style={{ 
                      marginLeft: '8px', 
                      fontSize: '12px', 
                      color: '#ff6b6b',
                      fontWeight: 'normal'
                    }}>
                      (DEV MODE)
                    </span>
                  )}
                </Typography>
              </div>
              {user.teacher_id && (
                <div style={{ padding: '12px', background: '#f5f7fa', borderRadius: '10px' }}>
                  <Typography style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>ID преподавателя</Typography>
                  <Typography style={{ fontSize: '16px', fontWeight: '500', color: '#333' }}>{user.teacher_id}</Typography>
                </div>
              )}
              {user.student_group_id && (
                <div style={{ padding: '12px', background: '#f5f7fa', borderRadius: '10px' }}>
                  <Typography style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>ID группы</Typography>
                  <Typography style={{ fontSize: '16px', fontWeight: '500', color: '#333' }}>{user.student_group_id}</Typography>
                </div>
              )}
            </Flex>
          </Panel>

          {/* Dev панель (только для админов) */}
          {isAdmin && (
            <Panel style={{ 
              padding: '20px',
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '16px',
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
              width: '100%',
              border: '2px solid #ff6b6b',
            }}>
              <Flex direction="column" gap="12px">
                <Flex align="center" gap="8px">
                  <Typography variant="h3" style={{ fontSize: '18px', fontWeight: '600', color: '#ff6b6b' }}>
                    ⚠️ DEV PANEL
                  </Typography>
                  <span style={{ 
                    fontSize: '10px', 
                    padding: '2px 8px',
                    background: '#ff6b6b',
                    color: '#fff',
                    borderRadius: '4px',
                    fontWeight: '600'
                  }}>
                    ТОЛЬКО ДЛЯ РАЗРАБОТКИ
                  </span>
                </Flex>
                <Typography style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                  Изменить роль для тестирования интерфейса (только локально, не сохраняется на сервере)
                </Typography>
                
                <Flex direction="column" gap="8px">
                  {(['student', 'teacher', 'staff', 'admin'] as const).map((role) => (
                    <Button
                      key={role}
                      onClick={() => handleDevRoleChange(role)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        borderRadius: '10px',
                        border: currentRole === role ? '2px solid #667eea' : '1px solid #e0e0e0',
                        background: currentRole === role 
                          ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                          : '#f5f7fa',
                        color: currentRole === role ? '#fff' : '#333',
                        fontSize: '14px',
                        fontWeight: currentRole === role ? '600' : '500',
                        minHeight: '44px',
                        transition: 'all 0.3s ease',
                      }}
                    >
                      {role === 'student' ? '👨‍🎓' :
                       role === 'teacher' ? '👨‍🏫' :
                       role === 'staff' ? '👔' :
                       '👑'} {role === 'student' ? 'Студент' :
                              role === 'teacher' ? 'Преподаватель' :
                              role === 'staff' ? 'Сотрудник' :
                              'Администратор'}
                      {currentRole === role && ' ✓'}
                    </Button>
                  ))}
                </Flex>

                {devRole && (
                  <Button
                    onClick={handleRefreshUser}
                    disabled={isRefreshing}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      borderRadius: '10px',
                      background: '#fff',
                      border: '2px solid #667eea',
                      color: '#667eea',
                      fontSize: '14px',
                      fontWeight: '500',
                      minHeight: '44px',
                      marginTop: '8px',
                    }}
                  >
                    {isRefreshing ? 'Обновление...' : '🔄 Сбросить DEV режим (вернуть реальную роль)'}
                  </Button>
                )}
              </Flex>
            </Panel>
          )}

          {/* Действия */}
          <Panel style={{ 
            padding: '20px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            width: '100%',
          }}>
            <Typography variant="h3" style={{ marginBottom: '16px', fontSize: '18px', fontWeight: '600', color: '#333' }}>
              Действия
            </Typography>
            <Flex direction="column" gap="12px">
              <Button
                onClick={handleRefreshUser}
                disabled={isRefreshing}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                  border: 'none',
                  color: '#333',
                  fontSize: '14px',
                  fontWeight: '500',
                  minHeight: '44px',
                }}
              >
                {isRefreshing ? 'Обновление...' : '🔄 Обновить данные профиля'}
              </Button>
              <Button
                onClick={logout}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)',
                  border: 'none',
                  color: '#fff',
                  fontSize: '14px',
                  fontWeight: '500',
                  minHeight: '44px',
                }}
              >
                🚪 Выйти из аккаунта
              </Button>
            </Flex>
          </Panel>
        </Flex>
      </Container>
    </div>
  )
}

