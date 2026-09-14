"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { Section } from "@/components/ui/Section";
import { SectionIntro } from "@/components/ui/SectionIntro";
import { faqItems } from "@/data/faq";
import { ChevronDown } from "lucide-react";

export default function FAQ() {
  const [openId, setOpenId] = useState<string | null>(faqItems[0]?.id ?? null);

  return (
    <Section id="faq" className="relative border-t border-white/5">
      <SectionIntro
        index="07"
        label="FAQ"
        title="Common questions."
        subtitle="Legality, requirements, and setup — straight answers for researchers and students."
      />

      <div className="max-w-3xl space-y-2">
        {faqItems.map((item, index) => {
          const isOpen = openId === item.id;
          const num = String(index + 1).padStart(2, "0");
          return (
            <div
              key={item.id}
              className="panel border-white/10 overflow-hidden"
            >
              <button
                type="button"
                id={`faq-trigger-${item.id}`}
                aria-expanded={isOpen}
                aria-controls={`faq-panel-${item.id}`}
                onClick={() => setOpenId(isOpen ? null : item.id)}
                className="flex w-full items-center justify-between gap-4 p-4 sm:p-6 text-left font-mono hover:no-underline group"
              >
              <div className="flex gap-4 min-w-0">
                <span className="text-neon-red text-xs shrink-0 hidden sm:inline pt-0.5">
                  [{num}]
                </span>
                <span className="text-xs sm:text-sm font-bold uppercase tracking-widest text-white group-hover:text-neon-cyan transition-colors">
                  {item.question}
                </span>
              </div>
                <ChevronDown
                  className={cn(
                    "h-4 w-4 shrink-0 text-muted-foreground transition-transform",
                    isOpen && "rotate-180",
                  )}
                  aria-hidden
                />
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    id={`faq-panel-${item.id}`}
                    role="region"
                    aria-labelledby={`faq-trigger-${item.id}`}
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25 }}
                    className="overflow-hidden"
                  >
                    <p className="px-4 sm:px-5 pb-5 pl-12 sm:pl-14 text-sm text-muted-foreground font-mono leading-relaxed border-t border-white/5 pt-4">
                      {item.answer}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </Section>
  );
}
