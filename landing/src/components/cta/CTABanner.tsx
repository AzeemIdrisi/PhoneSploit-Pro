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
    ghost:
      "inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 font-semibold text-primary-300 hover:text-white hover:bg-primary-900/30 transition-colors duration-200",
  };

  return (
    <a
      href={href}
      target={external ? "_blank" : undefined}
      rel={external ? "noopener noreferrer" : undefined}
      className={cn(
        variants[variant],
        "group w-full sm:w-auto min-w-[160px] inline-flex items-center justify-center gap-2",
      )}
    >
      <Icon className="mr-2 h-5 w-5" aria-hidden="true" />
      {label}
      {external && (
        <ExternalLink
          className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1"
          aria-hidden="true"
        />
      )}
    </a>
  );
}

export default function CTABanner() {
  return (
    <section className="relative py-20 sm:py-24" aria-labelledby="cta-heading">
      <div
        className="absolute inset-0 bg-linear-to-r from-primary-900/20 via-transparent to-primary-900/10"
        aria-hidden="true"
      />
      <div
        className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary-900/10 via-transparent to-transparent"
        aria-hidden="true"
      />

      <Container className="relative">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
          className="max-w-3xl mx-auto text-center"
        >
          <h2 id="cta-heading" className="section-title">
            Ready to Test Your Android Security?
          </h2>
          <p className="section-subtitle mx-auto">
            Join thousands of security researchers using PhoneSploit Pro. Star
            the repo, report issues, or start a discussion.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
            {ctaButtons.map((btn) => (
              <CTAButton key={btn.label} {...btn} />
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="mt-10 flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-sm text-primary-400"
          >
            <div className="flex items-center gap-2">
              <Star className="h-4 w-4 text-accent-500" aria-hidden="true" />
              <span>Star the repo to support development</span>
            </div>
            <div className="flex items-center gap-2">
              <GitHubIcon className="h-4 w-4" aria-hidden="true" />
              <span>MIT Licensed</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertTriangle
                className="h-4 w-4 text-yellow-500"
                aria-hidden="true"
              />
              <span>Educational use only</span>
            </div>
          </motion.div>
        </motion.div>
      </Container>
    </section>
  );
}
