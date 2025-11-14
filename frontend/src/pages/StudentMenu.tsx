import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import BackButton from '../components/BackButton'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function StudentMenu() {
  const navigate = useNavigate()
  const { logout } = useAuthStore()

  const menuItems = [
    {
      title: 'Создать обращение',
      description: 'Создание нового обращения',
      onClick: () => navigate('/tickets/create'),
    },
    {
      title: 'Пропуски университета',
      description: 'Подача заявлений на пропуски',
      onClick: () => navigate('/passes'),
    },
    {
      title: 'Единое окно',
      description: 'Подача заявлений в различные подразделения',
      onClick: () => navigate('/single-window'),
    },
    {
      title: 'Парковка',
      description: 'Управление парковочными местами',
      onClick: () => navigate('/parking'),
    },
    {
      title: 'Другие услуги',
      description: 'Дополнительные университетские услуги',
      onClick: () => navigate('/other-services'),
    },
  ]

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '100%' }}>
        <Flex direction="column" gap="16px">
          <Flex justify="space-between" align="center" wrap="wrap" gap="8px">
            <Flex align="center" gap="16px" style={{ flex: 1, minWidth: '200px' }}>
              <BackButton to="/" />
              <Typography variant="h1" style={{ fontSize: '18px', fontWeight: '600', color: '#fff', marginLeft: '4px', marginTop: '12px' }}>
                Меню
              </Typography>
            </Flex>
          </Flex>

          <Flex direction="column" gap="12px" style={{ width: '100%' }}>
            {menuItems.map((item, index) => (
              <Panel
                key={index}
                onClick={item.onClick}
                style={{
                  width: '100%',
                  padding: '16px',
                  cursor: 'pointer',
                  border: 'none',
                  borderRadius: '16px',
                  background: 'rgba(255, 255, 255, 0.95)',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
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
                <Typography variant="h4" style={{ marginBottom: '6px', fontSize: '15px', fontWeight: '600', color: '#333' }}>
                  {item.title}
                </Typography>
                <Typography variant="body2" style={{ color: '#666', fontSize: '12px' }}>
                  {item.description}
                </Typography>
              </Panel>
            ))}
          </Flex>

          <Button
            onClick={logout}
            style={{ 
              width: '100%',
              marginTop: '8px',
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
            Выйти
          </Button>
        </Flex>
      </Container>
    </div>
  )
}

