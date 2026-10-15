"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { connectSocket } from "@/lib/ws";

const KEYS = [
  { label: "Home", code: "3" },
  { label: "Back", code: "4" },
  { label: "Recent", code: "187" },
  { label: "Power", code: "26" },
  { label: "Vol +", code: "24" },
  { label: "Vol −", code: "25" },
];

export function ScreenView({ serial }: { serial: string }) {
  const imgRef = useRef<HTMLImageElement>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const drag = useRef<{ x: number; y: number } | null>(null);
  const [status, setStatus] = useState("Connecting…");
  const [text, setText] = useState("");

  useEffect(() => {
    const dispose = connectSocket(
      `/ws/devices/${encodeURIComponent(serial)}/screen`,
      {
        onopen: (_event, socket) => {
          socketRef.current = socket;
          setStatus("Live");
        },
        onclose: () => setStatus("Reconnecting…"),
        onmessage: (event) => {
          if (typeof event.data === "string") return;
          const blob = new Blob([event.data], { type: "image/png" });
          const url = URL.createObjectURL(blob);
          const image = imgRef.current;
          if (!image) return;
          const previous = image.src;
          image.src = url;
          if (previous.startsWith("blob:")) URL.revokeObjectURL(previous);
        },
      },
      { binary: true },
    );
    return () => {
      dispose();
      socketRef.current = null;
      const image = imgRef.current;
      if (image?.src.startsWith("blob:")) URL.revokeObjectURL(image.src);
    };
  }, [serial]);

  function point(event: React.PointerEvent<HTMLImageElement>) {
    const image = imgRef.current;
    if (!image?.naturalWidth) return null;
    const rect = image.getBoundingClientRect();
    const x = Math.round(
      ((event.clientX - rect.left) / rect.width) * image.naturalWidth,
    );
    const y = Math.round(
      ((event.clientY - rect.top) / rect.height) * image.naturalHeight,
    );
    return { x, y };
  }

  function send(payload: object) {
    const socket = socketRef.current;
    if (socket && socket.readyState === WebSocket.OPEN)
      socket.send(JSON.stringify(payload));
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,420px)_1fr]">
      <div className="overflow-hidden rounded-lg border border-border bg-black glow-cyan">
        <img
          ref={imgRef}
          alt="Device screen"
          className="mx-auto max-h-[72vh] w-full object-contain"
          onPointerDown={(event) => {
            drag.current = point(event);
          }}
          onPointerUp={(event) => {
            const start = drag.current;
            const end = point(event);
            drag.current = null;
            if (!start || !end) return;
            const moved = Math.hypot(end.x - start.x, end.y - start.y);
            if (moved < 12) send({ type: "tap", x: end.x, y: end.y });
            else
              send({
                type: "swipe",
                x1: start.x,
                y1: start.y,
                x2: end.x,
                y2: end.y,
              });
          }}
        />
      </div>
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          {status}. Click to tap, drag to swipe. Frames come from{" "}
          <span className="text-foreground">adb screencap</span>.
        </p>
        <div className="flex flex-wrap gap-2">
          {KEYS.map((key) => (
            <Button
              key={key.code}
              variant="outline"
              size="sm"
              onClick={() => send({ type: "key", code: key.code })}
            >
              {key.label}
            </Button>
          ))}
        </div>
        <form
          className="flex gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            if (!text.trim()) return;
            send({ type: "text", text });
            setText("");
          }}
        >
          <Input
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Type on device"
          />
          <Button type="submit" variant="secondary">
            Send
          </Button>
        </form>
      </div>
    </div>
  );
}
