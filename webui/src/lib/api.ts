import type { ActionResult, Catalog, Device, Health, Job } from "@/lib/types";
import { apiUrl } from "@/lib/utils";

async function parse<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail =
      typeof body.detail === "string" ? body.detail : response.statusText;
    throw new Error(detail || "Request failed");
  }
  return body as T;
}

export function getHealth() {
  return fetch(apiUrl("/api/health")).then((response) =>
    parse<Health>(response),
  );
}

export function getCatalog() {
  return fetch(apiUrl("/api/catalog")).then((response) =>
    parse<Catalog>(response),
  );
}

export function getDevices() {
  return fetch(apiUrl("/api/devices")).then((response) =>
    parse<{ ok: boolean; data: { devices: Device[] } }>(response),
  );
}

export function getJobs() {
  return fetch(apiUrl("/api/jobs")).then((response) =>
    parse<{ jobs: Job[] }>(response),
  );
}

export function getSessions() {
  return fetch(apiUrl("/api/sessions")).then((response) =>
    parse<{
      sessions: {
        id: string;
        feature: string;
        serial: string;
        running: boolean;
        artifact?: string;
      }[];
    }>(response),
  );
}

export function runAction(
  featureId: string,
  serial: string,
  scope: "host" | "device",
  params: Record<string, string>,
) {
  const path =
    scope === "host"
      ? `/api/actions/${featureId}`
      : `/api/devices/${encodeURIComponent(serial)}/actions/${featureId}`;
  return fetch(apiUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ params }),
  }).then((response) => parse<ActionResult>(response));
}

export function getJson<T>(path: string) {
  return fetch(apiUrl(path)).then((response) => parse<T>(response));
}

export function upload(
  serial: string,
  purpose: string,
  files: File[],
  destination = "",
) {
  const body = new FormData();
  body.set("purpose", purpose);
  body.set("destination", destination);
  for (const file of files) body.append("files", file);
  return fetch(apiUrl(`/api/devices/${encodeURIComponent(serial)}/upload`), {
    method: "POST",
    body,
  }).then((response) => parse<ActionResult>(response));
}

export function startSession(
  serial: string,
  feature: string,
  params: Record<string, string>,
) {
  const query = new URLSearchParams({ serial });
  return fetch(apiUrl(`/api/sessions?${query}`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ feature, params }),
  }).then((response) =>
    parse<{ ok: boolean; session: string; artifact?: string }>(response),
  );
}

export function stopSession(id: string) {
  return fetch(apiUrl(`/api/sessions/${id}`), { method: "DELETE" }).then(
    (response) => parse<{ ok: boolean }>(response),
  );
}

export function cancelJob(id: string) {
  return fetch(apiUrl(`/api/jobs/${encodeURIComponent(id)}/cancel`), {
    method: "POST",
  }).then((response) => parse<{ ok: boolean }>(response));
}
