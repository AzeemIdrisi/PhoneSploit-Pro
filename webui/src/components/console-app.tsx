"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Activity,
  Battery,
  ChevronLeft,
  Radio,
  Search,
  Wifi,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { ActionRunner } from "@/components/action-runner";
import { ScreenView } from "@/components/screen-view";
import { DEVICE_TABS, Sidebar } from "@/components/sidebar";
import { TerminalView } from "@/components/terminal-view";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  getCatalog,
  getDevices,
  getHealth,
  getJobs,
  getJson,
  getSessions,
  runAction,
  startSession,
  stopSession,
  upload,
} from "@/lib/api";
import { startTracked, stubFeature } from "@/lib/runs";
import { useConsole } from "@/lib/store";
import type { Device, Feature, Job } from "@/lib/types";
import { artifactUrl, cn, openDevice, openHome } from "@/lib/utils";
import { connectSocket } from "@/lib/ws";

function useHashSerial() {
  const [serial, setSerial] = useState<string | null>(null);
  useEffect(() => {
    const read = () => {
      const hash = window.location.hash.replace(/^#/, "");
      const match = hash.match(/^\/device\/([^/]+)\/?$/);
      setSerial(match ? decodeURIComponent(match[1]) : null);
    };
    read();
    window.addEventListener("hashchange", read);
    return () => window.removeEventListener("hashchange", read);
  }, []);
  return serial;
}

const UPLOAD_PURPOSE: Record<
  string,
  { purpose: string; accept?: string; multiple?: boolean }
> = {
  install_app: { purpose: "install", accept: ".apk" },
  install_split_apks: { purpose: "split", accept: ".apk", multiple: true },
  push_file: { purpose: "push" },
  open_photo: { purpose: "photo", accept: "image/*" },
  open_audio: { purpose: "audio", accept: "audio/*" },
  open_video: { purpose: "video", accept: "video/*" },
  set_wallpaper: { purpose: "wallpaper", accept: "image/*" },
};

export function ConsoleApp() {
  const serial = useHashSerial();
  const queryClient = useQueryClient();
  const flash = useConsole((state) => state.flash);
  const paletteOpen = useConsole((state) => state.paletteOpen);
  const setPaletteOpen = useConsole((state) => state.setPaletteOpen);
  const activityOpen = useConsole((state) => state.activityOpen);
  const setActivityOpen = useConsole((state) => state.setActivityOpen);
  const [activeFeature, setActiveFeature] = useState<Feature | null>(null);
  const [tab, setTab] = useState("overview");
  const [tabSerial, setTabSerial] = useState(serial);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pendingUpload = useRef<{ purpose: string; label: string } | null>(null);
  const pendingTab = useRef<string | null>(null);

  const health = useQuery({ queryKey: ["health"], queryFn: getHealth });
  const catalog = useQuery({ queryKey: ["catalog"], queryFn: getCatalog });
  const devices = useQuery({ queryKey: ["devices"], queryFn: getDevices });
  const jobs = useQuery({
    queryKey: ["jobs"],
    queryFn: getJobs,
    refetchInterval: 4000,
  });

  useEffect(() => {
    return connectSocket("/ws/devices", {
      onmessage: (event) => {
        if (typeof event.data !== "string") return;
        try {
          const payload = JSON.parse(event.data) as { devices: Device[] };
          queryClient.setQueryData(["devices"], { ok: true, data: payload });
        } catch {
          // Ignore malformed device frames.
        }
      },
    });
  }, [queryClient]);

  useEffect(() => {
    return connectSocket("/ws/jobs", {
      onmessage: (event) => {
        if (typeof event.data !== "string") return;
        try {
          const payload = JSON.parse(event.data) as { job?: Job; jobs?: Job[] };
          const { applyJob } = useConsole.getState();
          if (payload.job) applyJob(payload.job);
          if (Array.isArray(payload.jobs)) {
            for (const job of payload.jobs) applyJob(job);
          }
        } catch {
          // Ignore malformed job frames.
        }
        queryClient.invalidateQueries({ queryKey: ["jobs"] });
      },
    });
  }, [queryClient]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setPaletteOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setPaletteOpen]);

  if (serial !== tabSerial) {
    setTabSerial(serial);
    setTab(pendingTab.current ?? "overview");
    pendingTab.current = null;
  }

  const list = devices.data?.data.devices ?? [];
  const features = catalog.data?.features ?? [];

  function handleFeature(feature: Feature) {
    if (useConsole.getState().activeRun?.status === "running") {
      flash("An action is already running.");
      return;
    }
    const uploadSpec = UPLOAD_PURPOSE[feature.id];
    if (uploadSpec) {
      if (!serial) {
        flash("Open a device first.");
        return;
      }
      pendingUpload.current = {
        purpose: uploadSpec.purpose,
        label: feature.label,
      };
      const input = fileInputRef.current;
      if (input) {
        input.value = "";
        input.accept = uploadSpec.accept ?? "";
        input.multiple = Boolean(uploadSpec.multiple);
        input.click();
      }
      return;
    }
    if (feature.id === "live_logcat") {
      if (serial) {
        setTab("logcat");
        flash("Live logcat streams in the Logcat tab.");
      } else flash("Open a device first.");
      return;
    }
    if (
      feature.fields.length === 0 &&
      feature.tier === "native" &&
      !feature.destructive
    ) {
      launchFeature(feature, {});
      return;
    }
    setActiveFeature(feature);
  }

  function launchFeature(
    feature: Feature,
    params: Record<string, string>,
    target = serial ?? "",
  ) {
    if (feature.tier === "screen") {
      if (target) openDevice(target);
      return true;
    }
    if (feature.tier === "terminal") {
      if (feature.id === "metasploit" && params.lhost) {
        return startTracked({
          feature,
          params,
          serial: target,
          scope: "device",
          kind: "action",
          run: () => runAction(feature.id, target, "device", params),
          onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["jobs"] });
          },
        });
      }
      if (target) {
        if (target !== serial) pendingTab.current = "tools";
        else setTab("tools");
        openDevice(target);
      }
      flash(
        feature.id === "shell"
          ? "Open Tools to use the shell."
          : "Open Tools for the Metasploit console.",
      );
      return true;
    }
    if (feature.tier === "host_process") {
      return startTracked({
        feature,
        params,
        serial: target,
        scope: feature.scope,
        kind: "session",
        cancelable: false,
        run: async () => {
          const result = await startSession(target, feature.id, params);
          return {
            ok: result.ok,
            message: result.ok
              ? `Started ${feature.label}`
              : "Could not start session",
            artifact: result.artifact,
          };
        },
        onSettled: () => {
          queryClient.invalidateQueries({ queryKey: ["sessions"] });
        },
      });
    }
    return startTracked({
      feature,
      params,
      serial: target,
      scope: feature.scope,
      kind: "action",
      run: () => runAction(feature.id, target, feature.scope, params),
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["jobs"] });
        queryClient.invalidateQueries({ queryKey: ["devices"] });
      },
    });
  }

  const header = (
    <ShellHeader
      adb={!!health.data?.adb}
      scrcpy={!!health.data?.scrcpy}
      nmap={!!health.data?.nmap}
      hardax={!!health.data?.hardax}
      onPalette={() => setPaletteOpen(true)}
      onActivity={() => setActivityOpen(true)}
    />
  );

  return (
    <div className="relative min-h-screen">
      <div className="pointer-events-none absolute inset-0 grid-fade" />
      <div className="relative mx-auto flex min-h-screen max-w-[1440px] flex-col md:flex-row">
        {serial ? (
          <Tabs
            orientation="vertical"
            value={tab}
            onValueChange={setTab}
            className="flex min-h-screen w-full flex-col md:flex-row"
          >
            <Sidebar devices={list} serial={serial} showNavigation />
            <div className="flex min-w-0 flex-1 flex-col">
              {header}
              <main className="p-4 md:p-6">
                <TabsList
                  className="mb-4 md:hidden"
                  aria-label="Device sections"
                >
                  {DEVICE_TABS.map((item) => (
                    <TabsTrigger key={item} value={item} className="capitalize">
                      {item}
                    </TabsTrigger>
                  ))}
                </TabsList>
                <DeviceWorkspace
                  key={serial}
                  serial={serial}
                  device={list.find((item) => item.serial === serial)}
                  features={features}
                  onFeature={handleFeature}
                />
              </main>
            </div>
          </Tabs>
        ) : (
          <>
            <Sidebar devices={list} serial={null} />
            <div className="flex min-w-0 flex-1 flex-col">
              {header}
              <main className="p-4 md:p-6">
                <Dashboard
                  devices={list}
                  loading={devices.isLoading}
                  error={
                    devices.error instanceof Error
                      ? devices.error.message
                      : null
                  }
                  onFeature={handleFeature}
                />
              </main>
            </div>
          </>
        )}
      </div>
      <CommandPalette
        open={paletteOpen}
        onOpenChange={setPaletteOpen}
        features={features}
        onPick={(feature) => {
          setPaletteOpen(false);
          if (UPLOAD_PURPOSE[feature.id] || feature.id === "live_logcat") {
            handleFeature(feature);
            return;
          }
          if (
            feature.fields.length === 0 &&
            feature.tier === "native" &&
            !feature.destructive
          ) {
            launchFeature(feature, {});
          } else setActiveFeature(feature);
        }}
      />
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        aria-label="Upload file"
        onChange={(event) => {
          const files = [...(event.target.files ?? [])];
          const pending = pendingUpload.current;
          pendingUpload.current = null;
          event.currentTarget.value = "";
          if (!pending || !serial || files.length === 0) return;
          const names =
            files.length === 1 ? files[0].name : `${files.length} files`;
          startTracked({
            feature: stubFeature({
              id: `upload:${pending.purpose}`,
              label: pending.label,
              scope: "device",
            }),
            params: { purpose: pending.purpose },
            serial,
            scope: "device",
            kind: "upload",
            message: `Uploading ${names}…`,
            run: () => upload(serial, pending.purpose, files, ""),
            onSettled: () => {
              queryClient.invalidateQueries({ queryKey: ["jobs"] });
            },
          });
        }}
      />
      <FeatureDialog
        feature={activeFeature}
        onClose={() => setActiveFeature(null)}
        onSubmit={(feature, params) => {
          if (launchFeature(feature, params)) setActiveFeature(null);
        }}
      />
      <ActionRunner />
      <ActivityDrawer
        open={activityOpen}
        onOpenChange={setActivityOpen}
        jobs={jobs.data?.jobs ?? []}
      />
    </div>
  );
}

