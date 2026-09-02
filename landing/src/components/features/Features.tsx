'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import { featureCategories, features, FeatureCategory } from '@/data/features'
import { FeatureCard } from './FeatureCard'
import { Section } from '@/components/ui/Section'
import { Badge } from '@/components/ui/Badge'
import { ExternalLink } from 'lucide-react'

export default function Features() {
  const [activeCategory, setActiveCategory] = useState<FeatureCategory>('device')
  const filteredFeatures = features.filter(f => f.category === activeCategory)

  return (
    <Section id="features" className="relative">
      <div className="max-w-4xl mx-auto text-center mb-16">
        <Badge variant="info" className="mb-4 inline-block">75+ Features</Badge>
        <h2 className="section-title">Powerful Features for Android Security Testing</h2>
        <p className="section-subtitle mx-auto">
          Comprehensive toolkit covering device control, data extraction, media streaming, app management, network analysis, and automated exploitation.
        </p>
      </div>

      <div className="flex flex-wrap justify-center gap-2 mb-12" role="tablist" aria-label="Feature categories">
        {featureCategories.map((category) => (
          <button
            key={category.id}
            role="tab"
            aria-selected={activeCategory === category.id}
            aria-controls={`panel-${category.id}`}
            id={`tab-${category.id}`}
            onClick={() => setActiveCategory(category.id as FeatureCategory)}
            className={cn(
              'relative px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 whitespace-nowrap',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-900',
              activeCategory === category.id
                ? 'bg-primary-900/50 text-white border border-primary-700 shadow-lg shadow-primary-900/20'
                : 'text-primary-300 hover:text-white hover:bg-surface-700/50 border border-surface-700'
            )}
          >
            {category.label}
            <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-surface-700 text-primary-400">
              {category.count}
            </span>
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeCategory}
          id={`panel-${activeCategory}`}
          role="tabpanel"
          aria-labelledby={`tab-${activeCategory}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-5 sm:gap-6"
        >
          {filteredFeatures.map((feature, index) => (
            <FeatureCard key={feature.id} feature={feature} index={index} />
          ))}
        </motion.div>
      </AnimatePresence>

      <div className="mt-12 text-center">
        <p className="text-primary-400 mb-4">
          And many more features... <span className="text-primary-500">75+ total</span>
        </p>
        <a
          href="https://github.com/AzeemIdrisi/PhoneSploit-Pro#features"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-primary-400 hover:text-primary-300 font-medium transition-colors"
        >
          View all features on GitHub
          <ExternalLink className="h-4 w-4" aria-hidden="true" />
        </a>
      </div>
    </Section>
  )
}