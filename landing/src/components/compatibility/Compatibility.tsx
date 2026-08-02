'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Section } from '@/components/ui/Section'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Check, X, Monitor, Smartphone, Terminal, Shield, Cpu, ExternalLink } from 'lucide-react'

const osData = [
  { id: 'ubuntu', name: 'Ubuntu', icon: Monitor, status: 'supported', version: '20.04+', notes: 'Fully tested' },
  { id: 'kali', name: 'Kali Linux', icon: Shield, status: 'supported', version: '2023+', notes: 'Primary dev platform' },
  { id: 'mint', name: 'Linux Mint', icon: Monitor, status: 'supported', version: '21+', notes: 'Fully tested' },
  { id: 'fedora', name: 'Fedora', icon: Monitor, status: 'supported', version: '38+', notes: 'Fully tested' },
  { id: 'arch', name: 'Arch Linux', icon: Terminal, status: 'supported', version: 'Rolling', notes: 'AUR packages available' },
  { id: 'parrot', name: 'Parrot OS', icon: Shield, status: 'supported', version: '5.0+', notes: 'Fully tested' },
  { id: 'windows11', name: 'Windows 11', icon: Monitor, status: 'partial', version: '22H2+', notes: 'Some features limited' },
  { id: 'termux', name: 'Termux (Android)', icon: Smartphone, status: 'supported', version: 'Latest', notes: 'On-device usage' },
]

export default function Compatibility() {
  return (
    <Section id="compatibility" className="relative">
      <div className="max-w-4xl mx-auto text-center mb-16">
        <Badge variant="info" className="mb-4 inline-block">Cross Platform</Badge>
        <h2 className="section-title">Runs Everywhere</h2>
        <p className="section-subtitle mx-auto">
          Tested on major Linux distributions, Windows 11, and Android via Termux. Linux is recommended for the best experience.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto">
        {osData.map((os, index) => (
          <motion.article
            key={os.id}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ delay: index * 0.08, duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
            className={cn(
              'card p-6 text-center group h-full flex flex-col',
              os.status === 'partial' && 'border-yellow-700/50 bg-yellow-900/10'
            )}
          >
            <div className="relative mb-4 flex-shrink-0">
              <os.icon className="h-10 w-10 mx-auto text-primary-400 group-hover:text-primary-300 transition-colors" aria-hidden="true" />
              {os.status === 'partial' && (
                <span className="absolute -top-2 -right-2 px-2 py-0.5 text-xs rounded-full bg-yellow-900/50 text-yellow-300 border border-yellow-700">
                  Partial
                </span>
              )}
              {os.status === 'supported' && (
                <span className="absolute -top-2 -right-2 px-2 py-0.5 text-xs rounded-full bg-green-900/50 text-green-300 border border-green-700">
                  Full
                </span>
              )}
            </div>
            <h3 className="font-semibold text-white mb-1">{os.name}</h3>
            <p className="text-sm text-primary-400 mb-2">{os.version}</p>
            <p className="text-xs text-primary-500 mb-4 flex-1">{os.notes}</p>
            <div className="flex items-center justify-center gap-2 mt-auto">
              {os.status === 'supported' ? (
                <Check className="h-5 w-5 text-accent-500 shrink-0" />
              ) : (
                <X className="h-5 w-5 text-yellow-500 shrink-0" />
              )}
              <span className="text-sm font-medium text-primary-300 capitalize">{os.status}</span>
            </div>
          </motion.article>
        ))}
      </div>

      <div className="mt-12 max-w-3xl mx-auto">
        <Card padding="lg" className="bg-primary-900/20 border-primary-700/50">
          <div className="flex items-start gap-4">
            <Cpu className="h-6 w-6 text-primary-400 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-white">Note on Windows Support</h4>
              <p className="mt-1 text-sm text-primary-300">
                Windows support is experimental. Some features (scrcpy integration, certain ADB operations, Metasploit automation) 
                may not work correctly or require manual setup. For production use, Linux (Ubuntu, Kali, Fedora, Arch) or Termux is strongly recommended.
              </p>
              <p className="mt-2 text-sm text-primary-400">
                New features are primarily tested on Linux. See the <a href="https://github.com/AzeemIdrisi/PhoneSploit-Pro#compatibility" target="_blank" rel="noopener noreferrer" className="underline hover:text-primary-300 flex items-center gap-1">README<ExternalLink className="h-3 w-3" aria-hidden="true" /></a> for detailed compatibility notes.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </Section>
  )
}