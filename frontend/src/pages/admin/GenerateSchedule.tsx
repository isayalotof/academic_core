import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Button } from '../../components/ui/Button'
import { Typography } from '../../components/ui/Typography'
import BackButton from '../../components/BackButton'
import { useApi } from '../../hooks/useApi'
import { ScheduleGenerationService, GenerateScheduleRequest } from '../../services/scheduleGenerationService'

export default function GenerateSchedule() {
  const navigate = useNavigate()
  const api = useApi()
  const generationService = new ScheduleGenerationService(api)

  const [formData, setFormData] = useState<GenerateScheduleRequest>({
    semester: 1,
    max_iterations: 100,
    skip_stage1: false,
    skip_stage2: false,
  })
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [jobId, setJobId] = useState<string | null>(null)

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsGenerating(true)

    try {
      const result = await generationService.generateSchedule(formData)
      setSuccess(result.message || 'Генерация расписания запущена')
      setJobId(result.job_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при запуске генерации расписания')
    } finally {
      setIsGenerating(false)
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
                Генерация расписания
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
                    Семестр *
                  </label>
                  <select
                    value={formData.semester}
                    onChange={(e) => handleChange('semester', parseInt(e.target.value))}
                    required
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      transition: 'all 0.2s',
                    }}
                  >
                    {Array.from({ length: 12 }, (_, i) => i + 1).map((sem) => (
                      <option key={sem} value={sem}>
                        Семестр {sem}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    Максимум итераций
                  </label>
                  <input
                    type="number"
                    value={formData.max_iterations}
                    onChange={(e) => handleChange('max_iterations', parseInt(e.target.value) || 100)}
                    min="1"
                    max="500"
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '16px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '12px',
                      background: '#fff',
                      transition: 'all 0.2s',
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#667eea'
                      e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)'
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#e0e0e0'
                      e.target.style.boxShadow = 'none'
                    }}
                  />
                </div>

                <Flex direction="column" gap="12px">
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={formData.skip_stage1}
                      onChange={(e) => handleChange('skip_stage1', e.target.checked)}
                      style={{
                        width: '20px',
                        height: '20px',
                        cursor: 'pointer',
                      }}
                    />
                    <Typography style={{ color: '#333', fontSize: '14px' }}>
                      Пропустить Stage 1 (использовать существующее расписание)
                    </Typography>
                  </label>

                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={formData.skip_stage2}
                      onChange={(e) => handleChange('skip_stage2', e.target.checked)}
                      style={{
                        width: '20px',
                        height: '20px',
                        cursor: 'pointer',
                      }}
                    />
                    <Typography style={{ color: '#333', fontSize: '14px' }}>
                      Пропустить Stage 2 (без распределения аудиторий)
                    </Typography>
                  </label>
                </Flex>

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

                {success && (
                  <div style={{ 
                    padding: '16px', 
                    background: 'rgba(76, 175, 80, 0.1)', 
                    borderRadius: '12px',
                    border: '1px solid rgba(76, 175, 80, 0.3)',
                  }}>
                    <Typography variant="body2" style={{ color: '#2e7d32', marginBottom: '8px' }}>
                      {success}
                    </Typography>
                    {jobId && (
                      <Typography variant="body2" style={{ color: '#666', fontSize: '12px' }}>
                        ID задачи: {jobId}
                      </Typography>
                    )}
                  </div>
                )}

                <Flex gap="12px" style={{ marginTop: '8px' }}>
                  <Button 
                    type="submit" 
                    disabled={isGenerating} 
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
                    {isGenerating ? 'Запуск...' : 'Запустить генерацию'}
                  </Button>
                  <Button
                    type="button"
                    onClick={() => navigate('/')}
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

