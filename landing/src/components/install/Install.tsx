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
  { id: 'linux', label: 'Linux / macOS', icon: Terminal, recommended: true },
  { id: 'windows', label: 'Windows', icon: Monitor, recommended: false },
  { id: 'termux', label: 'Termux (Android)', icon: Smartphone, recommended: false },
] as const

type InstallTab = typeof installTabs[number]['id']

const installSteps: Record<
  InstallTab,
  {
    title: string
    description: string
    runCommands: string[]
    depsCommands?: string[]
    prerequisites: string[]
  }
> = {
  linux: {
    title: 'Linux / macOS Installation',
    description: 'Recommended platform with full feature support',
    prerequisites: [
      'Python 3.10 or higher',
      'Git',
      'ADB, scrcpy, Nmap, and Metasploit (see dependency installer below)',
    ],
    runCommands: [
      'git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git',
      'cd PhoneSploit-Pro/',
      'python3 -m venv .venv',
      'source .venv/bin/activate',
      'pip install -r requirements.txt',
      'python3 phonesploitpro.py',
    ],
    depsCommands: [
      'chmod +x install.sh',
      './install.sh',
    ],
  },
  windows: {
    title: 'Windows Installation',
    description: 'Run PowerShell as Administrator when using the dependency installer',
    prerequisites: [
      'Python 3.10+ (from python.org or Microsoft Store)',
      'Git for Windows',
      'Download platform-tools into the project folder before running',
    ],
    runCommands: [
      'git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git',
      'cd PhoneSploit-Pro/',
      'python -m venv .venv',
      '.\\.venv\\Scripts\\activate',
      'pip install -r requirements.txt',
      'python phonesploitpro.py',
    ],
    depsCommands: [
      'Set-ExecutionPolicy -Scope Process Bypass',
      '.\\install.ps1',
    ],
  },
  termux: {
    title: 'Termux (Android) Installation',
    description: 'Run PhoneSploit Pro directly on your Android device',
    prerequisites: [
      'Termux app (from F-Droid recommended)',
      'Termux:API addon for device access',
      'Storage permission granted',
    ],
    runCommands: [
      'pkg update && pkg upgrade',
      'pkg install python git nmap android-tools',
      'git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git',
      'cd PhoneSploit-Pro',
      'python -m venv .venv',
      'source .venv/bin/activate',
      'pip install -r requirements.txt',
      'python phonesploitpro.py',
    ],
    depsCommands: [
      'chmod +x install.sh',
      './install.sh',
    ],
  },
}

export default function Install() {
  const [activeTab, setActiveTab] = useState<InstallTab>('linux')
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null)

  const current = installSteps[activeTab]
  const tabMeta = installTabs.find((t) => t.id === activeTab)!

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedCommand(text)
      setTimeout(() => setCopiedCommand(null), 2000)
    } catch {
      setCopiedCommand(null)
    }
  }

  const renderCommandBlock = (commands: string[], startIndex = 0) => (
    <div className="bg-surface-900/50 rounded-xl border border-surface-700 p-4 font-mono text-sm overflow-x-auto">
      {commands.map((cmd, i) => (
        <div
          key={`${startIndex}-${i}`}
          className="flex items-start gap-3 py-1.5 border-b last:border-0 border-surface-700 group"
        >
          <span className="text-primary-500 shrink-0 mt-0.5">{startIndex + i + 1}.</span>
          <code className="text-primary-200 flex-1 break-all whitespace-pre-wrap">{cmd}</code>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => copyToClipboard(cmd)}
            className="h-8 w-8 p-0 shrink-0 opacity-70 hover:opacity-100 sm:opacity-100"
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
  )

  return (
    <Section id="install" className="relative">
      <div className="max-w-4xl mx-auto text-center mb-12">
        <Badge variant="info" className="mb-4 inline-block">Quick Start</Badge>
        <h2 className="section-title">Get Started in Minutes</h2>
        <p className="section-subtitle mx-auto">
          Clone the repo, create a virtual environment, install Python requirements, and run. Use the bundled installer when you need ADB, scrcpy, Nmap, or Metasploit.
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
              {tabMeta.recommended && (
                <Badge variant="success" className="self-start shrink-0">
                  <Check className="h-3 w-3 mr-1" />
                  Recommended
                </Badge>
              )}
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
                  Run PhoneSploit Pro
                </h4>
                {renderCommandBlock(current.runCommands)}
              </div>
            </div>

            {current.depsCommands && current.depsCommands.length > 0 && (
              <div className="mt-8">
                <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <Terminal className="h-5 w-5 text-primary-400 shrink-0" />
                  Install dependencies (optional)
                </h4>
                <p className="text-sm text-primary-400 mb-3">
                  Run after cloning if ADB, scrcpy, Nmap, or Metasploit are not already on your PATH.
                </p>
                {renderCommandBlock(current.depsCommands, current.runCommands.length)}
              </div>
            )}
          </Card>

          <Card padding="lg" className="bg-primary-900/20 border-primary-700/50">
            <div className="flex items-start gap-4">
              <GitHubIcon className="h-6 w-6 text-primary-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-white">More in the README</h4>
                <p className="mt-1 text-sm text-primary-300">
                  Device setup, manual tool installation, compatibility notes, and troubleshooting live in the repository README.
                </p>
                <div className="mt-3 flex gap-3">
                  <a
                    href="https://github.com/AzeemIdrisi/PhoneSploit-Pro#getting-started"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary text-sm"
                  >
                    <GitHubIcon className="mr-2 h-4 w-4" />
                    Getting started
                    <ExternalLink className="ml-2 h-4 w-4" aria-hidden="true" />
                  </a>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </AnimatePresence>

      <div className="mt-12 text-center">
        <p className="text-primary-400">
          Need help?{' '}
          <a
            href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/issues"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-300 hover:text-white underline"
          >
            Open an issue
          </a>{' '}
          or read the{' '}
          <a
            href="https://github.com/AzeemIdrisi/PhoneSploit-Pro#getting-started"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-300 hover:text-white underline"
          >
            Getting started guide
          </a>
          .
        </p>
      </div>
    </Section>
  )
}
