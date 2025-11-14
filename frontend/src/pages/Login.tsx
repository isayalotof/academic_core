import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Container, Flex } from '@maxhub/max-ui'
import { Button } from '../components/ui/Button'
import { Typography } from '../components/ui/Typography'
import { useAuthStore } from '../store/authStore'
import { useApi } from '../hooks/useApi'
import { AuthService } from '../services/authService'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const navigate = useNavigate()
  const { setUser, setTokens } = useAuthStore()
  const api = useApi()
  const authService = new AuthService(api)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await authService.login({ username, password })
      
      if (response.success) {
        setUser(response.user)
        setTokens(
          response.tokens.access_token,
          response.tokens.refresh_token,
          response.tokens.expires_in
        )
        navigate('/')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка входа')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Container
      style={{
        padding: '16px',
        width: '100%',
        maxWidth: '100%',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        boxSizing: 'border-box',
      }}
    >
      <div
        style={{
          background: '#ffffff',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.25)',
          width: '100%',
          maxWidth: '400px',
          boxSizing: 'border-box',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div
            style={{
              width: '60px',
              height: '60px',
              margin: '0 auto 16px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '28px',
              color: '#fff',
              fontWeight: 'bold',
            }}
          >
            🎓
          </div>
          <Typography variant="h1" style={{ marginBottom: '6px', color: '#333', fontSize: '20px' }}>
            Добро пожаловать
          </Typography>
          <Typography variant="body2" style={{ color: '#666', fontSize: '13px' }}>
            Войдите в систему расписания университета
          </Typography>
        </div>

        <form onSubmit={handleLogin}>
          <Flex direction="column" gap="14px">
            <div>
              <label
                style={{
                  display: 'block',
                  marginBottom: '6px',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#333',
                }}
              >
                Имя пользователя
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Введите имя пользователя"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  fontSize: '14px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '10px',
                  transition: 'all 0.3s ease',
                  outline: 'none',
                  minHeight: '44px',
                  boxSizing: 'border-box',
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

            <div>
              <label
                style={{
                  display: 'block',
                  marginBottom: '6px',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#333',
                }}
              >
                Пароль
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Введите пароль"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  fontSize: '14px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '10px',
                  transition: 'all 0.3s ease',
                  outline: 'none',
                  minHeight: '44px',
                  boxSizing: 'border-box',
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

            {error && (
              <div
                style={{
                  padding: '10px 12px',
                  background: '#ffebee',
                  borderRadius: '8px',
                  border: '1px solid #f44336',
                  animation: 'shake 0.5s',
                }}
              >
                <Typography variant="body2" style={{ color: '#c62828', fontSize: '12px' }}>
                  {error}
                </Typography>
              </div>
            )}

            <Button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                marginTop: '4px',
                padding: '12px 16px',
                fontSize: '14px',
                fontWeight: '600',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                color: '#fff',
                borderRadius: '10px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                minHeight: '44px',
              }}
              onMouseEnter={(e: any) => {
                if (!isLoading) {
                  e.currentTarget.style.transform = 'translateY(-2px)'
                  e.currentTarget.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)'
                }
              }}
              onMouseLeave={(e: any) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)'
              }}
            >
              {isLoading ? 'Вход...' : 'Войти'}
            </Button>

            <div style={{ textAlign: 'center', marginTop: '6px' }}>
              <Typography variant="body2" style={{ color: '#666', fontSize: '12px' }}>
                Нет аккаунта?{' '}
                <Link
                  to="/register"
                  style={{
                    color: '#667eea',
                    textDecoration: 'none',
                    fontWeight: '600',
                    transition: 'color 0.2s',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.color = '#764ba2'}
                  onMouseLeave={(e) => e.currentTarget.style.color = '#667eea'}
                >
                  Зарегистрироваться
                </Link>
              </Typography>
            </div>
          </Flex>
        </form>
      </div>

      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
          20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
      `}</style>
    </Container>
  )
}