function ShellHeader({
  adb,
  scrcpy,
  nmap,
  hardax,
  onPalette,
  onActivity,
}: {
  adb: boolean;
  scrcpy: boolean;
  nmap: boolean;
  hardax: boolean;
  onPalette: () => void;
  onActivity: () => void;
}) {
  return (
    <header className="flex items-center gap-3 border-b border-border px-4 py-3">
      <div className="flex items-center gap-2 text-xs">
        <Dot on={adb} label="ADB" />
        <Dot on={scrcpy} label="scrcpy" />
        <Dot on={nmap} label="nmap" />
        <Dot on={hardax} label="HARDAX" />
      </div>
      <button
        type="button"
        onClick={onPalette}
        className="ml-auto flex h-9 w-full max-w-sm items-center gap-2 rounded-md border border-border bg-black/40 px-3 text-sm text-muted-foreground"
      >
        <Search className="h-4 w-4" />
        Search features
        <kbd className="ml-auto rounded border border-border px-1.5 text-[10px]">
          ⌘K
        </kbd>
      </button>
      <Button
        variant="outline"
        size="icon"
        onClick={onActivity}
        aria-label="Activity"
      >
        <Activity className="h-4 w-4" />
      </Button>
    </header>
  );
}

function Dot({ on, label }: { on: boolean; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-muted-foreground">
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          on ? "bg-term" : "bg-primary",
        )}
      />
      {label}
    </span>
  );
}

