"use client";

import { motion } from "framer-motion";
import { Section } from "@/components/ui/Section";
import { SectionIntro } from "@/components/ui/SectionIntro";

const steps = [
  {
    num: "01",
    title: "Connect",
    body: "Attach over USB or Wi-Fi ADB. List devices, pick a target, and manage the ADB server from the menu.",
  },
  {
    num: "02",
    title: "Control",
    body: "Send keycodes, lock or unlock the screen, reboot modes, and mirror the display with scrcpy.",
  },
  {
    num: "03",
    title: "Extract",
    body: "Pull SMS, contacts, call logs, WhatsApp data, photos, screenshots, and files without juggling shell one-liners.",
  },
  {
    num: "04",
    title: "Exploit",
    body: "Run Nmap against the target and chain Metasploit payloads from the same interface when authorized testing calls for it.",
  },
];

export default function OperatorFlow() {
  return (
    <Section id="workflow" className="relative border-t border-white/5">
      <SectionIntro
        index="02"
        label="WORKFLOW"
        title={
          <>
            Connect. Control. Extract.{" "}
            <span className="text-neon-red">Exploit.</span>
          </>
        }
        subtitle="Four phases, one menu — the same flow security researchers use from first ADB handshake to payload delivery."
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {steps.map((step, index) => (
          <motion.article
            key={step.num}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ delay: index * 0.08, duration: 0.4 }}
            className="panel panel-hover p-6 corner-ticks"
          >
            <span className="font-mono text-2xl font-bold text-neon-red">
              {step.num}
            </span>
            <h3 className="mt-3 font-mono text-sm uppercase tracking-widest text-white font-semibold">
              {step.title}
            </h3>
            <p className="mt-2 text-sm text-muted-foreground font-mono leading-relaxed">
              {step.body}
            </p>
          </motion.article>
        ))}
      </div>
    </Section>
  );
}
