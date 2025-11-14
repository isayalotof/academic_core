import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { ClassroomService, Classroom } from '../../services/classroomService'

export default function ClassroomsList() {
  const navigate = useNavigate()
  const api = useApi()
  const classroomService = new ClassroomService(api)

  const [classrooms, setClassrooms] = useState<Classroom[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const pageSize = 20

  useEffect(() => {
    loadClassrooms()
  }, [page])

  const loadClassrooms = async () => {
    setIsLoading(true)
    try {
      const data = await classroomService.getClassrooms({
        page,
        page_size: pageSize,
      })
      setClassrooms(data.classrooms)
      setTotalCount(data.total_count)
    } catch (error) {
      console.error('Failed to load classrooms:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (classroomId: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту аудиторию?')) {
      return
    }

    try {
      await classroomService.deleteClassroom(classroomId)
      loadClassrooms()
    } catch (error) {
      alert('Ошибка при удалении аудитории')
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
                Аудитории
              </Typography>
            </Flex>
            <Button 
              onClick={() => navigate('/admin/classrooms/create')}
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
          ) : classrooms.length === 0 ? (
            <Panel style={{ 
              padding: '32px', 
              textAlign: 'center',
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '20px',
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            }}>
              <Typography style={{ color: '#666', fontSize: '16px' }}>Аудитории не найдены</Typography>
            </Panel>
          ) : (
            <>
              <Flex direction="column" gap="12px">
                {classrooms.map((classroom) => (
                  <Panel
                    key={classroom.id}
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
                          {classroom.name} ({classroom.code})
                        </Typography>
                        <Typography variant="body2" style={{ color: '#666' }}>
                          {classroom.building_name} • {classroom.floor} этаж • Вместимость: {classroom.capacity}
                        </Typography>
                        <Typography variant="body2" style={{ color: '#999', fontSize: '14px' }}>
                          Тип: {classroom.classroom_type}
                          {classroom.has_projector && ' • Проектор'}
                          {classroom.has_computers && ' • Компьютеры'}
                        </Typography>
                      </Flex>
                      <Flex gap="8px" wrap="wrap">
                        <Button
                          onClick={() => navigate(`/admin/classrooms/${classroom.id}/edit`)}
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
                          onClick={() => handleDelete(classroom.id)}
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

              {totalCount > pageSize && (
                <Panel style={{ 
                  padding: '16px',
                  background: 'rgba(255, 255, 255, 0.95)',
                  borderRadius: '20px',
                  boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
                }}>
                  <Flex justify="center" align="center" gap="12px" wrap="wrap">
                    <Button
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                      style={{
                        padding: '10px 16px',
                        background: page === 1 ? '#e0e0e0' : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                        border: 'none',
                        color: page === 1 ? '#999' : '#333',
                        borderRadius: '12px',
                        fontWeight: '500',
                        cursor: page === 1 ? 'not-allowed' : 'pointer',
                      }}
                    >
                      ←
                    </Button>
                    <Typography style={{ padding: '8px 16px', color: '#333', fontWeight: '500' }}>
                      Страница {page} из {Math.ceil(totalCount / pageSize)}
                    </Typography>
                    <Button
                      onClick={() => setPage((p) => p + 1)}
                      disabled={page >= Math.ceil(totalCount / pageSize)}
                      style={{
                        padding: '10px 16px',
                        background: page >= Math.ceil(totalCount / pageSize) ? '#e0e0e0' : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                        border: 'none',
                        color: page >= Math.ceil(totalCount / pageSize) ? '#999' : '#333',
                        borderRadius: '12px',
                        fontWeight: '500',
                        cursor: page >= Math.ceil(totalCount / pageSize) ? 'not-allowed' : 'pointer',
                      }}
                    >
                      →
                    </Button>
                  </Flex>
                </Panel>
              )}
            </>
          )}
        </Flex>
      </Container>
    </div>
  )
}