function Dashboard({
  devices,
  loading,
  error,
  onFeature,
}: {
  devices: Device[];
  loading: boolean;
  error: string | null;
  onFeature: (feature: Feature) => void;
}) {
  const catalog = useQuery({ queryKey: ["catalog"], queryFn: getCatalog });
  const quick = [
    "connect",
    "wireless_pair",
    "scan_network",
    "restart_adb",
    "stop_adb",
    "disconnect",
  ];
  const features = (catalog.data?.features ?? []).filter(
    (feature, index, all) => {
      return (
        quick.includes(feature.id) &&
        all.findIndex((item) => item.id === feature.id) === index
      );
    },
  );

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl tracking-tight">Live devices</h1>
          <p className="text-sm text-muted-foreground">
            USB and wireless ADB sessions on this computer.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {features.map((feature) => (
            <Button
              key={feature.id}
              variant="outline"
              size="sm"
              onClick={() => onFeature(feature)}
            >
              {feature.label}
            </Button>
          ))}
        </div>
      </div>
      {loading && (
        <p className="text-sm text-muted-foreground">Looking for devices…</p>
      )}
      {error && <p className="text-sm text-primary">{error}</p>}
      {!loading && devices.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="py-10 text-sm text-muted-foreground">
            Nothing is attached. Connect a phone with USB debugging, or use
            Connect / Pair above.
          </CardContent>
        </Card>
      )}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {devices.map((device, index) => (
          <motion.button
            key={device.serial}
            type="button"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.04 }}
            onClick={() =>
              device.state === "device" && openDevice(device.serial)
            }
            className="rounded-lg border border-border bg-card p-4 text-left hover:border-accent"
          >
            <div className="mb-3 flex items-center justify-between">
              <Badge
                className={
                  device.state === "device"
                    ? "border-term/40 text-term"
                    : "text-amber"
                }
              >
                {device.state}
              </Badge>
              <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                {device.transport === "wifi" ? (
                  <Wifi className="h-3 w-3" />
                ) : (
                  <Radio className="h-3 w-3" />
                )}
                {device.transport}
              </span>
            </div>
            <p className="font-display text-xl">
              {device.model || "Unknown device"}
            </p>
            <p className="truncate font-mono text-xs text-muted-foreground">
              {device.serial}
            </p>
            <div className="mt-4 flex items-center gap-3 text-sm">
              <span>Android {device.android || "—"}</span>
              <span className="inline-flex items-center gap-1">
                <Battery className="h-4 w-4 text-lime" />
                {device.battery ? `${device.battery}%` : "—"}
              </span>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  );
}

