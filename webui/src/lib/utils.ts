import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export function apiUrl(path: string) {
  return `${API_BASE}${path}`;
}

export function wsUrl(path: string) {
  if (API_BASE) {
    const url = new URL(API_BASE);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    return `${url.origin}${path}`;
  }
  if (typeof window === "undefined") return path;
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}${path}`;
}

export function artifactUrl(path: string) {
  return apiUrl(`/api/artifacts?path=${encodeURIComponent(path)}`);
}

export function openDevice(serial: string) {
  window.location.hash = `/device/${encodeURIComponent(serial)}`;
}

export function openHome() {
  window.location.hash = "/";
}
