export type Device = {
  serial: string;
  state: string;
  info: string;
  transport: string;
  model?: string;
  android?: string;
  battery?: string;
};

export type Field = {
  name: string;
  label: string;
  type: "text" | "number" | "select";
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
};

export type Feature = {
  id: string;
  label: string;
  hub: string | null;
  requires: string;
  tier: "native" | "terminal" | "host_process" | "screen";
  scope: "host" | "device";
  destructive: boolean;
  fields: Field[];
};

export type Catalog = {
  groups: { id: string; label: string; features: Feature[] }[];
  features: Feature[];
};

export type Job = {
  id: string;
  name: string;
  status: string;
  message: string;
  artifact?: string | null;
  data?: unknown;
  progress?: number | null;
};

export type ActionResult = {
  ok: boolean;
  message: string;
  data?: unknown;
  artifact?: string | null;
  job?: Job;
};

export type Health = {
  ok: boolean;
  adb: boolean;
  scrcpy: boolean;
  nmap: boolean;
  metasploit: boolean;
  hardax: boolean;
};
