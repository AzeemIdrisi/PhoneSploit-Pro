"use client";

import { repoInfo } from "@/data/constants";

/** Labels match MenuItem.display_label in modules/menu.py MAIN_ITEMS. */
const MENU_ITEMS = [
  "Device Connection ›",
  "ADB & Wireless Debugging ›",
  "Launch Metasploit Attack",
  "Mirror & Control Device",
  "Camera Live Stream",
  "Access Device Shell",
  "Screen Capture ›",
  "Microphone & Device Audio ›",
  "Open URL & Media on Device ›",
  "File Transfer ›",
  "Copy Media Files ›",
  "Messages, Calls & Contacts ›",
  "Notifications ›",
  "Power, Reboot & Lock ›",
  "Clipboard Control ›",
  "App Management ›",
  "App State Control ›",
  "Device Information ›",
  "Get Device Location",
  "Battery Info & Mocking ›",
  "Display Resolution & Size ›",
  "Brightness Controls ›",
  "Sound Controls ›",
  "Wi-Fi Tools ›",
  "Wi-Fi Hotspot ›",
  "Radio Toggles ›",
  "Network Diagnostics ›",
  "Send Keycode Inputs ›",
  "Device Diagnostics ›",
  "Vulnerability Analysis ›",
  "Port Forwarding ›",
  "Developer Settings",
  "Set Wallpaper",
  "Launch Web Interface",
] as const;

const NCOLS = 3;

function columnize<T>(items: readonly T[], cols: number): T[][] {
  const n = items.length;
  const perCol = Array(cols).fill(Math.floor(n / cols));
  for (let i = 0; i < n % cols; i++) perCol[i] += 1;
  const columns: T[][] = [];
  let offset = 0;
  for (const size of perCol) {
    columns.push(items.slice(offset, offset + size) as T[]);
    offset += size;
  }
  return columns;
}

function padIndex(n: number) {
  return String(n).padStart(2, " ");
}

const BANNER = `        █▀█ █░█ █▀█ █▄░█ █▀▀ █▀ █▀█ █░░ █▀█ █ ▀█▀   █▀█ █▀█ █▀█
        █▀▀ █▀█ █▄█ █░▀█ ██▄ ▄█ █▀▀ █▄▄ █▄█ █ ░█░   █▀▀ █▀▄ █▄█`;

export default function TerminalPreview() {
  const columns = columnize(MENU_ITEMS, NCOLS);
  let index = 1;

  return (
    <div className="panel corner-ticks overflow-hidden" aria-hidden="true">
      <div className="flex items-center justify-between gap-2 border-b border-white/10 px-3 py-2 bg-black/60">
        <div className="flex items-center gap-2 min-w-0">
          <span className="h-2 w-2 bg-neon-red shrink-0" />
          <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground truncate">
            python3 phonesploitpro.py
          </span>
        </div>
        <span className="font-mono text-[9px] uppercase tracking-widest text-neon-lime shrink-0">
          [ready]
        </span>
      </div>
      <div className="overflow-x-auto bg-black p-3 sm:p-4 font-mono text-[9px] sm:text-[10px] leading-[1.55]">
        <pre className="text-cyan-400 font-bold whitespace-pre mb-3">
          {BANNER}
        </pre>

        <p className="mb-3 whitespace-pre">
          {"            "}
          <span className="font-bold text-red-500">{repoInfo.version}</span>
          {"             "}
          <span className="font-bold text-white">By github.com/AzeemIdrisi</span>
        </p>

        <div className="grid grid-cols-3 gap-x-3 min-w-[36rem]">
          {columns.map((col, colIdx) => (
            <div key={colIdx} className="min-w-0">
              {col.map((label) => {
                const n = index++;
                return (
                  <p key={label} className="whitespace-nowrap overflow-hidden">
                    <span className="font-bold text-white">{padIndex(n)}. </span>
                    <span className="font-bold text-[#22c55e]">{label}</span>
                  </p>
                );
              })}
            </div>
          ))}
        </div>

        <p className="mt-3 text-white/50 font-bold">
          {"  "}
          Ctrl+D Exit{"  "}Ctrl+L Clear{"  "}Ctrl+C Cancel input{"  "}/ Search
        </p>
        <p className="mt-0.5 font-bold text-red-500">
          [Main Menu] &gt;{" "}
          <span className="inline-block w-1.5 h-3 align-middle bg-white animate-terminal-blink" />
        </p>
      </div>
    </div>
  );
}
