'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Section } from '@/components/ui/Section'
import { Copy, Check, Terminal, Monitor, Smartphone, AlertTriangle, ExternalLink } from 'lucide-react'
import { GitHubIcon } from '@/components/ui/BrandIcons'

const installTabs = [
  { id: 'linux', label: 'Linux / macOS', icon: Terminal },
  { id: 'windows', label: 'Windows', icon: Monitor },
  { id: 'termux', label: 'Termux (Android)', icon: Smartphone },
] as const

type InstallTab = typeof installTabs[number]['id']

const installSteps: Record<InstallTab, { title: string; description: string; commands: string[]; prerequisites: string[] }> = {
  linux: {
    title: 'Linux / macOS Installation',
    description: 'Recommended platform with full feature support',
    prerequisites: [
      'Python 3.10 or higher',
      'Git',
      'Internet connection for downloading dependencies',
    ],
    commands: [
      'git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git',
      'cd PhoneSploit-Pro/',
      'chmod +x install.sh',
      './install.sh',
      'python3 -m venv .venv',
      'source .venv/bin/activate',
      'pip install -r requirements.txt',
      'python3 phonesploitpro.py',
    ],
  },
  windows: {
    title: 'Windows Installation',
    description: 'Run PowerShell as Administrator for best results',
    prerequisites: [
      'Python 3.10+ (from python.org or Microsoft Store)',
      'Git for Windows',
      'PowerShell 5.1+ (run as Administrator)',
      'Manual ADB/scrcpy setup required',
    ],
    commands: [
      'git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git',
      'cd PhoneSploit-Pro',
      'Set-ExecutionPolicy -Scope Process Bypass',
      '.\\install.ps1',
      'python -m venv .venv',
      '.\\.venv\\Scripts\\activate',
      'pip install -r requirements.txt',
      '# Download platform-tools & scrcpy manually, copy to project folder',
      'python phonesploitpro.py',
    ],
  },
  termux: {
    title: 'Termux (Android) Installation',
    description: 'Run PhoneSploit Pro directly on your Android device',
    prerequisites: [
      'Termux app (from F-Droid recommended)',
      'Termux:API addon for device access',
      'Storage permission granted',
      'Root access optional but recommended',
    ],
    commands: [
      'pkg update && pkg upgrade',
      'pkg install python git nmap',
      'pkg install android-tools  # for ADB',
      'git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git',
      'cd PhoneSploit-Pro',
      'chmod +x install.sh',
      './install.sh',
      'python -m venv .venv',
      'source .venv/bin/activate',
      'pip install -r requirements.txt',
      'python phonesploitpro.py',
    ],
  },
}

export default function Install() {
  const [activeTab, setActiveTab] = useState<InstallTab>('linux')
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null)

  const current = installSteps[activeTab]

  const copyToClipboard = async (text: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedCommand(text)
    setTimeout(() => setCopiedCommand(null), 2000)
  }

  return (
    <Section id="install" className="relative">
      <div className="max-w-4xl mx-auto text-center mb-12">
        <Badge variant="info" className="mb-4 inline-block">Quick Start</Badge>
        <h2 className="section-title">Get Started in Minutes</h2>
        <p className="section-subtitle mx-auto">
          Automated installer detects your OS and sets up all dependencies. Choose your platform below.
        </p>
      </div>

      <div className="flex flex-wrap justify-center gap-2 mb-10" role="tablist" aria-label="Installation platforms">
        {installTabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`panel-${tab.id}`}
              id={`install-tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'relative flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 whitespace-nowrap',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-900',
                activeTab === tab.id
                  ? 'bg-primary-900/50 text-white border border-primary-700 shadow-lg shadow-primary-900/20'
                  : 'text-primary-300 hover:text-white hover:bg-surface-700/50 border border-surface-700'
              )}
            >
              <Icon className="h-4 w-4" aria-hidden="true" />
              {tab.label}
            </button>
          )
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          id={`panel-${activeTab}`}
          role="tabpanel"
          aria-labelledby={`install-tab-${activeTab}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
          className="max-w-4xl mx-auto"
        >
          <Card padding="lg" className="mb-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <div className="text-left">
                <h3 className="text-xl font-bold text-white">{current.title}</h3>
                <p className="mt-1 text-primary-400">{current.description}</p>
              </div>
              <Badge variant="success" className="self-start shrink-0">
                <Check className="h-3 w-3 mr-1" />
                Recommended
              </Badge>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
              <div>
                <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-500 shrink-0" />
                  Prerequisites
                </h4>
                <ul className="space-y-2">
                  {current.prerequisites.map((req, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-primary-300">
                      <Check className="h-4 w-4 text-accent-500 shrink-0 mt-0.5" />
                      <span>{req}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <Terminal className="h-5 w-5 text-primary-400 shrink-0" />
                  Installation Commands
                </h4>
                <div className="bg-surface-900/50 rounded-xl border border-surface-700 p-4 font-mono text-sm overflow-x-auto">
                  {current.commands.map((cmd, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-3 py-1.5 border-b last:border-0 border-surface-700 group"
                    >
                      <span className="text-primary-500 shrink-0 mt-0.5">{i + 1}.</span>
                      <code className="text-primary-200 flex-1 break-all whitespace-pre-wrap">{cmd}</code>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(cmd)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0 shrink-0"
                        aria-label={copiedCommand === cmd ? 'Copied!' : 'Copy command'}
                      >
                        {copiedCommand === cmd ? (
                          <Check className="h-4 w-4 text-accent-500" />
                        ) : (
                          <Copy className="h-4 w-4 text-primary-400" />
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>

          <Card padding="lg" className="bg-primary-900/20 border-primary-700/50">
            <div className="flex items-start gap-4">
              <GitHubIcon className="h-6 w-6 text-primary-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-white">Run from GitHub (Alternative)</h4>
                <p className="mt-1 text-sm text-primary-300">
                  Skip local setup? Use GitHub Codespaces or Gitpod for an instant cloud development environment.
                </p>
                <div className="mt-3 flex gap-3">
                  <a
                    href="https://github.com/AzeemIdrisi/PhoneSploit-Pro"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary text-sm"
                  >
                    <GitHubIcon className="mr-2 h-4 w-4" />
                    Open Repository
                    <ExternalLink className="ml-2 h-4 w-4" aria-hidden="true" />
                  </a>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </AnimatePresence>

      <div className="mt-12 text-center">
        <p className="text-primary-400 mb-4">
          Need help? <a href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/issues" target="_blank" rel="noopener noreferrer" className="text-primary-300 hover:text-white underline">Open an issue</a> or check the <a href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/wiki" target="_blank" rel="noopener noreferrer" className="text-primary-300 hover:text-white underline">Wiki</a>
        </p>
      </div>
    </Section>
  )
}