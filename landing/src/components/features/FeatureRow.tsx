"use client";

import { motion } from "framer-motion";
import { Feature, featureCategories } from "@/data/features";
import { cn } from "@/lib/utils";

interface FeatureRowProps {
  feature: Feature;
  index: number;
}

const categoryLabels = Object.fromEntries(
  featureCategories.map((c) => [c.id, c.label]),
) as Record<string, string>;

export function FeatureRow({ feature, index }: FeatureRowProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: Math.min(index, 12) * 0.02, duration: 0.3 }}
      className={cn(
        "panel panel-hover flex gap-3 sm:gap-4 p-3 sm:p-4 items-start border-white/10",
      )}
    >
      <span className="font-mono text-[10px] text-neon-red shrink-0 w-8 pt-0.5">
        {String(index + 1).padStart(2, "0")}
      </span>
      <div className="flex-1 min-w-0">
        <h3 className="font-mono text-xs sm:text-sm text-white uppercase tracking-wide">
          {feature.name}
        </h3>
        <p className="mt-1 text-xs text-muted-foreground font-mono line-clamp-2">
          {feature.description}
        </p>
      </div>
      <span className="hidden sm:inline font-mono text-[9px] uppercase tracking-widest text-neon-cyan shrink-0 max-w-[7rem] text-right">
        {categoryLabels[feature.category]?.split(" ")[0] ?? feature.category}
      </span>
    </motion.div>
  );
}
