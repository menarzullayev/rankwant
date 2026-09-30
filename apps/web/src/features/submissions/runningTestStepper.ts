import { isPendingVerdict } from "@/lib/theme/verdict";

/** Bir rAF tikida har bir urinish uchun ko'rsatiladigan indeksni bir qadam oldinga suradi. */
export function tickRunningTestDisplay(
  display: Record<number, number>,
  targets: Record<number, number>,
): Record<number, number> {
  let changed = false;
  const next = { ...display };
  for (const [idStr, target] of Object.entries(targets)) {
    const id = Number(idStr);
    const cur = next[id] ?? 0;
    if (cur >= target) continue;
    next[id] = cur === 0 ? 1 : cur + 1;
    changed = true;
  }
  return changed ? next : display;
}

export function runningTargetFrom(
  patch: { verdict?: string; running_test_index?: number | null } | undefined,
  serverVerdict: string,
  serverIndex: number | null,
): number | null {
  const verdict = patch?.verdict ?? serverVerdict;
  if (!isPendingVerdict(verdict)) return null;
  const patchIdx = patch?.running_test_index;
  const serverIdx = serverIndex;
  if (patchIdx != null && serverIdx != null) return Math.max(patchIdx, serverIdx);
  if (patchIdx != null) return patchIdx;
  if (serverIdx != null) return serverIdx;
  return null;
}
