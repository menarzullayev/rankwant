import type { Attempt } from "@/lib/api";
import { isPendingVerdict } from "@/lib/theme/verdict";

/** SSE dan kelgan vaqtinchalik yamoq — REST refresh kelguncha jadvalni yangilaydi. */
export type AttemptLivePatch = {
  verdict?: string;
  running_test_index?: number | null;
};

export function mergeAttemptRow(row: Attempt, patch?: AttemptLivePatch): Attempt {
  if (!patch) return row;
  const patchVerdict = patch.verdict ?? row.verdict;
  const serverPending = isPendingVerdict(row.verdict);
  const patchPending = isPendingVerdict(patchVerdict);

  if (!serverPending && !patchPending) return row;

  return {
    ...row,
    verdict: patchVerdict,
    running_test_index:
      patch.running_test_index !== undefined
        ? patch.running_test_index
        : row.running_test_index,
  };
}

export type AttemptLiveEventPayload = {
  attempt_id?: number;
  problem?: string;
  verdict?: string;
  running_test_index?: number | null;
};
