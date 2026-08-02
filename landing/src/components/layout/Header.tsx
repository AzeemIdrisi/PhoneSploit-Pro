'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Menu, X, Github } from 'lucide-react'
import { useState, useEffect } from 'react'
import { navLinks } from '@/data/constants'
import { getBasePath } from '@/lib/utils'

export default function Header() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const { scrollY } = useScroll()
  const y = useTransform(scrollY, [0, 100], [0, 1])
  const basePath = getBasePath()

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <motion.header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        scrolled && 'bg-surface-900/90 backdrop-blur-md border-b border-surface-700 shadow-xl shadow-primary-900/20'
      )}
      style={{ opacity: y }}
    >
      <nav className="container-custom" aria-label="Main navigation">
        <div className="flex h-16 items-center justify-between">
          <a href={`${basePath}/`} className="flex items-center gap-2 text-xl font-bold text-white hover:opacity-80 transition-opacity" aria-label="PhoneSploit Pro Home">
            <span className="text-primary-400">PhoneSploit</span>
            <span className="text-white">Pro</span>
          </a>

          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-primary-300 hover:text-white transition-colors"
              >
                {link.label}
              </a>
            ))}
            <a
              href="https://github.com/AzeemIdrisi/PhoneSploit-Pro"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary text-sm px-4 py-2"
            >
              <Github className="mr-2 h-4 w-4" />
              GitHub
            </a>
          </div>

          <div className="md:hidden flex items-center gap-4">
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 rounded-lg text-primary-300 hover:bg-surface-700 hover:text-white transition-colors"
              aria-expanded={mobileOpen}
              aria-controls="mobile-menu"
              aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
            >
              {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        <motion.div
          id="mobile-menu"
          className="md:hidden overflow-hidden bg-surface-900 border-t border-surface-700"
          initial={false}
          animate={{ height: mobileOpen ? 'auto' : 0, opacity: mobileOpen ? 1 : 0 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
        >
          <div className="py-4 space-y-2 px-4">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="block px-4 py-2 rounded-lg text-primary-300 hover:bg-surface-700 hover:text-white transition-colors"
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </a>
            ))}
            <a
              href="https://github.com/AzeemIdrisi/PhoneSploit-Pro"
              target="_blank"
              rel="noopener noreferrer"
              className="block px-4 py-2 rounded-lg text-primary-300 hover:bg-surface-700 hover:text-white transition-colors"
              onClick={() => setMobileOpen(false)}
            >
              View on GitHub
            </a>
          </div>
        </motion.div>
      </nav>
    </motion.header>
  )
}