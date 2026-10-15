"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { cn } from "@/lib/utils";
import {
  featureCategories,
  features,
  featureCount,
  FeatureCategoryFilter,
} from "@/data/features";
import { FeatureRow } from "./FeatureRow";
import { Section } from "@/components/ui/Section";
import { SectionIntro } from "@/components/ui/SectionIntro";
import { ChevronDown, ExternalLink } from "lucide-react";

const COLLAPSED_COUNT = 12;

export default function Features() {
  const [activeCategory, setActiveCategory] =
    useState<FeatureCategoryFilter>("all");
  const [expanded, setExpanded] = useState(false);

  const selectCategory = (cat: FeatureCategoryFilter) => {
    if (cat === activeCategory) return;
    setActiveCategory(cat);
    setExpanded(false);
  };

  const toggleExpanded = () => {
    const next = !expanded;
    if (!next) {
      const section = document.getElementById("features");
      if (section && section.getBoundingClientRect().top < 0) {
        section.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }
    setExpanded(next);
  };

  const filteredFeatures =
    activeCategory === "all"
      ? features
      : features.filter((f) => f.category === activeCategory);

  const visibleFeatures = expanded
    ? filteredFeatures
    : filteredFeatures.slice(0, COLLAPSED_COUNT);
  const hiddenCount = filteredFeatures.length - visibleFeatures.length;
  const showToggle = filteredFeatures.length > COLLAPSED_COUNT;

  const panelId =
    activeCategory === "all"
      ? "features-panel-all"
      : `features-panel-${activeCategory}`;

  return (
    <Section id="features" className="relative border-t border-white/5">
      <SectionIntro
        index="03"
        label="FEATURES"
        title={
          <>
            {featureCount} commands.{" "}
            <span className="text-neon-red">One menu.</span>
          </>
        }
        subtitle="Every capability from the README, indexed like the interactive menu — filter by category or browse the full list."
      />

      <div
        className="flex flex-wrap gap-2 mb-8"
        role="tablist"
        aria-label="Feature categories"
      >
        <TabButton
          active={activeCategory === "all"}
          onClick={() => selectCategory("all")}
          id="features-tab-all"
          controls="features-panel-all"
        >
          ALL
          <Count>{featureCount}</Count>
        </TabButton>
        {featureCategories.map((category) => {
          const isActive = activeCategory === category.id;
          return (
            <TabButton
              key={category.id}
              active={isActive}
              onClick={() =>
                selectCategory(category.id as FeatureCategoryFilter)
              }
              id={`features-tab-${category.id}`}
              controls={`features-panel-${category.id}`}
            >
              {category.label.split(" ")[0].toUpperCase()}
              <Count>{category.count}</Count>
            </TabButton>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeCategory}
          id={panelId}
          role="tabpanel"
          aria-labelledby={
            activeCategory === "all"
              ? "features-tab-all"
              : `features-tab-${activeCategory}`
          }
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.25 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-2 sm:gap-3"
        >
          {visibleFeatures.map((feature, index) => (
            <FeatureRow key={feature.id} feature={feature} index={index} />
          ))}
        </motion.div>
      </AnimatePresence>

      {showToggle && (
        <div className="mt-6 flex justify-center">
          <button
            type="button"
            aria-expanded={expanded}
            aria-controls={panelId}
            onClick={toggleExpanded}
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2 font-mono text-[10px] uppercase tracking-widest border transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neon-cyan",
              "border-white/15 text-muted-foreground hover:text-white hover:border-white/30",
            )}
          >
            {expanded ? "See less" : `See more (${hiddenCount})`}
            <ChevronDown
              className={cn(
                "h-3.5 w-3.5 transition-transform",
                expanded && "rotate-180",
              )}
              aria-hidden="true"
            />
          </button>
        </div>
      )}

      <div className="mt-10">
        <a
          href="https://github.com/AzeemIdrisi/PhoneSploit-Pro#features"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-neon-cyan hover:text-white transition-colors"
        >
          Full feature table in README
          <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
        </a>
      </div>
    </Section>
  );
}

function TabButton({
  active,
  onClick,
  id,
  controls,
  children,
}: {
  active: boolean;
  onClick: () => void;
  id: string;
  controls: string;
  children: React.ReactNode;
}) {
  return (
    <button
      role="tab"
      aria-selected={active}
      aria-controls={controls}
      id={id}
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-2 px-3 py-2 font-mono text-[10px] uppercase tracking-widest border transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neon-cyan",
        active
          ? "border-neon-red/50 text-white bg-neon-red/10"
          : "border-white/15 text-muted-foreground hover:text-white hover:border-white/30",
      )}
    >
      {children}
    </button>
  );
}

function Count({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-muted text-[9px] border border-white/10 px-1.5 py-0.5">
      {children}
    </span>
  );
}
