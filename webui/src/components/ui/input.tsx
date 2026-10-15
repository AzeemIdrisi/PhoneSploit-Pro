import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Input({
  className,
  ...props
}: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "flex h-9 w-full rounded-md border border-border bg-input px-3 text-sm outline-none placeholder:text-muted-foreground focus:border-accent",
        className,
      )}
      {...props}
    />
  );
}
