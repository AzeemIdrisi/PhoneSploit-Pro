'use client'

import { useState } from 'react'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import { screenshots, Screenshot } from '@/data/screenshots'
import { ScreenshotLightbox } from './ScreenshotLightbox'
import { Section } from '@/components/ui/Section'
import { Badge } from '@/components/ui/Badge'
import { Maximize } from 'lucide-react'

export default function Screenshots() {
  const [openImage, setOpenImage] = useState<Screenshot | null>(null)
  const screenshot = screenshots[0]

  if (!screenshot) {
    return null
  }

  return (
    <Section id="screenshot" className="relative">
      <div className="max-w-4xl mx-auto text-center mb-16">
        <Badge variant="info" className="mb-4 inline-block">Interface</Badge>
        <h2 className="section-title">PhoneSploit Pro Menu</h2>
        <p className="section-subtitle mx-auto">
          The single-page menu brings every capability into one numbered list — pick an option and run.
        </p>
      </div>

      <div className="max-w-5xl mx-auto">
        <motion.article
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-50px' }}
          transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
          className="group relative rounded-2xl overflow-hidden bg-surface-800/50 border border-surface-700 cursor-zoom-in"
        >
          <div className="relative w-full">
            <Image
              src={screenshot.src}
              alt={screenshot.alt}
              width={1920}
              height={1080}
              sizes="(max-width: 1024px) 100vw, 80rem"
              className="w-full h-auto object-contain"
              placeholder="blur"
              blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            />
            <div className="absolute inset-0 bg-linear-to-t from-surface-900/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
            <button
              type="button"
              onClick={() => setOpenImage(screenshot)}
              className="absolute inset-0 flex items-center justify-center"
              aria-label="View full size screenshot"
            >
              <span className="flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-white bg-surface-900/80 backdrop-blur-sm border border-surface-700 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 translate-y-2 group-hover:translate-y-0 transition-all duration-300">
                <Maximize className="h-4 w-4" aria-hidden="true" />
                View full size
              </span>
            </button>
          </div>
        </motion.article>
      </div>

      <AnimatePresence>
        {openImage && (
          <ScreenshotLightbox
            screenshot={openImage}
            onClose={() => setOpenImage(null)}
          />
        )}
      </AnimatePresence>
    </Section>
  )
}
