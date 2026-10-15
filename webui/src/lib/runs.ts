import { cancelJob } from "@/lib/api";
import { jobRunStatus, useConsole, type ActiveRun } from "@/lib/store";
import type { ActionResult, Feature, Job } from "@/lib/types";

export type TrackInput = {
  feature: Feature;
  params: Record<string, string>;
  serial: string;
  scope: "host" | "device";
  kind: "action" | "upload" | "session";
  cancelable?: boolean;
  message?: string;
  run: () => Promise<ActionResult>;
  onSettled?: () => void;
};

export function stubFeature(input: {
  id: string;
  label: string;
  scope?: "host" | "device";
  tier?: Feature["tier"];
}): Feature {
  return {
    id: input.id,
    label: input.label,
    hub: null,
    requires: "adb",
    tier: input.tier ?? "native",
    scope: input.scope ?? "device",
    destructive: false,
    fields: [],
  };
}

export function startTracked(input: TrackInput): boolean {
  const started = useConsole.getState().startRun({
    feature: input.feature,
    params: input.params,
    serial: input.serial,
    scope: input.scope,
    kind: input.kind,
    cancelable: input.cancelable,
    message: input.message,
  });
  if (!started) return false;
  const generation = useConsole.getState().runGeneration;
  void settle(generation, input);
  return true;
}

function releaseUnattachedJob(job: Job | undefined) {
  if (!job) return;
  const state = useConsole.getState();
  const run = state.activeRun;
  void cancelJob(job.id).catch(() => undefined);
  if (!run || run.status !== "canceled" || run.jobId) return;
  const latest = state.jobsById[job.id] ?? job;
  useConsole.getState().patchRun(
    {
      jobId: latest.id,
      progress: latest.progress ?? run.progress,
      data: latest.data ?? run.data,
      artifact: latest.artifact ?? run.artifact,
    },
    state.runGeneration,
  );
}

function rememberedJob(
  job: Job,
  run: ActiveRun,
  generation: number,
  fallbackMessage: string,
) {
  const existing = useConsole.getState().jobsById[job.id];
  const latest = existing ?? job;
  if (!existing) useConsole.getState().upsertJob(latest);
  useConsole.getState().patchRun(
    {
      jobId: latest.id,
      message: latest.message || fallbackMessage || run.message,
      progress: latest.progress ?? null,
      data: latest.data ?? run.data,
      artifact: latest.artifact ?? run.artifact,
      status: jobRunStatus(latest.status),
      cancelable: true,
    },
    generation,
  );
}

async function settle(generation: number, input: TrackInput) {
  try {
    const result = await input.run();
    const state = useConsole.getState();
    const run = state.activeRun;
    const detached =
      state.runGeneration !== generation || !run || run.status === "canceled";
    if (detached) {
      releaseUnattachedJob(result.job);
      return;
    }
    if (result.job) {
      rememberedJob(result.job, run, generation, result.message);
      return;
    }
    useConsole.getState().finishRun(result, generation);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Request failed";
    useConsole.getState().failRun(message, generation);
  } finally {
    input.onSettled?.();
  }
}
