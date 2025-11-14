import React from 'react'
import ReactDOM from 'react-dom/client'
import { MaxUI } from '@maxhub/max-ui'
import '@maxhub/max-ui/dist/styles.css'
import App from './App'
import './index.css'

// Инициализация MAX WebApp
declare global {
  interface Window {
    WebApp?: {
      initData: string
      initDataUnsafe: {
        user?: {
          id: number
          first_name: string
          last_name?: string
          username?: string
          language_code?: string
        }
        query_id?: string
        auth_date?: number
        hash?: string
      }
      platform: 'ios' | 'android' | 'desktop' | 'web'
      ready: () => void
      close: () => void
      BackButton: {
        show: () => void
        hide: () => void
        onClick: (callback: () => void) => void
        offClick: (callback: () => void) => void
        isVisible: boolean
      }
      HapticFeedback: {
        impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
        notificationOccurred: (type: 'error' | 'success' | 'warning') => void
      }
    }
  }
}

// Уведомляем MAX, что приложение готово
if (window.WebApp) {
  window.WebApp.ready()
}

const Root = () => (
  <MaxUI>
    <App />
  </MaxUI>
)

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
)

