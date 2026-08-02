import { cn } from '@/lib/utils'

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
}

export function Badge({ className, variant = 'default', children, ...props }: BadgeProps) {
  const variants = {
    default: 'bg-primary-900/50 text-primary-200 border-primary-700',
    success: 'bg-green-900/50 text-green-300 border-green-700',
    warning: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
    danger: 'bg-red-900/50 text-red-300 border-red-700',
    info: 'bg-blue-900/50 text-blue-300 border-blue-700',
  }

  return (
    <span
      className={cn('badge', variants[variant], className)}
      {...props}
    >
      {children}
    </span>
  )
}