function DeviceWorkspace({
  serial,
  device,
  features,
  onFeature,
}: {
  serial: string;
  device?: Device;
  features: Feature[];
  onFeature: (feature: Feature) => void;
}) {
  const unique = useMemo(() => {
    const seen = new Set<string>();
    return features.filter((feature) => {
      if (feature.scope === "host" || seen.has(feature.id)) return false;
      seen.add(feature.id);
      return true;
    });
  }, [features]);

  return (
    <div>
      <button
        type="button"
        onClick={openHome}
        className="mb-3 inline-flex items-center text-sm text-muted-foreground"
      >
        <ChevronLeft className="h-4 w-4" /> Devices
      </button>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
        <div>
          <h1 className="font-display text-3xl">{device?.model || serial}</h1>
          <p className="font-mono text-xs text-muted-foreground">{serial}</p>
        </div>
        <div className="flex gap-2 text-sm text-muted-foreground">
          <span>Android {device?.android || "—"}</span>
          <span>{device?.battery ? `${device.battery}%` : ""}</span>
        </div>
      </div>
      <TabsContent value="overview">
        <Overview serial={serial} />
      </TabsContent>
      <TabsContent value="screen">
        <ScreenView serial={serial} />
        <div className="mt-4 flex flex-wrap gap-2">
          {unique
            .filter((feature) =>
              [
                "screenshot",
                "anon_screenshot",
                "screenrecord",
                "anon_screenrecord",
              ].includes(feature.id),
            )
            .map((feature) => (
              <Button
                key={feature.id}
                variant="outline"
                size="sm"
                onClick={() => onFeature(feature)}
              >
                {feature.label}
              </Button>
            ))}
        </div>
      </TabsContent>
      <TabsContent value="apps">
        <AppsPanel serial={serial} onFeature={onFeature} features={unique} />
      </TabsContent>
      <TabsContent value="files">
        <FilesPanel serial={serial} onFeature={onFeature} features={unique} />
      </TabsContent>
      <TabsContent value="data">
        <DataPanel serial={serial} onFeature={onFeature} features={unique} />
      </TabsContent>
      <TabsContent value="logcat">
        <Logcat serial={serial} onFeature={onFeature} />
      </TabsContent>
      <TabsContent value="controls">
        <FeatureGrid
          features={unique.filter((feature) =>
            [
              "unlock",
              "lock",
              "reboot",
              "reboot_advanced",
              "power_off",
              "keycode_text",
              "keycode_home",
              "keycode_back",
              "keycode_power",
              "radio_data",
              "radio_bluetooth",
              "radio_nfc",
              "radio_airplane",
              "wifi_toggle",
              "sound_volume_show",
              "sound_volume_set",
              "sound_brightness",
              "sound_timeout",
              "sound_dnd",
              "screen_stay_on",
              "notif_post",
              "notif_expand",
              "notif_collapse",
              "mock_battery_set",
              "mock_battery_reset",
              "display_view",
              "display_resolution",
              "display_density",
              "display_reset",
              "developer_settings",
              "clipboard_read",
              "clipboard_set",
              "clipboard_clear",
              "location",
            ].includes(feature.id),
          )}
          onFeature={onFeature}
        />
      </TabsContent>
      <TabsContent value="network">
        <NetworkPanel serial={serial} onFeature={onFeature} features={unique} />
      </TabsContent>
      <TabsContent value="security">
        <FeatureGrid
          features={unique.filter(
            (feature) =>
              feature.id.startsWith("vuln_") ||
              feature.id === "root_heuristics",
          )}
          onFeature={onFeature}
        />
      </TabsContent>
      <TabsContent value="tools">
        <ToolsPanel serial={serial} features={unique} onFeature={onFeature} />
      </TabsContent>
    </div>
  );
}

function Overview({ serial }: { serial: string }) {
  const query = useQuery({
    queryKey: ["overview", serial],
    queryFn: async () => {
      const [device, battery] = await Promise.all([
        runAction("device_info", serial, "device", {}),
        runAction("battery_info", serial, "device", {}),
      ]);
      return { device, battery };
    },
  });
  if (query.isLoading)
    return <p className="text-sm text-muted-foreground">Reading device…</p>;
  if (query.error)
    return (
      <p className="text-sm text-primary">{(query.error as Error).message}</p>
    );
  const props = (query.data?.device.data ?? {}) as Record<string, string>;
  const battery =
    ((query.data?.battery.data ?? {}) as { props?: Record<string, string> })
      .props ?? {};
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Identity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {Object.entries(props).map(([key, value]) => (
            <div key={key} className="flex justify-between gap-4">
              <span className="text-muted-foreground">{key}</span>
              <span className="truncate text-right">{value || "—"}</span>
            </div>
          ))}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Battery</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {[
            "level",
            "status",
            "temperature",
            "health",
            "AC powered",
            "USB powered",
          ].map((key) => (
            <div key={key} className="flex justify-between gap-4">
              <span className="text-muted-foreground">{key}</span>
              <span>{battery[key] || "—"}</span>
            </div>
          ))}
        </CardContent>
      </Card>
      <ExtraBlocks serial={serial} />
    </div>
  );
}

