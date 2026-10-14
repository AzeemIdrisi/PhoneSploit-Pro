"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";

type CommandBoxProps = {
  command: string;
  prompt?: string;
  className?: string;
  multiline?: boolean;
};

export function CommandBox({
  command,
  prompt = "root@psp:~#",
  className,
  multiline = false,
}: CommandBoxProps) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={copied ? "Command copied" : `Copy command: ${command}`}
      onClick={copy}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          copy();
        }
      }}
      className={cn(
        "panel corner-ticks cursor-copy group flex items-center justify-between gap-6 px-6 py-4 font-mono text-sm",
        className,
      )}
    >
      <div className="flex-1 min-w-0 overflow-x-auto">
        <span className="text-term-green/70">{prompt} </span>
        <code
          className={cn(
            "text-term-green break-all",
            multiline && "whitespace-pre-wrap block mt-1",
          )}
        >
          {command}
        </code>
      </div>
      <span className="text-xs text-neon-red group-hover:text-neon-lime transition-colors hidden sm:block shrink-0 tracking-widest">
        {copied ? "[OK]" : "[COPY]"}
      </span>
    </div>
  );
}

type CommandListProps = {
  commands: string[];
  copiedCommand: string | null;
  onCopy: (cmd: string) => void;
  startIndex?: number;
  className?: string;
};

export function CommandList({
  commands,
  copiedCommand,
  onCopy,
  startIndex = 0,
  className,
}: CommandListProps) {
  return (
    <div className={cn("panel border-white/15 divide-y divide-white/10", className)}>
      {commands.map((cmd, i) => (
        <div
          key={`${startIndex}-${i}`}
          className="flex items-start gap-3 p-3 font-mono text-xs sm:text-sm group cursor-copy"
          onClick={() => onCopy(cmd)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              onCopy(cmd);
            }
          }}
          role="button"
          tabIndex={0}
          aria-label={copiedCommand === cmd ? "Command copied" : `Copy command: ${cmd}`}
        >
          <span className="text-muted shrink-0 mt-0.5 w-6">
            {String(startIndex + i + 1).padStart(2, "0")}
          </span>
          <code className="text-foreground/90 flex-1 break-all whitespace-pre-wrap">
            {cmd}
          </code>
          <span className="text-[10px] tracking-widest text-neon-red group-hover:text-neon-lime shrink-0">
            {copiedCommand === cmd ? "[OK]" : "[COPY]"}
          </span>
        </div>
      ))}
    </div>
  );
}
