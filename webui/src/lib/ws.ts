import { wsUrl } from "@/lib/utils";

const RETRY_DELAYS = [500, 1000, 2000, 4000, 8000];

export type SocketHandlers = {
  onopen?: (event: Event, socket: WebSocket) => void;
  onmessage?: (event: MessageEvent, socket: WebSocket) => void;
  onerror?: (event: Event, socket: WebSocket) => void;
  onclose?: (event: CloseEvent, socket: WebSocket) => void;
};

export function connectSocket(
  path: string,
  handlers: SocketHandlers,
  options?: { binary?: boolean },
): () => void {
  if (typeof WebSocket === "undefined") return () => {};

  let disposed = false;
  let socket: WebSocket | null = null;
  let timer: ReturnType<typeof setTimeout> | null = null;
  let attempt = 0;

  const open = () => {
    if (disposed) return;
    const current = new WebSocket(wsUrl(path));
    socket = current;
    if (options?.binary) current.binaryType = "arraybuffer";

    current.onopen = (event) => {
      if (disposed || current !== socket) return;
      attempt = 0;
      if (options?.binary) current.binaryType = "arraybuffer";
      handlers.onopen?.(event, current);
    };
    current.onmessage = (event) => {
      if (disposed || current !== socket) return;
      handlers.onmessage?.(event, current);
    };
    current.onerror = (event) => {
      if (disposed || current !== socket) return;
      handlers.onerror?.(event, current);
    };
    current.onclose = (event) => {
      if (current !== socket) return;
      if (!disposed) handlers.onclose?.(event, current);
      if (disposed) return;
      const delay = RETRY_DELAYS[Math.min(attempt, RETRY_DELAYS.length - 1)];
      attempt += 1;
      if (timer) clearTimeout(timer);
      timer = setTimeout(open, delay);
    };
  };

  open();

  return () => {
    disposed = true;
    if (timer) clearTimeout(timer);
    timer = null;
    socket?.close();
  };
}
