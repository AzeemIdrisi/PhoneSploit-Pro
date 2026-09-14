import { cn } from '@/lib/utils'
import { Container } from './Container'

export function Section({ 
  className, 
  id, 
  children, 
  ...props 
}: React.ComponentProps<'section'> & { id?: string }) {
  return (
    <section 
      id={id} 
      className={cn('section scroll-mt-28', className)} 
      {...props}
    >
      <Container>{children}</Container>
    </section>
  )
}