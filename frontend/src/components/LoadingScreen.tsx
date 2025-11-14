import { Container } from '@maxhub/max-ui'
import { Typography } from './ui/Typography'

export default function LoadingScreen() {
  return (
    <Container
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        flexDirection: 'column',
        gap: '16px',
      }}
    >
      <Typography variant="h2">Загрузка...</Typography>
    </Container>
  )
}

