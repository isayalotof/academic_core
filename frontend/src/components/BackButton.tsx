import { useNavigate } from 'react-router-dom'
import { Button } from './ui/Button'

interface BackButtonProps {
  to?: string
  onClick?: () => void
  style?: React.CSSProperties
}

interface MenuButtonProps {
  onClick?: () => void
}

export default function BackButton({ to, onClick, style }: BackButtonProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    if (onClick) {
      onClick()
    } else if (to) {
      navigate(to)
    } else {
      navigate(-1)
    }
  }

  return (
    <Button
      onClick={handleClick}
      style={{
        padding: '6px 10px',
        fontSize: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        background: 'rgba(255, 255, 255, 0.2)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        color: '#fff',
        borderRadius: '10px',
        fontWeight: '500',
        minHeight: '36px',
        ...style,
      }}
    >
      ← Назад
    </Button>
  )
}

