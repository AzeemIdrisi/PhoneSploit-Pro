"use client";

import { motion } from "framer-motion";
import { showcaseVideos } from "@/data/showcase";
import { Section } from "@/components/ui/Section";
import { SectionIntro } from "@/components/ui/SectionIntro";

export default function Showcase() {
  return (
    <Section id="demos" className="relative border-t border-white/5">
      <SectionIntro
        index="01"
        label="DEMOS"
        title={
          <>
            Watch it{" "}
            <span className="text-neon-red">in action.</span>
          </>
        }
        subtitle="Step-by-step walkthroughs for connection, device control, and exploitation workflows."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-5">
        {showcaseVideos.map((video, index) => (
          <motion.div
            key={video.id}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ delay: index * 0.08, duration: 0.45 }}
            className="panel overflow-hidden corner-ticks"
          >
            <div className="flex items-center gap-2 border-b border-white/10 px-3 py-2 bg-surface-950">
              <span className="h-2 w-2 bg-neon-red shrink-0" aria-hidden />
              <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground truncate">
                DEMO_{String(index + 1).padStart(2, "0")} — {video.title}
              </span>
            </div>
            <div className="relative aspect-video bg-black">
              <iframe
                className="absolute inset-0 h-full w-full"
                src={`https://www.youtube-nocookie.com/embed/${video.videoId}${video.start ? `?start=${video.start}` : ""}`}
                title={video.title}
                loading="lazy"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                referrerPolicy="strict-origin-when-cross-origin"
                allowFullScreen
              />
            </div>
          </motion.div>
        ))}
      </div>
    </Section>
  );
}
