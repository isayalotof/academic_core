import { Container, Flex, Panel } from '@maxhub/max-ui'
import { Typography } from '../components/ui/Typography'
import BackButton from '../components/BackButton'
import MenuButton from '../components/MenuButton'

interface UnderDevelopmentProps {
  title: string
}

export default function UnderDevelopment({ title }: UnderDevelopmentProps) {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '16px',
    }}>
      <Container style={{ width: '100%', maxWidth: '800px' }}>
        <Flex direction="column" gap="16px">
          {/* Header */}
          <Flex justify="space-between" align="center" wrap="wrap" gap="8px">
            <Flex align="center" gap="12px">
              <BackButton />
              <Typography variant="h1" style={{ fontSize: '20px', fontWeight: '600', color: '#fff' }}>
                {title}
              </Typography>
            </Flex>
            {/* MenuButton removed - not needed on this page */}
          </Flex>

          {/* Content */}
          <Panel style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '16px',
            padding: '60px 40px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <Typography variant="h2" style={{ 
              fontSize: '32px', 
              fontWeight: '700', 
              color: '#667eea',
              marginBottom: '16px',
              letterSpacing: '2px'
            }}>
              В РАЗРАБОТКЕ
            </Typography>
            <Typography variant="body1" style={{ 
              fontSize: '16px', 
              color: '#666',
              lineHeight: '1.6'
            }}>
              Данный раздел находится в разработке.<br />
              Скоро здесь появится новая функциональность.
            </Typography>
          </Panel>
        </Flex>
      </Container>
    </div>
  )
}

