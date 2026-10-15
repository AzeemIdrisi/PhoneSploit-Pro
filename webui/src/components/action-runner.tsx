"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { cancelJob, runAction } from "@/lib/api";
import { startTracked, stubFeature } from "@/lib/runs";
import { useConsole } from "@/lib/store";
import type { Catalog, Feature } from "@/lib/types";
import { artifactUrl } from "@/lib/utils";

const STATUS_LABEL = {
  running: "Running",
  done: "Done",
  error: "Error",
  canceled: "Canceled",
} as const;

const PREVIEW_LIMIT = 4000;

function hasHosts(data: unknown) {
  return (
    !!data &&
    typeof data === "object" &&
    !Array.isArray(data) &&
    Array.isArray((data as { hosts?: unknown }).hosts)
  );
}

type ScanHost = { ip: string; adb: unknown; hint: unknown };

function scanHosts(data: unknown): ScanHost[] | null {
  if (!hasHosts(data)) return null;
  return (data as { hosts: unknown[] }).hosts.flatMap((host) => {
    if (!host || typeof host !== "object") return [];
    const row = host as Record<string, unknown>;
    if (typeof row.ip !== "string" || !row.ip) return [];
    return [{ ip: row.ip, adb: row.adb, hint: row.hint }];
  });
}

function formatCell(value: unknown) {
  if (value == null || value === "") return "—";
  if (typeof value === "string" || typeof value === "number")
    return String(value);
  if (typeof value === "boolean") return value ? "yes" : "no";
  try {
    return JSON.stringify(value);
  } catch {
    return "—";
  }
}

function subnetOf(data: unknown) {
  if (!data || typeof data !== "object" || Array.isArray(data)) return null;
  const subnet = (data as { subnet?: unknown }).subnet;
  return typeof subnet === "string" && subnet ? subnet : null;
}

function isShortPrimitive(value: unknown) {
  if (
    value == null ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return true;
  }
  return typeof value === "string" && value.length <= 160;
}

function PreBlock({ text }: { text: string }) {
  const clipped =
    text.length > PREVIEW_LIMIT ? `${text.slice(0, PREVIEW_LIMIT)}…` : text;
  return (
    <pre className="max-h-40 overflow-auto rounded-md border border-border bg-black p-3 text-xs text-muted-foreground">
      {clipped}
    </pre>
  );
}

function DataPreview({ data }: { data: unknown }) {
  if (data == null || hasHosts(data)) return null;
  if (typeof data !== "object") return <PreBlock text={String(data)} />;
  if (Array.isArray(data))
    return <PreBlock text={JSON.stringify(data, null, 2)} />;
  const entries = Object.entries(data as Record<string, unknown>).filter(
    ([key]) => key !== "hosts",
  );
  if (entries.length === 0) return null;
  if (entries.every(([, value]) => isShortPrimitive(value))) {
    return (
      <dl className="space-y-1 text-sm">
        {entries.map(([key, value]) => (
          <div key={key} className="flex justify-between gap-4">
            <dt className="text-muted-foreground">{key}</dt>
            <dd className="max-w-[60%] truncate text-right">
              {value == null || value === "" ? "—" : String(value)}
            </dd>
          </div>
        ))}
      </dl>
    );
  }
  return <PreBlock text={JSON.stringify(data, null, 2)} />;
}

