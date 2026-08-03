'use client'

import { motion } from 'framer-motion'
import { showcaseVideos } from '@/data/showcase'
import { Section } from '@/components/ui/Section'
import { Badge } from '@/components/ui/Badge'

export default function Showcase() {
  return (
    <Section id="showcase" className="relative">
      <div className="max-w-4xl mx-auto text-center mb-16">
        <Badge variant="info" className="mb-4 inline-block">Video Demos</Badge>
        <h2 className="section-title">Watch PhoneSploit Pro in Action</h2>
        <p className="section-subtitle mx-auto">
          Step-by-step walkthroughs covering device connection, control, and exploitation.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 sm:gap-6">
        {showcaseVideos.map((video, index) => (
          <motion.div
            key={video.id}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ delay: index * 0.1, duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="rounded-2xl overflow-hidden bg-surface-800/50 border border-surface-700"
          >
            <div className="relative aspect-video">
              <iframe
                className="absolute inset-0 h-full w-full"
                src={`https://www.youtube-nocookie.com/embed/${video.videoId}${video.start ? `?start=${video.start}` : ''}`}
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
  )
}