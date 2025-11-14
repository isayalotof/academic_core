import { Button as MaxButton } from '@maxhub/max-ui'
import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline' | 'ghost'
  children: React.ReactNode
  style?: React.CSSProperties
}

export const Button: React.FC<ButtonProps> = ({ variant, style, children, ...props }) => {
  // MAX UI Button может не иметь variant, используем style для стилизации
  const buttonStyle: React.CSSProperties = {
    ...style,
  }
  
  if (variant === 'outline') {
    buttonStyle.background = 'transparent'
    buttonStyle.border = '1px solid currentColor'
  } else if (variant === 'ghost') {
    buttonStyle.background = 'transparent'
    buttonStyle.border = 'none'
    buttonStyle.color = 'inherit'
  }
  
  // Используем MaxButton напрямую, передавая все пропсы
  return (
    <MaxButton style={buttonStyle} {...(props as any)}>
      {children}
    </MaxButton>
  )
}

