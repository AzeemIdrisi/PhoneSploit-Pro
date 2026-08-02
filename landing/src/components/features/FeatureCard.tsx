'use client'

import { motion } from 'framer-motion'
import { Feature } from '@/data/features'
import { Card } from '@/components/ui/Card'
import { icons } from '@/data/features'

interface FeatureCardProps {
  feature: Feature
  index: number
}

export function FeatureCard({ feature, index }: FeatureCardProps) {
  const Icon = icons[feature.icon] || icons.Smartphone

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
      whileHover={{ y: -4, scale: 1.01 }}
    >
      <Card hover padding="lg" className="h-full group">
        <div className="flex items-start gap-4">
          <div className="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary-900/50 border border-primary-700 group-hover:border-primary-500 group-hover:bg-primary-900 transition-colors">
            <Icon className="h-6 w-6 text-primary-400 group-hover:text-primary-300 transition-colors" aria-hidden="true" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-white group-hover:text-primary-200 transition-colors">
              {feature.name}
            </h3>
            <p className="mt-1.5 text-sm text-primary-400 line-clamp-3">
              {feature.description}
            </p>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}