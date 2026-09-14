"use client";

import { useState } from "react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { screenshots, Screenshot } from "@/data/screenshots";
import { ScreenshotLightbox } from "./ScreenshotLightbox";
import { Section } from "@/components/ui/Section";
import { SectionIntro } from "@/components/ui/SectionIntro";
import { Maximize } from "lucide-react";

export default function Screenshots() {
  const [openImage, setOpenImage] = useState<Screenshot | null>(null);
  const screenshot = screenshots[0];

  if (!screenshot) {
    return null;
  }

  return (
    <Section id="screenshot" className="relative border-t border-white/5">
      <SectionIntro
        index="04"
        label="INTERFACE"
        title={
          <>
            The Master <span className="text-neon-red">Menu</span>
          </>
        }
        subtitle="Pick an option from the single-page interface — every feature maps to a menu entry you can run immediately."
        align="center"
        className="mx-auto text-center"
      />

      <div className="max-w-5xl mx-auto">
        <motion.article
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.5 }}
          className="group panel corner-ticks overflow-hidden cursor-zoom-in"
        >
          <div className="flex items-center gap-2 border-b border-white/10 px-3 py-2 bg-surface-950">
            <span className="h-2 w-2 bg-neon-red" aria-hidden />
            <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              phonesploitpro.py — session
            </span>
          </div>
          <div className="relative w-full bg-surface-950">
            <Image
              src={screenshot.src}
              alt={screenshot.alt}
              width={1920}
              height={1080}
              sizes="(max-width: 1024px) 100vw, 80rem"
              className="w-full h-auto object-contain"
              placeholder="blur"
              blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            />
            <button
              type="button"
              onClick={() => setOpenImage(screenshot)}
              className="absolute inset-0 flex items-center justify-center"
              aria-label="View full size screenshot"
            >
              <span className="flex items-center gap-2 px-4 py-2 font-mono text-[10px] uppercase tracking-widest text-white bg-background/90 border border-white/20 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity">
                <Maximize className="h-3.5 w-3.5" aria-hidden="true" />
                Full size
              </span>
            </button>
          </div>
        </motion.article>
      </div>

      <AnimatePresence>
        {openImage && (
          <ScreenshotLightbox
            screenshot={openImage}
            onClose={() => setOpenImage(null)}
          />
        )}
      </AnimatePresence>
    </Section>
  );
}
