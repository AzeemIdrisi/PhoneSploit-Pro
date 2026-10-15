"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Device } from "@/lib/types";
import { openDevice, openHome } from "@/lib/utils";

export const DEVICE_TABS = [
  "overview",
  "screen",
  "apps",
  "files",
  "data",
  "logcat",
  "controls",
  "network",
  "security",
  "tools",
] as const;

export function Sidebar({
  devices,
  serial,
  showNavigation = false,
}: {
  devices: Device[];
  serial: string | null;
  showNavigation?: boolean;
}) {
  const connected = devices.filter((device) => device.state === "device");
  const options =
    serial && !connected.some((device) => device.serial === serial)
      ? [
          {
            serial,
            state: "device",
            info: "",
            transport: "",
            model: devices.find((device) => device.serial === serial)?.model,
          } satisfies Device,
          ...connected,
        ]
      : connected;

  return (
    <aside className="w-full shrink-0 border-b border-border p-4 md:sticky md:top-0 md:flex md:max-h-screen md:w-72 md:flex-col md:overflow-y-auto md:border-r md:border-b-0">
      <button type="button" onClick={openHome} className="mb-4 block text-left">
        <p className="font-display text-xl tracking-tight">PhoneSploit Pro</p>
        <p className="font-display text-xs tracking-[0.2em] text-primary uppercase">
          Web Console
        </p>
      </button>
      <p className="mb-2 text-[11px] tracking-widest text-muted-foreground uppercase">
        Device
      </p>
      <Select
        value={serial ?? ""}
        onValueChange={(value) => {
          if (value === "__home__") openHome();
          else openDevice(value);
        }}
      >
        <SelectTrigger aria-label="Device" className="w-full">
          <SelectValue placeholder="Select a device" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="__home__">All devices</SelectItem>
          {options.length === 0 ? (
            <SelectItem value="__none__" disabled>
              No devices yet
            </SelectItem>
          ) : (
            options.map((device) => (
              <SelectItem key={device.serial} value={device.serial}>
                <span className="flex min-w-0 items-baseline gap-2">
                  <span className="truncate">
                    {device.model || device.serial}
                  </span>
                  {device.model ? (
                    <span className="truncate font-mono text-[10px] text-muted-foreground">
                      {device.serial}
                    </span>
                  ) : null}
                </span>
              </SelectItem>
            ))
          )}
        </SelectContent>
      </Select>
      {showNavigation ? (
        <TabsList
          aria-label="Device sections"
          className="mt-4 hidden h-auto w-full flex-col items-stretch gap-1 overflow-x-hidden border-0 bg-transparent p-0 md:flex"
        >
          {DEVICE_TABS.map((item) => (
            <TabsTrigger
              key={item}
              value={item}
              className="w-full justify-start capitalize"
            >
              {item}
            </TabsTrigger>
          ))}
        </TabsList>
      ) : null}
    </aside>
  );
}
