'use client'

import { useEffect, useCallback, useRef } from 'react'
import { motion } from 'framer-motion'
import Image from 'next/image'
import { Screenshot } from '@/data/screenshots'
import { X } from 'lucide-react'

interface ScreenshotLightboxProps {
  screenshot: Screenshot
  onClose: () => void
}

export function ScreenshotLightbox({ screenshot, onClose }: ScreenshotLightboxProps) {
  const closeRef = useRef<HTMLButtonElement>(null)
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose()
  }, [onClose])

  useEffect(() => {
    closeRef.current?.focus()
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
      className="fixed inset-0 z-[70] flex items-center justify-center bg-black/95 backdrop-blur-sm"
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
            ref={closeRef}
            type="button"
            onClick={onClose}
            className="p-2 bg-background/90 border border-white/20 text-muted-foreground hover:text-white hover:border-neon-red/40 transition-all font-mono"
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
            className="object-contain max-w-[90vw] max-h-[85vh]"
            priority
            placeholder="blur"
            blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
          />
        </div>
      </motion.div>
    </motion.div>
  )
}