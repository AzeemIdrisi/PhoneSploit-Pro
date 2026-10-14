"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { StatusChip } from "@/components/ui/StatusChip";
import { Section } from "@/components/ui/Section";
import { SectionIntro } from "@/components/ui/SectionIntro";
import { CommandList } from "@/components/ui/CommandBox";
import { Terminal, Monitor, Smartphone, ExternalLink } from "lucide-react";
import { GitHubIcon } from "@/components/ui/BrandIcons";

const installTabs = [
  { id: "linux", label: "Linux / macOS", icon: Terminal, recommended: true },
  { id: "windows", label: "Windows", icon: Monitor, recommended: false },
  { id: "termux", label: "Termux", icon: Smartphone, recommended: false },
] as const;

type InstallTab = (typeof installTabs)[number]["id"];

const installSteps: Record<
  InstallTab,
  {
    title: string;
    description: string;
    runCommands: string[];
    depsCommands?: string[];
    prerequisites: string[];
  }
> = {
  linux: {
    title: "Linux / macOS",
    description: "Full feature support — recommended host",
    prerequisites: [
      "REQ: Python 3.10+",
      "REQ: Git",
      "REQ: ADB, scrcpy, Nmap, Metasploit (optional install.sh)",
    ],
    runCommands: [
      "git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git",
      "cd PhoneSploit-Pro/",
      "python3 -m venv .venv",
      "source .venv/bin/activate",
      "pip install -r requirements.txt",
      "python3 phonesploitpro.py",
    ],
    depsCommands: ["chmod +x install.sh", "./install.sh"],
  },
  windows: {
    title: "Windows",
    description: "Run PowerShell as Administrator for install.ps1",
    prerequisites: [
      "REQ: Python 3.10+",
      "REQ: Git for Windows",
      "REQ: platform-tools in project folder",
    ],
    runCommands: [
      "git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git",
      "cd PhoneSploit-Pro/",
      "python -m venv .venv",
      ".\\.venv\\Scripts\\activate",
      "pip install -r requirements.txt",
      "python phonesploitpro.py",
    ],
    depsCommands: [
      "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass",
      ".\\install.ps1",
    ],
  },
  termux: {
    title: "Termux (Android)",
    description: "Run on-device from Termux",
    prerequisites: [
      "REQ: Termux (F-Droid)",
      "REQ: Termux:API addon",
      "REQ: Storage permission",
    ],
    runCommands: [
      "pkg update && pkg upgrade",
      "pkg install python git nmap android-tools",
      "git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git",
      "cd PhoneSploit-Pro",
      "python -m venv .venv",
      "source .venv/bin/activate",
      "pip install -r requirements.txt",
      "python phonesploitpro.py",
    ],
    depsCommands: ["chmod +x install.sh", "./install.sh"],
  },
};

export default function Install() {
  const [activeTab, setActiveTab] = useState<InstallTab>("linux");
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);

  const current = installSteps[activeTab];

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCommand(text);
      setTimeout(() => setCopiedCommand(null), 2000);
    } catch {
      setCopiedCommand(null);
    }
  };

  return (
    <Section id="install" className="relative border-t border-white/5">
      <SectionIntro
        index="05"
        label="INSTALL"
        title={
          <>
            Get started in{" "}
            <span className="text-neon-red">minutes.</span>
          </>
        }
        subtitle="Clone, virtualenv, pip install, run. Use install.sh or install.ps1 when you need ADB, scrcpy, Nmap, or Metasploit on PATH."
      />

      <div
        className="flex flex-wrap gap-2 mb-8"
        role="tablist"
        aria-label="Installation platforms"
      >
        {installTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              aria-controls={`install-panel-${tab.id}`}
              id={`install-tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "inline-flex items-center gap-2 px-3 py-2 font-mono text-[10px] uppercase tracking-widest border transition-colors",
                isActive
                  ? "border-neon-red/50 text-white bg-neon-red/10"
                  : "border-white/15 text-muted-foreground hover:text-white",
              )}
            >
              <Icon className="h-3.5 w-3.5" aria-hidden="true" />
              {tab.label}
              {tab.recommended && (
                <StatusChip variant="red" className="py-0 px-1.5 text-[8px]">
                  REC
                </StatusChip>
              )}
            </button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          id={`install-panel-${activeTab}`}
          role="tabpanel"
          aria-labelledby={`install-tab-${activeTab}`}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -16 }}
          transition={{ duration: 0.25 }}
          className="max-w-4xl"
        >
          <Card padding="lg" ticks className="mb-6">
            <div className="mb-6 border-b border-white/10 pb-4">
              <h3 className="font-mono text-sm uppercase tracking-widest text-white">
                {current.title}
              </h3>
              <p className="mt-1 text-sm text-muted-foreground font-mono">
                {current.description}
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h4 className="font-mono text-[10px] uppercase tracking-widest text-neon-cyan mb-3">
                  Prerequisites
                </h4>
                <ul className="space-y-2 font-mono text-xs text-muted-foreground">
                  {current.prerequisites.map((req, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-neon-red">›</span>
                      {req}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="font-mono text-[10px] uppercase tracking-widest text-neon-cyan mb-3">
                  Run
                </h4>
                <CommandList
                  commands={current.runCommands}
                  copiedCommand={copiedCommand}
                  onCopy={copyToClipboard}
                />
              </div>
            </div>

            {current.depsCommands && current.depsCommands.length > 0 && (
              <div className="mt-8">
                <h4 className="font-mono text-[10px] uppercase tracking-widest text-neon-cyan mb-3">
                  Dependencies (optional)
                </h4>
                <p className="text-xs text-muted-foreground font-mono mb-3">
                  After clone, if ADB, scrcpy, Nmap, or Metasploit are missing.
                </p>
                <CommandList
                  commands={current.depsCommands}
                  copiedCommand={copiedCommand}
                  onCopy={copyToClipboard}
                  startIndex={current.runCommands.length}
                />
              </div>
            )}
          </Card>

          <Card padding="lg" className="border-neon-cyan/20 bg-neon-cyan/5">
            <div className="flex items-start gap-4">
              <GitHubIcon className="h-5 w-5 text-neon-cyan shrink-0 mt-0.5" />
              <div>
                <h4 className="font-mono text-xs uppercase tracking-widest text-white">
                  README — device setup & troubleshooting
                </h4>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro#getting-started"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-flex btn-secondary text-[10px]"
                >
                  Getting started
                  <ExternalLink className="h-3 w-3 ml-2" aria-hidden="true" />
                </a>
              </div>
            </div>
          </Card>
        </motion.div>
      </AnimatePresence>

      <p className="mt-10 text-sm font-mono text-muted-foreground">
        Need help?{" "}
        <a
          href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/issues"
          target="_blank"
          rel="noopener noreferrer"
          className="text-neon-cyan hover:text-white underline"
        >
          Open an issue
        </a>
        .
      </p>
    </Section>
  );
}
