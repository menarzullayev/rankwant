import { Badge, type BadgeColor } from "@/components/ui/Badge";

/** 20 verdict kodi — `apps/api/judging/verdicts.py` bilan bir xil ro'yxat.
 *
 * Rang guruhlari: yashil = qabul qilindi, sariq = hali ketmoqda yoki
 * qisman, qizil = foydalanuvchi xatosi, kulrang = infratuzilma nosozligi
 * (foydalanuvchi aybi emas, shuning uchun qizil emas). */
const VERDICTS: Record<string, { label: string; color: BadgeColor }> = {
  PENDING: { label: "Navbatda", color: "neutral" },
  RUNNING: { label: "Tekshirilmoqda", color: "warning" },
  AC: { label: "Accepted", color: "success" },
  PARTIAL: { label: "Qisman ball", color: "warning" },
  WA: { label: "Wrong Answer", color: "error" },
  TLE: { label: "Time Limit", color: "error" },
  MLE: { label: "Memory Limit", color: "error" },
  OLE: { label: "Output Limit", color: "error" },
  RE: { label: "Runtime Error", color: "error" },
  CE: { label: "Compilation Error", color: "error" },
  PE: { label: "Presentation Error", color: "error" },
  IDLENESS: { label: "Idleness Limit", color: "error" },
  SECURITY_VIOLATION: { label: "Xavfsizlik buzildi", color: "error" },
  SKIPPED: { label: "O'tkazib yuborildi", color: "neutral" },
  COMPILE_TIMEOUT: { label: "Kompilyatsiya cho'zildi", color: "error" },
  IE: { label: "Ichki xato", color: "neutral" },
  CHECKER_ERROR: { label: "Checker xatosi", color: "neutral" },
  TESTING_ABORTED: { label: "Tekshiruv to'xtadi", color: "neutral" },
  RATE_LIMITED: { label: "Submit limiti", color: "neutral" },
  DENIAL_OF_JUDGEMENT: { label: "Infra nosozligi", color: "neutral" },
};

export const isPending = (verdict: string) =>
  verdict === "PENDING" || verdict === "RUNNING";

export function VerdictBadge({ verdict }: { verdict: string }) {
  const known = VERDICTS[verdict];
  return (
    <Badge color={known?.color ?? "neutral"}>{known?.label ?? verdict}</Badge>
  );
}
