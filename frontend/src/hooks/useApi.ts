import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios'
import { useAuthStore } from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Флаг для предотвращения множественных одновременных запросов на обновление токена
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: any) => void
  reject: (error?: any) => void
}> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

export const useApi = (): AxiosInstance => {
  const { token, refreshToken, tokenExpiresAt, setTokens, logout } = useAuthStore()

  const api = axios.create({
    baseURL: API_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Добавляем токен к каждому запросу
  api.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      const currentToken = useAuthStore.getState().token
      const currentRefreshToken = useAuthStore.getState().refreshToken
      const currentExpiresAt = useAuthStore.getState().tokenExpiresAt

      // Проверяем, не истек ли токен (обновляем за минуту до истечения)
      if (
        currentToken &&
        currentRefreshToken &&
        currentExpiresAt &&
        Date.now() >= currentExpiresAt - 60000
      ) {
        // Токен скоро истечет, обновляем его
        if (!isRefreshing) {
          isRefreshing = true
          try {
            const response = await axios.post(
              `${API_URL}/api/auth/refresh`,
              { refresh_token: currentRefreshToken }
            )
            if (response.data.success && response.data.tokens) {
              useAuthStore.getState().setTokens(
                response.data.tokens.access_token,
                response.data.tokens.refresh_token,
                response.data.tokens.expires_in
              )
              config.headers.Authorization = `Bearer ${response.data.tokens.access_token}`
              processQueue(null, response.data.tokens.access_token)
            } else {
              processQueue(new Error('Token refresh failed'))
              logout()
            }
          } catch (error) {
            processQueue(error)
            logout()
            return Promise.reject(error)
          } finally {
            isRefreshing = false
          }
        } else {
          // Ждем завершения обновления токена
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject })
          })
            .then((newToken) => {
              if (newToken) {
                config.headers.Authorization = `Bearer ${newToken}`
              }
              return config
            })
            .catch((error) => {
              return Promise.reject(error)
            })
        }
      } else if (currentToken) {
        config.headers.Authorization = `Bearer ${currentToken}`
      }

      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Обработка ошибок
  api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

      // Если получили 401 и это не запрос на обновление токена
      if (error.response?.status === 401 && !originalRequest._retry) {
        const currentRefreshToken = useAuthStore.getState().refreshToken

        if (currentRefreshToken && !isRefreshing) {
          originalRequest._retry = true
          isRefreshing = true

          try {
            const response = await axios.post(
              `${API_URL}/api/auth/refresh`,
              { refresh_token: currentRefreshToken }
            )

            if (response.data.success && response.data.tokens) {
              useAuthStore.getState().setTokens(
                response.data.tokens.access_token,
                response.data.tokens.refresh_token,
                response.data.tokens.expires_in
              )

              // Обновляем заголовок для повторного запроса
              originalRequest.headers.Authorization = `Bearer ${response.data.tokens.access_token}`
              processQueue(null, response.data.tokens.access_token)

              // Повторяем оригинальный запрос с новым токеном
              return api(originalRequest)
            } else {
              processQueue(new Error('Token refresh failed'))
              logout()
              return Promise.reject(error)
            }
          } catch (refreshError) {
            processQueue(refreshError)
            logout()
            return Promise.reject(refreshError)
          } finally {
            isRefreshing = false
          }
        } else if (isRefreshing) {
          // Ждем завершения обновления токена
          return new Promise((resolve, reject) => {
            failedQueue.push({
              resolve: (newToken) => {
                if (newToken && originalRequest) {
                  originalRequest.headers.Authorization = `Bearer ${newToken}`
                  resolve(api(originalRequest))
                } else {
                  reject(error)
                }
              },
              reject: (err) => reject(err),
            })
          })
        } else {
          // Нет refresh token, разлогиниваем
          logout()
          return Promise.reject(error)
        }
      }

      return Promise.reject(error)
    }
  )

  return api
}