function ExtraBlocks({ serial }: { serial: string }) {
  const query = useQuery({
    queryKey: ["extras", serial],
    queryFn: async () => {
      const [sim, accounts, bluetooth, locale] = await Promise.all([
        runAction("device_sim", serial, "device", {}),
        runAction("device_accounts", serial, "device", {}),
        runAction("device_bluetooth", serial, "device", {}),
        runAction("locale_read", serial, "device", {}),
      ]);
      return { sim, accounts, bluetooth, locale };
    },
  });
  if (!query.data)
    return (
      <p className="text-sm text-muted-foreground md:col-span-2">
        Loading SIM, accounts, Bluetooth…
      </p>
    );
  const sim = (query.data.sim.data ?? {}) as {
    values?: Record<string, string>;
    lookups?: { label: string }[];
  };
  const accounts =
    (
      (query.data.accounts.data ?? {}) as {
        accounts?: { type?: string; name?: string }[];
      }
    ).accounts ?? [];
  const radios =
    (
      (query.data.bluetooth.data ?? {}) as {
        devices?: { name?: string; address?: string; vendor?: string }[];
      }
    ).devices ?? [];
  const locale = (query.data.locale.data ?? {}) as Record<string, string>;
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>SIM / locale</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm">
          {Object.entries(sim.values ?? {}).map(([key, value]) => (
            <p key={key}>
              <span className="text-muted-foreground">{key}: </span>
              {value || "—"}
            </p>
          ))}
          {(sim.lookups ?? []).map((item) => (
            <p key={item.label} className="text-accent">
              {item.label}
            </p>
          ))}
          {Object.entries(locale).map(([key, value]) => (
            <p key={key}>
              <span className="text-muted-foreground">{key}: </span>
              {value || "—"}
            </p>
          ))}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Accounts and Bluetooth</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm">
          {accounts.length === 0 && (
            <p className="text-muted-foreground">No accounts parsed.</p>
          )}
          {accounts.slice(0, 8).map((account) => (
            <p key={`${account.type}-${account.name}`}>
              {account.type} · {account.name}
            </p>
          ))}
          {radios.slice(0, 8).map((item) => (
            <p key={item.address}>
              {item.name || "Unnamed"} · {item.address} ·{" "}
              {item.vendor || "unknown vendor"}
            </p>
          ))}
        </CardContent>
      </Card>
    </>
  );
}

function AppsPanel({
  serial,
  features,
  onFeature,
}: {
  serial: string;
  features: Feature[];
  onFeature: (feature: Feature) => void;
}) {
  const [filter, setFilter] = useState("");
  const [thirdParty, setThirdParty] = useState(true);
  const query = useQuery({
    queryKey: ["apps", serial, thirdParty],
    queryFn: () =>
      runAction("list_apps", serial, "device", {
        thirdParty: thirdParty ? "true" : "false",
      }),
  });
  const packages = (
    ((query.data?.data ?? {}) as { packages?: string[] }).packages ?? []
  ).filter((pkg) => pkg.toLowerCase().includes(filter.toLowerCase()));
  const queryClient = useQueryClient();

  function runPackage(id: string, label: string, pkg: string) {
    const feature =
      features.find((item) => item.id === id) ??
      stubFeature({ id, label, scope: "device" });
    startTracked({
      feature,
      params: { package: pkg },
      serial,
      scope: "device",
      kind: "action",
      run: () => runAction(id, serial, "device", { package: pkg }),
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["jobs"] });
      },
    });
  }

  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2">
        <Input
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          placeholder="Filter packages"
          className="max-w-xs"
        />
        <Button
          variant="outline"
          size="sm"
          onClick={() => setThirdParty((value) => !value)}
        >
          {thirdParty ? "Third-party" : "All packages"}
        </Button>
        <UploadButton serial={serial} purpose="install" label="Install APK" />
        <UploadButton
          serial={serial}
          purpose="split"
          label="Install splits"
          multiple
        />
        {features
          .filter((feature) =>
            ["usage_stats", "show_home_app", "battery_whitelist_show"].includes(
              feature.id,
            ),
          )
          .map((feature) => (
            <Button
              key={feature.id}
              variant="outline"
              size="sm"
              onClick={() => onFeature(feature)}
            >
              {feature.label}
            </Button>
          ))}
      </div>
      {query.isLoading && (
        <p className="text-sm text-muted-foreground">Loading packages…</p>
      )}
      <div className="max-h-[560px] overflow-auto rounded-lg border border-border">
        {packages.map((pkg) => (
          <div
            key={pkg}
            className="flex items-center gap-2 border-b border-border px-3 py-2 text-sm last:border-0"
          >
            <span className="min-w-0 flex-1 truncate font-mono">{pkg}</span>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => runPackage("launch_app", "Run app", pkg)}
            >
              Run
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => runPackage("force_stop_app", "Stop app", pkg)}
            >
              Stop
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => runPackage("extract_apk", "Extract APK", pkg)}
            >
              APK
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}

