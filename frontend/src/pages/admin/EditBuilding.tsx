import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { ClassroomService, CreateBuildingRequest } from '../../services/classroomService'

export default function EditBuilding() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const api = useApi()
  const classroomService = new ClassroomService(api)

  const [formData, setFormData] = useState<CreateBuildingRequest>({
    name: '',
    address: '',
    description: '',
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (id) {
      loadBuilding()
    }
  }, [id])

  const loadBuilding = async () => {
    if (!id) return
    setIsLoading(true)
    try {
      const building = await classroomService.getBuilding(Number(id))
      setFormData({
        name: building.name,
        address: building.address || '',
        description: building.description || '',
      })
    } catch (error) {
      setError('Не удалось загрузить данные здания')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return

    setError('')
    setIsSaving(true)
    try {
      await classroomService.updateBuilding(Number(id), formData)
      alert('Здание успешно обновлено!')
      navigate('/admin/buildings')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при обновлении здания')
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
              <BackButton to="/admin/buildings" />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                Редактировать здание
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
                  Адрес
                </label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => handleChange('address', e.target.value)}
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
                  Описание
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  rows={4}
                  style={{
                    width: '100%',
                    padding: '12px',
                    fontSize: '16px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '12px',
                    background: '#fff',
                    transition: 'all 0.2s',
                    resize: 'vertical',
                  }}
                />
              </div>

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
                  onClick={() => navigate('/admin/buildings')}
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

