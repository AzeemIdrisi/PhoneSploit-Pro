'use client'

import { useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import Image from 'next/image'
import { Screenshot } from '@/data/screenshots'
import { X } from 'lucide-react'

interface ScreenshotLightboxProps {
  screenshot: Screenshot
  onClose: () => void
}

export function ScreenshotLightbox({ screenshot, onClose }: ScreenshotLightboxProps) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose()
  }, [onClose])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [handleKeyDown])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Full size view"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        transition={{ duration: 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
        className="relative max-w-[90vw] max-h-[90vh] w-full h-full"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="absolute top-4 right-4 flex items-center gap-2 z-10">
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-surface-900/90 backdrop-blur-sm border border-surface-700 text-primary-300 hover:text-white hover:bg-primary-900/50 hover:border-primary-700 transition-all"
            aria-label="Close lightbox"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="relative h-full w-full flex items-center justify-center">
          <Image
            src={screenshot.src}
            alt={screenshot.alt}
            fill
            sizes="(max-width: 1024px) 100vw, 80vw"
            className="object-contain max-w-[90vw] max-h-[85vh] rounded-xl"
            priority
            placeholder="blur"
            blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
          />
        </div>
      </motion.div>
    </motion.div>
  )
}