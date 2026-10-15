import { cn } from "@/lib/utils";

type ProgressProps = {
  value?: number;
  className?: string;
  label?: string;
};

export function Progress({ value = 0, className, label }: ProgressProps) {
  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemax={100}
      aria-valuemin={0}
      aria-valuenow={clamped}
      className={cn(
        "h-1.5 w-full overflow-hidden rounded-full bg-muted",
        className,
      )}
    >
      <div
        className="h-full rounded-full bg-accent transition-[width] duration-300 ease-out"
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}
