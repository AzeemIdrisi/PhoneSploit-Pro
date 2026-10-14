import { StatusChip } from "./StatusChip";

/** @deprecated Prefer StatusChip */
export function Badge(
  props: React.ComponentProps<typeof StatusChip> & {
    variant?: "default" | "success" | "warning" | "danger" | "info";
  },
) {
  const map = {
    default: "default" as const,
    success: "lime" as const,
    warning: "amber" as const,
    danger: "red" as const,
    info: "cyan" as const,
  };
  const { variant = "default", ...rest } = props;
  return <StatusChip variant={map[variant]} {...rest} />;
}
