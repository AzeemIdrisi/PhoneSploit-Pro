"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { CommandBox } from "@/components/ui/CommandBox";
import { StatusChip } from "@/components/ui/StatusChip";
import { GitHubIcon } from "@/components/ui/BrandIcons";
import { repoInfo } from "@/data/constants";
import { useReducedMotion } from "@/hooks";
import TerminalPreview from "./TerminalPreview";
import ToolStrip from "./ToolStrip";

export default function Hero() {
  const reducedMotion = useReducedMotion();

  const scrollToInstall = () => {
    document.getElementById("install")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="relative pt-8 pb-12 sm:pt-10 sm:pb-16 overflow-hidden">
      <div className="container-custom">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <motion.div
            initial={reducedMotion ? false : { opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            <a
              href={`${repoInfo.url}/releases`}
              target="_blank"
              rel="noopener noreferrer"
              className="mb-8 inline-flex group"
            >
              <StatusChip
                variant="red"
                live
                className="px-4 py-2 hover:bg-neon-red/10 transition-colors"
              >
                Release {repoInfo.version}
              </StatusChip>
            </a>

            <h1 className="display-title text-5xl sm:text-6xl md:text-7xl leading-none mb-6">
              <span className="text-outline block">The Android</span>
              <span className="text-white block glitch-hover">Swiss Army</span>
              <span className="text-neon-red glow-text-red block">Knife.</span>
            </h1>

            <p className="mt-6 text-lg font-mono text-muted-foreground max-w-lg mb-8 leading-relaxed">
              All-in-one remote Android testing from a single numbered menu.
              Connect over ADB, mirror with scrcpy, extract data, scan with
              Nmap, and drive Metasploit — without memorizing commands.
            </p>

            <div className="mt-8">
              <CommandBox command={repoInfo.cloneUrl} prompt="root@psp:~#" />
            </div>

            <div className="mt-6">
              <ToolStrip />
            </div>

            <div className="mt-8 flex flex-col sm:flex-row gap-3">
              <Button size="lg" onClick={scrollToInstall}>
                Get Started
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={() =>
                  window.open(repoInfo.url, "_blank", "noopener,noreferrer")
                }
              >
                <GitHubIcon className="h-4 w-4" />
                GitHub
              </Button>
            </div>

            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
              <span>
                <span className="text-neon-red">{repoInfo.starsFormatted}+</span>{" "}
                stars
              </span>
              <span>GPL-3.0</span>
              <span>Python 3.10+</span>
              <span className="text-amber">Educational use</span>
            </div>
          </motion.div>

          <motion.div
            initial={reducedMotion ? false : { opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="relative"
          >
            <TerminalPreview />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
