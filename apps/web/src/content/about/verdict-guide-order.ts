import type { VerdictKey } from "@/lib/theme/verdict";

/** `/about` jadvali — platformadagi 24 ta `Verdict` kodi (08-technical-spec tartibi). */
export const ABOUT_VERDICT_ORDER: VerdictKey[] = [
  "PENDING",
  "RUNNING",
  "AC",
  "WA",
  "PE",
  "TLE",
  "MLE",
  "OLE",
  "IDLENESS",
  "CE",
  "COMPILE_TIMEOUT",
  "RE_SIGNAL",
  "RE_EXIT",
  "RE",
  "PARTIAL",
  "SKIPPED",
  "HACKED",
  "WRONG_TEST",
  "CHECKER_ERROR",
  "IE",
  "SECURITY_VIOLATION",
  "TESTING_ABORTED",
  "RATE_LIMITED",
  "DENIAL_OF_JUDGEMENT",
];
