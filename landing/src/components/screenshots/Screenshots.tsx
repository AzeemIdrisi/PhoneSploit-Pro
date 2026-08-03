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

  return (
    <Section id="screenshots" className="relative">
      <div className="max-w-4xl mx-auto text-center mb-16">
        <Badge variant="info" className="mb-4 inline-block">In Action</Badge>
        <h2 className="section-title">See PhoneSploit Pro in Action</h2>
        <p className="section-subtitle mx-auto">
          A look at PhoneSploit Pro in action.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6" role="list" aria-label="PhoneSploit Pro screenshots">
        {screenshots.map((screenshot, index) => (
          <motion.article
            key={screenshot.id}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ delay: index * 0.1, duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="group relative rounded-2xl overflow-hidden bg-surface-800/50 border border-surface-700 cursor-zoom-in"
            role="listitem"
          >
            <div className="relative aspect-[3/2] overflow-hidden">
              <Image
                src={screenshot.src}
                alt={screenshot.alt}
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-all duration-500 group-hover:scale-105"
                placeholder="blur"
                blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
              />
              <div className="absolute inset-0 bg-linear-to-t from-surface-900/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <button
              onClick={() => setOpenImage(screenshot)}
              className="absolute inset-0 flex items-center justify-center"
              aria-label={`View full size`}
            >
              <span className="flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-white bg-surface-900/80 backdrop-blur-sm border border-surface-700 opacity-0 group-hover:opacity-100 translate-x-4 group-hover:translate-x-0 transition-all duration-300">
                <Maximize className="h-4 w-4" />
                View full size
              </span>
            </button>
            </div>
          </motion.article>
        ))}
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