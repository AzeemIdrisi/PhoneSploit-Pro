"use client";

import { motion } from "framer-motion";
import { Section } from "@/components/ui/Section";
import { SectionIntro } from "@/components/ui/SectionIntro";
import { Card } from "@/components/ui/Card";
import { ExternalLink } from "lucide-react";

const matrixRows = [
  { platform: "Ubuntu", version: "20.04+", status: "full" as const },
  { platform: "Kali Linux", version: "2023+", status: "full" as const },
  { platform: "Linux Mint", version: "21+", status: "full" as const },
  { platform: "Fedora", version: "38+", status: "full" as const },
  { platform: "Arch Linux", version: "Rolling", status: "full" as const },
  { platform: "Parrot OS", version: "5.0+", status: "full" as const },
  { platform: "macOS", version: "12+", status: "full" as const },
  { platform: "Windows 11", version: "22H2+", status: "partial" as const },
  { platform: "Termux", version: "Latest", status: "full" as const },
];

export default function Compatibility() {
  return (
    <Section id="compatibility" className="relative border-t border-white/5">
      <SectionIntro
        index="06"
        label="COMPATIBILITY"
        title={
          <>
            Runs on your{" "}
            <span className="text-neon-red">host.</span>
          </>
        }
        subtitle="Linux and macOS are fully supported. Windows is experimental. Termux runs on-device."
      />

      <div className="panel overflow-hidden max-w-4xl">
        <div className="grid grid-cols-[1fr_auto_auto] gap-4 px-4 py-3 border-b border-white/10 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
          <span>Platform</span>
          <span className="hidden sm:inline">Version</span>
          <span>Status</span>
        </div>
        {matrixRows.map((row, index) => (
          <motion.div
            key={row.platform}
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.04 }}
            className="grid grid-cols-[1fr_auto_auto] gap-4 px-4 py-3 border-b border-white/5 last:border-0 items-center font-mono text-sm hover:bg-white/[0.02]"
          >
            <span className="text-white">{row.platform}</span>
            <span className="hidden sm:inline text-muted-foreground text-xs">
              {row.version}
            </span>
            <span
              className={
                row.status === "full" ? "status-full" : "status-partial"
              }
            >
              {row.status}
            </span>
          </motion.div>
        ))}
      </div>

      <div className="mt-8 max-w-4xl">
        <Card padding="lg" className="border-amber/30 bg-amber/5">
          <h4 className="font-mono text-xs uppercase tracking-widest text-amber">
            Windows — partial support
          </h4>
          <p className="mt-2 text-sm text-muted-foreground font-mono leading-relaxed">
            scrcpy integration, some ADB operations, and Metasploit automation
            may require manual setup. New features are tested primarily on
            Linux. See the{" "}
            <a
              href="https://github.com/AzeemIdrisi/PhoneSploit-Pro#compatibility"
              target="_blank"
              rel="noopener noreferrer"
              className="text-neon-cyan hover:text-white inline-flex items-center gap-1 underline"
            >
              README
              <ExternalLink className="h-3 w-3" aria-hidden="true" />
            </a>{" "}
            for details.
          </p>
        </Card>
      </div>
    </Section>
  );
}
