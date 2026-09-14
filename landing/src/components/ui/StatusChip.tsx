import { cn } from "@/lib/utils";

type StatusChipProps = React.HTMLAttributes<HTMLSpanElement> & {
  live?: boolean;
  variant?: "default" | "red" | "cyan" | "lime" | "amber";
};

export function StatusChip({
  className,
  live = false,
  variant = "default",
  children,
  ...props
}: StatusChipProps) {
  const variants = {
    default: "border-white/20 text-muted-foreground bg-white/5",
    red: "border-neon-red/40 text-neon-red bg-neon-red/5",
    cyan: "border-neon-cyan/40 text-neon-cyan bg-neon-cyan/5",
    lime: "border-neon-lime/40 text-neon-lime bg-neon-lime/5",
    amber: "border-amber/40 text-amber bg-amber/5",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 border px-3 py-1 text-[10px] font-mono uppercase tracking-[0.2em]",
        variants[variant],
        className,
      )}
      {...props}
    >
      {live && (
          <span className="block w-2 h-2 bg-neon-red animate-pulse shrink-0" />
      )}
      {children}
    </span>
  );
}
