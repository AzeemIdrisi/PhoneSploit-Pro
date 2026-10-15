"use client";

import type { ComponentProps, CSSProperties } from "react";
import { Toaster as Sonner } from "sonner";
import { cn } from "@/lib/utils";

export function Toaster({
  className,
  style,
  toastOptions,
  ...props
}: ComponentProps<typeof Sonner>) {
  return (
    <Sonner
      className={cn("toaster group", className)}
      toastOptions={{
        ...toastOptions,
        classNames: {
          toast: "border-border bg-card text-foreground",
          description: "text-muted-foreground",
          actionButton: "bg-primary text-primary-foreground",
          cancelButton: "bg-muted text-muted-foreground",
          ...toastOptions?.classNames,
        },
      }}
      style={
        {
          "--normal-bg": "var(--color-card)",
          "--normal-text": "var(--color-foreground)",
          "--normal-border": "var(--color-border)",
          ...style,
        } as CSSProperties
      }
      {...props}
      theme="dark"
    />
  );
}
