import { toast } from "sonner";
import { create } from "zustand";
import type { ActionResult, Feature, Job } from "@/lib/types";

export type RunStatus = "running" | "done" | "error" | "canceled";

export type ActiveRun = {
  feature: Feature;
  params: Record<string, string>;
  serial: string;
  scope: "host" | "device";
  kind: "action" | "upload" | "session";
  status: RunStatus;
  jobId: string | null;
  message: string;
  progress: number | null;
  data: unknown;
  artifact?: string | null;
  cancelable: boolean;
};

export type RunInput = {
  feature: Feature;
  params: Record<string, string>;
  serial: string;
  scope: "host" | "device";
  kind: "action" | "upload" | "session";
  cancelable?: boolean;
  message?: string;
};

type ConsoleState = {
  paletteOpen: boolean;
  activityOpen: boolean;
  sidebarOpen: boolean;
  notice: string | null;
  activeRun: ActiveRun | null;
  jobsById: Record<string, Job>;
  runGeneration: number;
  setPaletteOpen: (open: boolean) => void;
  setActivityOpen: (open: boolean) => void;
  setSidebarOpen: (open: boolean) => void;
  flash: (message: string) => void;
  startRun: (input: RunInput) => boolean;
  patchRun: (partial: Partial<ActiveRun>, generation?: number) => void;
  upsertJob: (job: Job) => void;
  applyJob: (job: Job) => void;
  finishRun: (result: ActionResult, generation?: number) => void;
  failRun: (message: string, generation?: number) => void;
  cancelRun: () => void;
  markCanceled: () => void;
  closeRun: () => void;
};

export function jobRunStatus(status: string): RunStatus {
  if (status === "done" || status === "error" || status === "canceled") {
    return status;
  }
  return "running";
}

function currentGeneration(
  state: ConsoleState,
  generation: number | undefined,
) {
  return generation === undefined || state.runGeneration === generation;
}

export const useConsole = create<ConsoleState>((set, get) => ({
  paletteOpen: false,
  activityOpen: false,
  sidebarOpen: true,
  notice: null,
  activeRun: null,
  jobsById: {},
  runGeneration: 0,
  setPaletteOpen: (paletteOpen) => set({ paletteOpen }),
  setActivityOpen: (activityOpen) => set({ activityOpen }),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  flash: (message) => {
    set({ notice: message });
    toast(message, { duration: 4200 });
    window.setTimeout(() => set({ notice: null }), 4200);
  },
  startRun: (input) => {
    if (get().activeRun?.status === "running") {
      toast("An action is already running.");
      return false;
    }
    const runGeneration = get().runGeneration + 1;
    set({
      runGeneration,
      activeRun: {
        feature: input.feature,
        params: input.params,
        serial: input.serial,
        scope: input.scope,
        kind: input.kind,
        status: "running",
        jobId: null,
        message: input.message ?? "Running…",
        progress: null,
        data: null,
        artifact: null,
        cancelable: input.cancelable ?? true,
      },
    });
    return true;
  },
  patchRun: (partial, generation) => {
    set((state) => {
      if (!currentGeneration(state, generation) || !state.activeRun)
        return state;
      return { activeRun: { ...state.activeRun, ...partial } };
    });
  },
  upsertJob: (job) => {
    set((state) => ({ jobsById: { ...state.jobsById, [job.id]: job } }));
  },
  applyJob: (job) => {
    set((state) => {
      const jobsById = { ...state.jobsById, [job.id]: job };
      const run = state.activeRun;
      if (!run || run.jobId !== job.id) return { jobsById };
      if (run.status === "canceled") {
        return {
          jobsById,
          activeRun: {
            ...run,
            progress:
              job.progress === undefined
                ? (run.progress ?? null)
                : job.progress,
            data: job.data === undefined ? run.data : job.data,
            artifact: job.artifact === undefined ? run.artifact : job.artifact,
          },
        };
      }
      return {
        jobsById,
        activeRun: {
          ...run,
          status: jobRunStatus(job.status),
          message: job.message || run.message,
          progress:
            job.progress === undefined ? (run.progress ?? null) : job.progress,
          data: job.data === undefined ? run.data : job.data,
          artifact: job.artifact === undefined ? run.artifact : job.artifact,
        },
      };
    });
  },
  finishRun: (result, generation) => {
    set((state) => {
      if (!currentGeneration(state, generation)) return state;
      const run = state.activeRun;
      if (!run || run.status === "canceled") return state;
      return {
        activeRun: {
          ...run,
          status: result.ok ? "done" : "error",
          message: result.message || run.feature.label,
          data: result.data ?? null,
          artifact: result.artifact ?? null,
          jobId: null,
        },
      };
    });
  },
  failRun: (message, generation) => {
    set((state) => {
      if (!currentGeneration(state, generation)) return state;
      const run = state.activeRun;
      if (!run || run.status === "canceled") return state;
      return { activeRun: { ...run, status: "error", message } };
    });
  },
  cancelRun: () => {
    set((state) => {
      const run = state.activeRun;
      if (!run) return state;
      if (run.status !== "running") return state;
      return {
        runGeneration: state.runGeneration + 1,
        activeRun: { ...run, status: "canceled", message: "Canceled" },
      };
    });
  },
  markCanceled: () => {
    get().cancelRun();
  },
  closeRun: () => {
    const run = get().activeRun;
    if (!run || run.status === "running") return;
    set({ activeRun: null });
  },
}));
