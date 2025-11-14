import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { ClassroomService, Building } from '../../services/classroomService'

export default function BuildingsList() {
  const navigate = useNavigate()
  const api = useApi()
  const classroomService = new ClassroomService(api)

  const [buildings, setBuildings] = useState<Building[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadBuildings()
  }, [])

  const loadBuildings = async () => {
    setIsLoading(true)
    try {
      const data = await classroomService.getBuildings()
      setBuildings(data.buildings || [])
    } catch (error) {
      console.error('Failed to load buildings:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (buildingId: number) => {
    if (!confirm('Вы уверены, что хотите удалить это здание?')) {
      return
    }

    try {
      await classroomService.deleteBuilding(buildingId)
      loadBuildings()
    } catch (error) {
      alert('Ошибка при удалении здания')
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
              <BackButton to="/" />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Здания
              </Typography>
            </Flex>
            <Button 
              onClick={() => navigate('/admin/buildings/create')}
              style={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: 'none',
                color: '#667eea',
                padding: '8px 16px',
                borderRadius: '12px',
                fontWeight: '600',
                fontSize: '14px',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
              }}
            >
              + Создать
            </Button>
          </Flex>

          {isLoading ? (
            <Panel style={{ 
              padding: '32px', 
              textAlign: 'center',
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '20px',
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            }}>
              <Typography style={{ color: '#666' }}>Загрузка...</Typography>
            </Panel>
          ) : buildings.length === 0 ? (
            <Panel style={{ 
              padding: '32px', 
              textAlign: 'center',
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '20px',
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            }}>
              <Typography style={{ color: '#666', fontSize: '16px' }}>Здания не найдены</Typography>
            </Panel>
          ) : (
            <Flex direction="column" gap="12px">
              {buildings.map((building) => (
                <Panel
                  key={building.id}
                  style={{
                    padding: '20px',
                    border: 'none',
                    borderRadius: '20px',
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
                  <Flex justify="space-between" align="center" wrap="wrap" gap="12px">
                    <Flex direction="column" gap="4px" style={{ flex: 1, minWidth: '200px' }}>
                      <Typography variant="h4" style={{ fontWeight: '600', color: '#333' }}>
                        {building.name}
                      </Typography>
                      {building.address && (
                        <Typography variant="body2" style={{ color: '#666' }}>
                          {building.address}
                        </Typography>
                      )}
                      {building.description && (
                        <Typography variant="body2" style={{ color: '#999', fontSize: '14px' }}>
                          {building.description}
                        </Typography>
                      )}
                    </Flex>
                    <Flex gap="8px" wrap="wrap">
                      <Button
                        onClick={() => navigate(`/admin/buildings/${building.id}/edit`)}
                        style={{ 
                          fontSize: '14px', 
                          padding: '10px 16px',
                          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                          border: 'none',
                          color: '#333',
                          borderRadius: '12px',
                          fontWeight: '500',
                        }}
                      >
                        Изменить
                      </Button>
                      <Button
                        onClick={() => handleDelete(building.id)}
                        style={{
                          fontSize: '14px',
                          padding: '10px 16px',
                          background: 'rgba(244, 67, 54, 0.1)',
                          border: 'none',
                          color: '#f44336',
                          borderRadius: '12px',
                          fontWeight: '500',
                        }}
                      >
                        Удалить
                      </Button>
                    </Flex>
                  </Flex>
                </Panel>
              ))}
            </Flex>
          )}
        </Flex>
      </Container>
    </div>
  )
}

