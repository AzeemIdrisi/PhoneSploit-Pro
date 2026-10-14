"use client";

import { motion } from "framer-motion";
import { Container } from "@/components/ui/Container";
import { cn } from "@/lib/utils";
import { Star, MessageSquare, AlertTriangle, ExternalLink } from "lucide-react";
import { GitHubIcon } from "@/components/ui/BrandIcons";

type CTAButtonProps = {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  external: boolean;
  variant: "primary" | "secondary" | "ghost";
};

const ctaButtons: CTAButtonProps[] = [
  {
    href: "https://github.com/AzeemIdrisi/PhoneSploit-Pro",
    label: "View on GitHub",
    icon: GitHubIcon,
    external: true,
    variant: "primary",
  },
  {
    href: "https://github.com/AzeemIdrisi/PhoneSploit-Pro/issues/new/choose",
    label: "Report Issue",
    icon: AlertTriangle,
    external: true,
    variant: "secondary",
  },
  {
    href: "https://github.com/AzeemIdrisi/PhoneSploit-Pro/discussions",
    label: "Discussions",
    icon: MessageSquare,
    external: true,
    variant: "ghost",
  },
];

function CTAButton({
  href,
  label,
  icon: Icon,
  external,
  variant,
}: CTAButtonProps) {
  const variants = {
    primary: "btn-primary",
    secondary: "btn-secondary",
    ghost: "btn-ghost border border-white/15 px-6 py-3",
  };

  return (
    <a
      href={href}
      target={external ? "_blank" : undefined}
      rel={external ? "noopener noreferrer" : undefined}
      className={cn(
        variants[variant],
        "group w-full sm:w-auto min-w-[140px] inline-flex items-center justify-center gap-2",
      )}
    >
      <Icon className="h-4 w-4" aria-hidden="true" />
      {label}
      {external && variant === "primary" && (
        <ExternalLink
          className="h-3.5 w-3.5 opacity-70"
          aria-hidden="true"
        />
      )}
    </a>
  );
}

export default function CTABanner() {
  return (
    <section
      className="relative py-20 sm:py-24 border-t border-white/10"
      aria-labelledby="cta-heading"
    >
      <Container className="relative">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="max-w-3xl mx-auto text-center panel corner-ticks p-8 sm:p-12"
        >
          <p className="section-eyebrow mb-4">[ READY ]</p>
          <h2 id="cta-heading" className="section-title glitch-hover">
            Ready to own the{" "}
            <span className="text-neon-red glow-text-red">device?</span>
          </h2>
          <p className="section-subtitle mx-auto">
            Star the repo, report bugs, or join discussions. Use only on systems
            you are authorized to test.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
            {ctaButtons.map((btn) => (
              <CTAButton key={btn.label} {...btn} />
            ))}
          </div>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
            <div className="flex items-center gap-2">
              <Star className="h-3.5 w-3.5 text-neon-red" aria-hidden="true" />
              <span>Star the repo</span>
            </div>
            <span>GPL-3.0</span>
            <div className="flex items-center gap-2 text-amber">
              <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
              <span>Educational use only</span>
            </div>
          </div>
        </motion.div>
      </Container>
    </section>
  );
}