function HostTable({
  hosts,
  subnet,
  scanRunning,
  onConnect,
}: {
  hosts: ScanHost[];
  subnet: string | null;
  scanRunning: boolean;
  onConnect: (ip: string) => void;
}) {
  return (
    <div className="space-y-2">
      {subnet ? (
        <p className="text-xs text-muted-foreground">Subnet {subnet}</p>
      ) : null}
      <div className="max-h-64 overflow-auto rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <caption className="sr-only">Discovered hosts</caption>
          <thead className="sticky top-0 bg-card text-xs tracking-wide text-muted-foreground uppercase">
            <tr>
              <th className="px-3 py-2 font-medium" scope="col">
                IP
              </th>
              <th className="px-3 py-2 font-medium" scope="col">
                ADB
              </th>
              <th className="px-3 py-2 font-medium" scope="col">
                Android hint
              </th>
              <th className="px-3 py-2 font-medium" scope="col">
                <span className="sr-only">Connect</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {hosts.length === 0 ? (
              <tr>
                <td className="px-3 py-4 text-muted-foreground" colSpan={4}>
                  No hosts yet.
                </td>
              </tr>
            ) : (
              hosts.map((host) => (
                <tr key={host.ip} className="border-t border-border">
                  <td className="px-3 py-2 font-mono">{host.ip}</td>
                  <td className="px-3 py-2">{formatCell(host.adb)}</td>
                  <td className="px-3 py-2">{formatCell(host.hint)}</td>
                  <td className="px-3 py-2 text-right">
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      aria-disabled={scanRunning}
                      title={
                        scanRunning ? "Wait for the scan to finish" : undefined
                      }
                      className={scanRunning ? "opacity-40" : undefined}
                      onClick={() => onConnect(host.ip)}
                    >
                      Connect
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function ActionRunner() {
  const activeRun = useConsole((state) => state.activeRun);
  const runGeneration = useConsole((state) => state.runGeneration);
  const closeRun = useConsole((state) => state.closeRun);
  const cancelRun = useConsole((state) => state.cancelRun);
  const queryClient = useQueryClient();
  const toasted = useRef<string | null>(null);
  const [canceling, setCanceling] = useState(false);

  useEffect(() => {
    if (!activeRun || activeRun.status === "running") return;
    const key = `${runGeneration}:${activeRun.status}`;
    if (toasted.current === key) return;
    toasted.current = key;
    if (activeRun.status === "done") {
      toast.success(activeRun.message || activeRun.feature.label);
    } else if (activeRun.status === "error") {
      toast.error(activeRun.message || "Action failed");
    } else {
      toast(activeRun.message || "Canceled");
    }
  }, [activeRun, runGeneration]);

  useEffect(() => {
    if (!activeRun) return;
    if (activeRun.status !== "done") return;
    if (activeRun.jobId || activeRun.artifact || hasHosts(activeRun.data))
      return;
    const generation = runGeneration;
    const timer = window.setTimeout(() => {
      const state = useConsole.getState();
      if (state.runGeneration !== generation) return;
      if (state.activeRun?.status !== "done") return;
      state.closeRun();
    }, 900);
    return () => window.clearTimeout(timer);
  }, [activeRun, runGeneration]);

  useEffect(() => {
    setCanceling(false);
  }, [runGeneration]);

  const running = activeRun?.status === "running";
  const hosts = activeRun ? scanHosts(activeRun.data) : null;
  const progress =
    activeRun &&
    running &&
    typeof activeRun.progress === "number" &&
    Number.isFinite(activeRun.progress)
      ? activeRun.progress
      : null;

  async function handleCancel() {
    const run = useConsole.getState().activeRun;
    if (canceling || !run) return;
    if (run.status !== "running") return;
    setCanceling(true);
    if (run.jobId && run.cancelable) {
      try {
        await cancelJob(run.jobId);
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Could not cancel",
        );
      }
    }
    cancelRun();
  }

  function connectHost(ip: string) {
    if (useConsole.getState().activeRun?.status === "running") {
      toast("Wait for the scan to finish");
      return;
    }
    const catalog = queryClient.getQueryData<Catalog>(["catalog"]);
    const match = catalog?.features.find((item) => item.id === "connect");
    const feature: Feature = match
      ? { ...match, scope: "host" }
      : stubFeature({ id: "connect", label: "Connect", scope: "host" });
    startTracked({
      feature,
      params: { ip },
      serial: "",
      scope: "host",
      kind: "action",
      run: () => runAction("connect", "", "host", { ip }),
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["devices"] });
        queryClient.invalidateQueries({ queryKey: ["jobs"] });
      },
    });
  }

  return (
    <Dialog
      open={activeRun != null}
      modal={activeRun?.status !== "running"}
      onOpenChange={(open) => {
        if (!open) closeRun();
      }}
    >
      {activeRun ? (
        <DialogContent
          passiveOverlay={activeRun.status === "running"}
          showClose={activeRun.status !== "running"}
          className="max-h-[85vh] w-[min(720px,calc(100%-2rem))] overflow-y-auto"
          onPointerDownOutside={(event) => {
            if (activeRun.status === "running") event.preventDefault();
          }}
          onEscapeKeyDown={(event) => {
            if (activeRun.status === "running") event.preventDefault();
          }}
        >
          <DialogTitle>{activeRun.feature.label}</DialogTitle>
          <DialogDescription>
            {STATUS_LABEL[activeRun.status]}
          </DialogDescription>
          <div className="mt-4 space-y-3">
            {activeRun.status === "error" ? (
              <p
                role="alert"
                className="rounded-md border border-primary/40 bg-primary/10 px-3 py-2 text-sm text-primary"
              >
                {activeRun.message || "The action failed."}
              </p>
            ) : (
              <p role="status" className="text-sm text-muted-foreground">
                {activeRun.message || STATUS_LABEL[activeRun.status]}
              </p>
            )}
            {progress != null ? (
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Progress</span>
                  <span>{Math.round(progress * 100)}%</span>
                </div>
                <Progress
                  value={progress * 100}
                  label={activeRun.feature.label}
                />
              </div>
            ) : null}
            {hosts ? (
              <HostTable
                hosts={hosts}
                subnet={subnetOf(activeRun.data)}
                scanRunning={activeRun.status === "running"}
                onConnect={connectHost}
              />
            ) : null}
            <DataPreview data={activeRun.data} />
            {activeRun.artifact ? (
              <a
                className="inline-block text-sm text-accent"
                href={artifactUrl(activeRun.artifact)}
              >
                Download artifact
              </a>
            ) : null}
            <div className="flex justify-end gap-2">
              {activeRun.status === "running" ? (
                <Button
                  type="button"
                  variant="danger"
                  disabled={canceling}
                  onClick={() => void handleCancel()}
                >
                  {canceling ? "Canceling…" : "Cancel"}
                </Button>
              ) : (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => closeRun()}
                >
                  Close
                </Button>
              )}
            </div>
          </div>
        </DialogContent>
      ) : null}
    </Dialog>
  );
}
