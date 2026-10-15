"use client";

import { motion } from "framer-motion";
import { cn, getBasePath } from "@/lib/utils";
import { Menu, X } from "lucide-react";
import { useState, useEffect } from "react";
import { navLinks, repoInfo } from "@/data/constants";
import { GitHubIcon } from "../ui/BrandIcons";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const basePath = getBasePath();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed top-2 left-1/2 z-50 w-[95%] max-w-7xl -translate-x-1/2 transition-all duration-300 panel corner-ticks px-4 sm:px-6 py-3",
        scrolled && "bg-black/80",
      )}
    >
      <nav aria-label="Main navigation">
        <div className="flex items-center justify-between">
          <a
            href={`${basePath}/`}
            className="group flex items-center gap-2"
            aria-label="PhoneSploit Pro Home"
          >
            <span className="font-mono text-sm sm:text-base font-bold tracking-[0.18em] uppercase text-white glitch-hover">
              PHONESPLOIT
            </span>
            <span className="font-mono text-sm sm:text-base font-bold tracking-[0.18em] uppercase text-neon-red">
              PRO
            </span>
          </a>

          <div className="hidden lg:flex items-center gap-4 xl:gap-6">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="nav-link group whitespace-nowrap"
              >
                <span className="nav-caret">&gt;</span>
                {link.label}
              </a>
            ))}
            <a
              href={repoInfo.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary text-[10px] px-4 py-2"
            >
              <GitHubIcon className="w-4 h-4" /> GITHUB
            </a>
          </div>

          <div className="lg:hidden flex items-center">
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 border border-neon-red/20 text-neon-red hover:text-white transition-colors"
              aria-expanded={mobileOpen}
              aria-controls="mobile-menu"
              aria-label={mobileOpen ? "Close menu" : "Open menu"}
            >
              {mobileOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>

        <motion.div
          id="mobile-menu"
          className="lg:hidden overflow-hidden"
          initial={false}
          animate={{
            height: mobileOpen ? "auto" : 0,
            opacity: mobileOpen ? 1 : 0,
          }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          <div
            className="pt-4 space-y-1"
            inert={!mobileOpen}
            aria-hidden={!mobileOpen}
          >
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="flex items-center gap-3 px-2 py-3 font-mono text-xs uppercase tracking-widest text-muted-foreground hover:text-neon-cyan transition-colors"
                onClick={() => setMobileOpen(false)}
              >
                <span className="text-neon-red">{link.num}</span>
                {link.label}
              </a>
            ))}
            <a
              href={repoInfo.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block mt-2 btn-primary text-center text-[10px]"
              onClick={() => setMobileOpen(false)}
            >
              GITHUB
            </a>
          </div>
        </motion.div>
      </nav>
    </header>
  );
}