function FilesPanel({
  serial,
  features,
  onFeature,
}: {
  serial: string;
  features: Feature[];
  onFeature: (feature: Feature) => void;
}) {
  const [path, setPath] = useState("/sdcard");
  const query = useQuery({
    queryKey: ["files", serial, path],
    queryFn: () =>
      getJson<{
        data: { path: string; entries: { name: string; kind: string }[] };
      }>(
        `/api/devices/${encodeURIComponent(serial)}/files?path=${encodeURIComponent(path)}`,
      ),
  });
  const entries = query.data?.data.entries ?? [];
  const queryClient = useQueryClient();
  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2">
        <Input
          value={path}
          onChange={(event) => setPath(event.target.value)}
          className="max-w-md font-mono"
        />
        <UploadButton
          serial={serial}
          purpose="push"
          label="Push file"
          destination={path.replace(/^\/sdcard\/?/, "")}
        />
        {features
          .filter((feature) =>
            [
              "copy_whatsapp",
              "copy_screenshots",
              "copy_camera",
              "pull_file",
              "set_wallpaper",
              "open_photo",
              "open_audio",
              "open_video",
            ].includes(feature.id),
          )
          .map((feature) => (
            <Button
              key={feature.id}
              size="sm"
              variant="outline"
              onClick={() => onFeature(feature)}
            >
              {feature.label}
            </Button>
          ))}
      </div>
      {query.isLoading && (
        <p className="text-sm text-muted-foreground">Listing…</p>
      )}
      {query.error && (
        <p className="text-sm text-primary">{(query.error as Error).message}</p>
      )}
      <div className="max-h-[560px] overflow-auto rounded-lg border border-border">
        {path !== "/sdcard" && (
          <button
            type="button"
            className="block w-full px-3 py-2 text-left text-sm text-accent"
            onClick={() =>
              setPath(path.split("/").slice(0, -1).join("/") || "/")
            }
          >
            ..
          </button>
        )}
        {entries.map((entry) => (
          <button
            key={entry.name}
            type="button"
            className="flex w-full items-center justify-between border-t border-border px-3 py-2 text-left text-sm hover:bg-muted"
            onClick={() => {
              if (entry.kind === "dir") {
                setPath(`${path.replace(/\/$/, "")}/${entry.name}`);
                return;
              }
              const relative =
                `${path.replace(/^\/sdcard\/?/, "")}/${entry.name}`.replace(
                  /^\/+/,
                  "",
                );
              const feature =
                features.find((item) => item.id === "pull_file") ??
                stubFeature({ id: "pull_file", label: "Pull file" });
              startTracked({
                feature,
                params: { path: relative },
                serial,
                scope: "device",
                kind: "action",
                run: () =>
                  runAction("pull_file", serial, "device", { path: relative }),
                onSettled: () => {
                  queryClient.invalidateQueries({ queryKey: ["jobs"] });
                },
              });
            }}
          >
            <span className="font-mono">{entry.name}</span>
            <span className="text-xs text-muted-foreground">{entry.kind}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function DataPanel({
  serial,
  features,
  onFeature,
}: {
  serial: string;
  features: Feature[];
  onFeature: (feature: Feature) => void;
}) {
  return (
    <FeatureGrid
      features={features.filter((feature) =>
        [
          "dump_sms",
          "dump_contacts",
          "dump_call_logs",
          "send_sms",
          "location",
          "usage_stats",
          "open_link",
        ].includes(feature.id),
      )}
      onFeature={onFeature}
      serialHint={serial}
    />
  );
}

function NetworkPanel({
  serial,
  features,
  onFeature,
}: {
  serial: string;
  features: Feature[];
  onFeature: (feature: Feature) => void;
}) {
  const query = useQuery({
    queryKey: ["net", serial],
    queryFn: () => runAction("network_snapshot", serial, "device", {}),
  });
  const data = (query.data?.data ?? {}) as {
    addr?: string;
    route?: string;
    dns?: string;
  };
  return (
    <div className="space-y-4">
      <FeatureGrid
        features={features.filter((feature) =>
          [
            "wifi_toggle",
            "nearby_wifi",
            "saved_wifi",
            "wifi_status",
            "wlan_ip",
            "hotspot_start",
            "hotspot_stop",
            "ping",
            "port_forward_add",
            "port_forward_reverse",
            "port_forward_list",
            "port_forward_remove",
            "port_forward_remove_all",
          ].includes(feature.id),
        )}
        onFeature={onFeature}
      />
      <pre className="max-h-80 overflow-auto rounded-lg border border-border bg-black p-3 text-xs text-muted-foreground">
        {data.addr ||
          query.data?.message ||
          "Network snapshot loads with the tab."}
        {data.dns ? `\n\nDNS ${data.dns}` : ""}
      </pre>
    </div>
  );
}

function Logcat({
  serial,
  onFeature,
}: {
  serial: string;
  onFeature: (feature: Feature) => void;
}) {
  const [lines, setLines] = useState<string[]>([]);
  useEffect(() => {
    return connectSocket(`/ws/devices/${encodeURIComponent(serial)}/logcat`, {
      onmessage: (event) => {
        if (typeof event.data !== "string") return;
        try {
          const payload = JSON.parse(event.data) as { line?: unknown };
          if (typeof payload.line !== "string") return;
          const line = payload.line;
          setLines((current) => [...current.slice(-400), line]);
        } catch {
          // Ignore malformed log frames.
        }
      },
    });
  }, [serial]);
  return (
    <div>
      <Button
        variant="outline"
        size="sm"
        className="mb-3"
        onClick={() =>
          onFeature({
            id: "logcat_snippet",
            label: "Save logcat snippet",
            hub: null,
            requires: "adb",
            tier: "native",
            scope: "device",
            destructive: false,
            fields: [
              {
                name: "lines",
                label: "Lines",
                type: "number",
                placeholder: "500",
              },
            ],
          })
        }
      >
        Save snippet
      </Button>
      <pre className="h-[480px] overflow-auto rounded-lg border border-border bg-black p-3 font-mono text-xs leading-5 text-[#c8c8c8]">
        {lines.join("\n") || "Waiting for logcat…"}
      </pre>
    </div>
  );
}

function ToolsPanel({
  serial,
  features,
  onFeature,
}: {
  serial: string;
  features: Feature[];
  onFeature: (feature: Feature) => void;
}) {
  const [mode, setMode] = useState<"shell" | "metasploit">("shell");
  const sessions = useQuery({
    queryKey: ["sessions"],
    queryFn: getSessions,
    refetchInterval: 3000,
  });
  const queryClient = useQueryClient();
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Button
          variant={mode === "shell" ? "default" : "outline"}
          size="sm"
          onClick={() => setMode("shell")}
        >
          Device shell
        </Button>
        <Button
          variant={mode === "metasploit" ? "default" : "outline"}
          size="sm"
          onClick={() => setMode("metasploit")}
        >
          msfconsole
        </Button>
        {features
          .filter(
            (feature) =>
              feature.tier === "host_process" || feature.id === "metasploit",
          )
          .filter(
            (feature, index, all) =>
              all.findIndex((item) => item.id === feature.id) === index,
          )
          .map((feature) => (
            <Button
              key={feature.id}
              variant="outline"
              size="sm"
              onClick={() => onFeature(feature)}
            >
              {feature.label}
            </Button>
          ))}
      </div>
      <TerminalView mode={mode} serial={serial} />
      <div className="space-y-2">
        {(sessions.data?.sessions ?? []).map((session) => (
          <div
            key={session.id}
            className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
          >
            <span>
              {session.feature} · {session.running ? "running" : "stopped"}
            </span>
            {session.running && (
              <Button
                size="sm"
                variant="danger"
                onClick={() =>
                  startTracked({
                    feature: stubFeature({
                      id: "stop_session",
                      label: `Stop ${session.feature}`,
                    }),
                    params: { session: session.id },
                    serial: session.serial,
                    scope: "device",
                    kind: "session",
                    cancelable: false,
                    run: async () => {
                      const result = await stopSession(session.id);
                      return {
                        ok: result.ok,
                        message: result.ok
                          ? "Session stopped"
                          : "Could not stop session",
                      };
                    },
                    onSettled: () => {
                      queryClient.invalidateQueries({ queryKey: ["sessions"] });
                    },
                  })
                }
              >
                Stop
              </Button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function FeatureGrid({
  features,
  onFeature,
}: {
  features: Feature[];
  onFeature: (feature: Feature) => void;
  serialHint?: string;
}) {
  return (
    <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
      {features.map((feature) => (
        <button
          key={`${feature.hub}-${feature.id}`}
          type="button"
          onClick={() => onFeature(feature)}
          className="rounded-lg border border-border bg-card px-3 py-3 text-left hover:border-accent"
        >
          <p className="text-sm">{feature.label}</p>
          <p className="text-xs text-muted-foreground">
            {feature.hub || feature.tier}
          </p>
        </button>
      ))}
    </div>
  );
}

function UploadButton({
  serial,
  purpose,
  label,
  multiple,
  destination,
}: {
  serial: string;
  purpose: string;
  label: string;
  multiple?: boolean;
  destination?: string;
}) {
  const queryClient = useQueryClient();
  return (
    <label className="inline-flex h-8 cursor-pointer items-center rounded-md border border-border px-2.5 text-xs hover:border-accent">
      {label}
      <input
        type="file"
        multiple={multiple}
        accept={
          purpose === "install" || purpose === "split" ? ".apk" : undefined
        }
        className="hidden"
        aria-label={label}
        onChange={(event) => {
          const files = [...(event.target.files ?? [])];
          event.currentTarget.value = "";
          if (!files.length) return;
          const names =
            files.length === 1 ? files[0].name : `${files.length} files`;
          startTracked({
            feature: stubFeature({
              id: `upload:${purpose}`,
              label,
              scope: "device",
            }),
            params: { purpose, destination: destination ?? "" },
            serial,
            scope: "device",
            kind: "upload",
            message: `Uploading ${names}…`,
            run: () => upload(serial, purpose, files, destination ?? ""),
            onSettled: () => {
              queryClient.invalidateQueries({ queryKey: ["jobs"] });
            },
          });
        }}
      />
    </label>
  );
}

function CommandPalette({
  open,
  onOpenChange,
  features,
  onPick,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  features: Feature[];
  onPick: (feature: Feature) => void;
}) {
  const [query, setQuery] = useState("");
  const matches = features
    .filter(
      (feature, index, all) =>
        all.findIndex(
          (item) => item.id === feature.id && item.hub === feature.hub,
        ) === index,
    )
    .filter((feature) =>
      `${feature.label} ${feature.hub ?? ""}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    )
    .slice(0, 12);
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>Features</DialogTitle>
        <DialogDescription>
          Every action from this branch of PhoneSploit Pro.
        </DialogDescription>
        <Input
          autoFocus
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="screenshot, sms, wifi…"
          className="mt-4"
        />
        <div className="mt-3 max-h-80 overflow-auto">
          {matches.map((feature) => (
            <button
              key={`${feature.hub}-${feature.id}`}
              type="button"
              className="flex w-full items-center justify-between rounded-md px-2 py-2 text-left text-sm hover:bg-muted"
              onClick={() => onPick(feature)}
            >
              <span>{feature.label}</span>
              <span className="text-xs text-muted-foreground">
                {feature.hub || feature.tier}
              </span>
            </button>
          ))}
          {matches.length === 0 && (
            <p className="px-2 py-6 text-sm text-muted-foreground">
              No matches.
            </p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function FeatureDialog({
  feature,
  onClose,
  onSubmit,
}: {
  feature: Feature | null;
  onClose: () => void;
  onSubmit: (feature: Feature, params: Record<string, string>) => void;
}) {
  const [params, setParams] = useState<Record<string, string>>({});
  return (
    <Dialog
      key={feature?.id ?? "closed"}
      open={!!feature}
      onOpenChange={(open) => {
        if (!open) {
          setParams({});
          onClose();
        }
      }}
    >
      <DialogContent>
        <DialogTitle>{feature?.label}</DialogTitle>
        <DialogDescription>
          {feature?.destructive
            ? "This can disconnect the device or delete data."
            : feature?.hub || "Run this action"}
        </DialogDescription>
        <form
          className="mt-4 space-y-3"
          onSubmit={(event) => {
            event.preventDefault();
            if (feature) onSubmit(feature, params);
          }}
        >
          {(feature?.fields ?? []).map((field) => (
            <div key={field.name} className="block text-sm">
              <span className="mb-1 block text-muted-foreground">
                {field.label}
              </span>
              {field.type === "select" ? (
                <select
                  className="h-9 w-full rounded-md border border-border bg-input px-2"
                  value={params[field.name] ?? ""}
                  onChange={(event) =>
                    setParams((current) => ({
                      ...current,
                      [field.name]: event.target.value,
                    }))
                  }
                  required={field.required}
                >
                  <option value="">Choose</option>
                  {(field.options ?? []).map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : (
                <Input
                  type={field.type === "number" ? "number" : "text"}
                  placeholder={field.placeholder}
                  required={field.required}
                  value={params[field.name] ?? ""}
                  onChange={(event) =>
                    setParams((current) => ({
                      ...current,
                      [field.name]: event.target.value,
                    }))
                  }
                />
              )}
            </div>
          ))}
          <Button
            type="submit"
            variant={feature?.destructive ? "danger" : "default"}
          >
            Run
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function ActivityDrawer({
  open,
  onOpenChange,
  jobs,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  jobs: Job[];
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>Activity</DialogTitle>
        <DialogDescription>
          Long-running scans, dumps, and recordings.
        </DialogDescription>
        <div className="mt-4 max-h-96 space-y-2 overflow-auto">
          {jobs.length === 0 && (
            <p className="text-sm text-muted-foreground">No jobs yet.</p>
          )}
          {jobs.map((job) => (
            <div
              key={job.id}
              className="rounded-md border border-border p-3 text-sm"
            >
              <div className="flex justify-between gap-2">
                <span>{job.name}</span>
                <Badge>{job.status}</Badge>
              </div>
              <p className="mt-1 text-muted-foreground">{job.message}</p>
              {job.artifact && (
                <a
                  className="mt-2 inline-block text-accent"
                  href={artifactUrl(job.artifact)}
                >
                  Download
                </a>
              )}
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
