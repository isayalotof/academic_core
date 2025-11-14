import { Typography as MaxTypography } from '@maxhub/max-ui'
import React from 'react'

interface TypographyProps {
  variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'body1' | 'body2'
  children: React.ReactNode
  style?: React.CSSProperties
  [key: string]: any
}

export const Typography: React.FC<TypographyProps> = ({ variant = 'body1', children, style, ...props }) => {
  // MAX UI Typography - это объект с подкомпонентами
  const TypographyObj = MaxTypography as any
  
  // Определяем компонент на основе варианта
  let Component: any
  
  if (variant === 'h1' || variant === 'h2') {
    Component = TypographyObj.Display || TypographyObj.Title || TypographyObj.Body || 'div'
  } else if (variant === 'h3' || variant === 'h4') {
    Component = TypographyObj.Title || TypographyObj.Body || 'div'
  } else {
    Component = TypographyObj.Body || TypographyObj.Caption || 'div'
  }
  
  // Если Component - функция React компонента, используем её
  if (typeof Component === 'function') {
    const Comp = Component as React.ComponentType<any>
    return <Comp style={style} {...props}>{children}</Comp>
  }
  
  // Fallback на обычный div с соответствующими стилями
  const variantStyles: Record<string, React.CSSProperties> = {
    h1: { fontSize: '32px', fontWeight: 'bold', marginBottom: '16px' },
    h2: { fontSize: '24px', fontWeight: 'bold', marginBottom: '12px' },
    h3: { fontSize: '20px', fontWeight: '600', marginBottom: '8px' },
    h4: { fontSize: '18px', fontWeight: '600', marginBottom: '8px' },
    body1: { fontSize: '16px', lineHeight: '1.5' },
    body2: { fontSize: '14px', lineHeight: '1.5' },
  }
  
  return (
    <div style={{ ...variantStyles[variant], ...style }} {...props}>
      {children}
    </div>
  )
}

