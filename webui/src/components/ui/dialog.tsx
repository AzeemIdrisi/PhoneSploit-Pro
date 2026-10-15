"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogClose = DialogPrimitive.Close;

export function DialogContent({
  className,
  children,
  showClose = true,
  passiveOverlay = false,
  ...props
}: ComponentProps<typeof DialogPrimitive.Content> & {
  showClose?: boolean;
  passiveOverlay?: boolean;
}) {
  return (
    <DialogPrimitive.Portal>
      {passiveOverlay ? (
        <div className="pointer-events-none fixed inset-0 z-50 bg-black/70 backdrop-blur-sm" />
      ) : (
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm" />
      )}
      <DialogPrimitive.Content
        className={cn(
          "fixed top-1/2 left-1/2 z-50 w-[min(560px,calc(100%-2rem))] -translate-x-1/2 -translate-y-1/2 rounded-lg border border-border bg-[#090909] p-5 shadow-2xl",
          className,
        )}
        {...props}
      >
        {children}
        {showClose ? (
          <DialogPrimitive.Close
            aria-label="Close"
            className="absolute top-3 right-3 rounded-md p-1 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </DialogPrimitive.Close>
        ) : null}
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

export function DialogTitle({
  className,
  ...props
}: ComponentProps<typeof DialogPrimitive.Title>) {
  return (
    <DialogPrimitive.Title
      className={cn("font-display text-lg", className)}
      {...props}
    />
  );
}

export function DialogDescription({
  className,
  ...props
}: ComponentProps<typeof DialogPrimitive.Description>) {
  return (
    <DialogPrimitive.Description
      className={cn("mt-1 text-sm text-muted-foreground", className)}
      {...props}
    />
  );
}
