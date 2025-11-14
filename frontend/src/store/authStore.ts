import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: 'student' | 'teacher' | 'staff' | 'admin'
  roles: string[]
  student_group_id?: number
  teacher_id?: number
}

// Dev-режим: локальное переопределение роли для тестирования
const DEV_ROLE_KEY = 'dev-role-override'

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  tokenExpiresAt: number | null
  isLoading: boolean
  devRole: 'student' | 'teacher' | 'staff' | 'admin' | null
  setUser: (user: User) => void
  setToken: (token: string) => void
  setRefreshToken: (refreshToken: string) => void
  setTokens: (accessToken: string, refreshToken: string, expiresIn: number) => void
  setDevRole: (role: 'student' | 'teacher' | 'staff' | 'admin' | null) => void
  clearDevRole: () => void
  logout: () => void
  checkAuth: () => Promise<void>
  refreshAccessToken: () => Promise<boolean>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      tokenExpiresAt: null,
      isLoading: true,
      devRole: null,

      setUser: (user) => {
        const devRole = get().devRole
        // Если установлена dev-роль, применяем её к пользователю
        if (devRole) {
          user = {
            ...user,
            role: devRole,
            roles: [devRole]
          }
        }
        set({ user })
      },
      
      setToken: (token) => set({ token }),

      setRefreshToken: (refreshToken) => set({ refreshToken }),

      setTokens: (accessToken, refreshToken, expiresIn) => {
        const expiresAt = Date.now() + (expiresIn * 1000)
        set({ 
          token: accessToken, 
          refreshToken,
          tokenExpiresAt: expiresAt
        })
      },

      setDevRole: (role) => {
        set({ devRole: role })
        // Применяем dev-роль к текущему пользователю, если он есть
        const user = get().user
        if (user && role) {
          set({
            user: {
              ...user,
              role: role,
              roles: [role]
            }
          })
        } else if (user && !role) {
          // Если dev-роль сброшена, нужно обновить пользователя с сервера
          // Но это будет сделано через checkAuth или явное обновление
        }
        // Сохраняем в localStorage для восстановления после перезагрузки
        if (role) {
          localStorage.setItem(DEV_ROLE_KEY, role)
        } else {
          localStorage.removeItem(DEV_ROLE_KEY)
        }
      },

      clearDevRole: () => {
        set({ devRole: null })
        localStorage.removeItem(DEV_ROLE_KEY)
      },

      logout: () => {
        set({ user: null, token: null, refreshToken: null, tokenExpiresAt: null, devRole: null })
        localStorage.removeItem('auth-storage')
        localStorage.removeItem(DEV_ROLE_KEY)
      },

      checkAuth: async () => {
        const { token, refreshToken, tokenExpiresAt } = get()
        
        // Восстанавливаем dev-роль из localStorage при загрузке
        const savedDevRole = localStorage.getItem(DEV_ROLE_KEY) as 'student' | 'teacher' | 'staff' | 'admin' | null
        if (savedDevRole) {
          set({ devRole: savedDevRole })
        }
        
        if (!token) {
          set({ isLoading: false })
          return
        }

        // Проверяем, не истек ли токен
        if (tokenExpiresAt && Date.now() >= tokenExpiresAt - 60000) { // Обновляем за минуту до истечения
          if (refreshToken) {
            const refreshed = await get().refreshAccessToken()
            if (!refreshed) {
              set({ user: null, token: null, refreshToken: null, tokenExpiresAt: null, isLoading: false })
              return
            }
          }
        }

        try {
          // Проверяем токен через API
          const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${get().token}`,
            },
          })

          if (response.ok) {
            const data = await response.json()
            let user = data.user
            
            // Если установлена dev-роль, применяем её
            const devRole = get().devRole || savedDevRole
            if (devRole) {
              user = {
                ...user,
                role: devRole,
                roles: [devRole]
              }
            }
            
            set({ user, isLoading: false })
          } else if (response.status === 401 && refreshToken) {
            // Токен истек, пытаемся обновить
            const refreshed = await get().refreshAccessToken()
            if (refreshed) {
              // Повторяем запрос с новым токеном
              const retryResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`, {
                headers: {
                  'Authorization': `Bearer ${get().token}`,
                },
              })
              if (retryResponse.ok) {
                const retryData = await retryResponse.json()
                let user = retryData.user
                
                // Если установлена dev-роль, применяем её
                const devRole = get().devRole || savedDevRole
                if (devRole) {
                  user = {
                    ...user,
                    role: devRole,
                    roles: [devRole]
                  }
                }
                
                set({ user, isLoading: false })
              } else {
                set({ user: null, token: null, refreshToken: null, tokenExpiresAt: null, isLoading: false })
              }
            } else {
              set({ user: null, token: null, refreshToken: null, tokenExpiresAt: null, isLoading: false })
            }
          } else {
            set({ user: null, token: null, refreshToken: null, tokenExpiresAt: null, isLoading: false })
          }
        } catch (error) {
          console.error('Auth check failed:', error)
          set({ user: null, token: null, refreshToken: null, tokenExpiresAt: null, isLoading: false })
        }
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get()
        
        if (!refreshToken) {
          return false
        }

        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/refresh`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh_token: refreshToken }),
          })

          if (response.ok) {
            const data = await response.json()
            if (data.success && data.tokens) {
              get().setTokens(
                data.tokens.access_token,
                data.tokens.refresh_token,
                data.tokens.expires_in
              )
              return true
            }
          }
          return false
        } catch (error) {
          console.error('Token refresh failed:', error)
          return false
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
)

