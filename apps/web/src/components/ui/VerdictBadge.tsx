import { Badge, type BadgeColor } from "@/components/ui/Badge";

const COLOR: Record<string, BadgeColor> = {
  AC: "success",
  PENDING: "neutral",
  RUNNING: "info",
  WA: "error",
  TLE: "warning",
  MLE: "warning",
  RE: "error",
  CE: "neutral",
  IE: "neutral",
};

export function VerdictBadge({ verdict }: { verdict: string }) {
  return <Badge color={COLOR[verdict] ?? "error"}>{verdict}</Badge>;
}
