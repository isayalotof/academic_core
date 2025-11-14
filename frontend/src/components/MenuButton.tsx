import { Button } from './ui/Button'

interface MenuButtonProps {
  onClick?: () => void
}

export default function MenuButton({ onClick }: MenuButtonProps) {
  return (
    <Button
      onClick={onClick || (() => {})}
      style={{
        padding: '8px 12px',
        fontSize: '12px',
        background: 'rgba(255, 255, 255, 0.2)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        color: '#fff',
        borderRadius: '10px',
        minHeight: '36px',
      }}
      variant="outline"
    >
      Меню
    </Button>
  )
}

