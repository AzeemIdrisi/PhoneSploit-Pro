import { Cpu, Terminal, Shield, Radio, LayoutList } from "lucide-react";
import { toolStripItems } from "@/data/constants";
import { featureCount } from "@/data/features";

const icons = [Terminal, LayoutList, Radio, Shield, Cpu];

export default function ToolStrip() {
  const items = [...toolStripItems, `${featureCount} FEATURES`];

  return (
    <ul className="flex flex-wrap items-center justify-start gap-x-8 gap-y-3">
        {items.map((item, i) => {
          const Icon = icons[i] ?? Terminal;
          return (
            <li
              key={item}
              className="flex items-center gap-2 font-mono text-[10px] sm:text-xs uppercase tracking-[0.2em] text-neon-cyan"
            >
              <Icon className="h-3.5 w-3.5" aria-hidden />
              {item}
            </li>
          );
        })}
      </ul>
  );
}
