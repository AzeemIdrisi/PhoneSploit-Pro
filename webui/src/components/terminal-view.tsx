"use client";

import { FitAddon } from "@xterm/addon-fit";
import { Terminal } from "@xterm/xterm";
import { useEffect, useRef } from "react";
import "@xterm/xterm/css/xterm.css";
import { connectSocket } from "@/lib/ws";

export function TerminalView({
  mode,
  serial,
}: {
  mode: "shell" | "metasploit";
  serial: string;
}) {
  const hostRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const term = new Terminal({
      cursorBlink: true,
      fontFamily: "var(--font-geist-mono), ui-monospace, monospace",
      fontSize: 13,
      theme: {
        background: "#050505",
        foreground: "#d6d6d6",
        cursor: "#00ff41",
      },
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    if (hostRef.current) term.open(hostRef.current);
    fit.fit();
    const query = new URLSearchParams({ mode, serial });
    let active: WebSocket | null = null;
    const stop = connectSocket(`/ws/pty?${query}`, {
      onopen: (_event, socket) => {
        active = socket;
      },
      onmessage: (event) => {
        if (typeof event.data === "string") term.write(event.data);
      },
      onclose: () => {
        term.write("\r\n[reconnecting]\r\n");
      },
    });
    const disposable = term.onData((data) => {
      if (active && active.readyState === WebSocket.OPEN) active.send(data);
    });
    const onResize = () => fit.fit();
    window.addEventListener("resize", onResize);
    return () => {
      disposable.dispose();
      stop();
      window.removeEventListener("resize", onResize);
      term.dispose();
    };
  }, [mode, serial]);

  return (
    <div
      ref={hostRef}
      className="h-[480px] overflow-hidden rounded-lg border border-border bg-black p-2"
    />
  );
}
