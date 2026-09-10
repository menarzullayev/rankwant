import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { type Locale, t } from "@/i18n/messages";

/** Rang guruhlari: yashil = qabul qilindi, sariq = hali ketmoqda yoki
 * qisman, qizil = FOYDALANUVCHI xatosi, kulrang = infratuzilma yoki
 * masala nosozligi. Kulrang muhim: `IE`, `WRONG_TEST`,
 * `DENIAL_OF_JUDGEMENT` odamning aybi emas, qizil ko'rsatish uni
 * bekorga ayblardi.
 *
 * Yorliqlar bu yerda EMAS — `verdict.<KOD>` kalitlari orqali tarjima
 * qilinadi (10 til). */
const COLOR: Record<string, BadgeColor> = {
  PENDING: "neutral",
  RUNNING: "warning",
  TESTING_ABORTED: "warning",
  AC: "success",
  PARTIAL: "warning",
  WA: "error",
  PE: "error",
  TLE: "error",
  MLE: "error",
  OLE: "error",
  RE: "error",
  RE_SIGNAL: "error",
  RE_EXIT: "error",
  CE: "error",
  COMPILE_TIMEOUT: "error",
  IDLENESS: "error",
  SECURITY_VIOLATION: "error",
  RATE_LIMITED: "warning",
  SKIPPED: "neutral",
  IE: "neutral",
  CHECKER_ERROR: "neutral",
  WRONG_TEST: "neutral",
  DENIAL_OF_JUDGEMENT: "neutral",
};

/** Verdict kodlari — `apps/api/judging/verdicts.py` bilan bir xil ro'yxat.
 *
 * Rang guruhlari: yashil = qabul qilindi, sariq = hali ketmoqda yoki
 * qisman, qizil = foydalanuvchi xatosi, kulrang = infratuzilma nosozligi
 * (foydalanuvchi aybi emas, shuning uchun qizil emas). */

/** Hali natija kutilayotgan holatlar — mijoz shu paytda pollinglaydi.
 *
 * `TESTING_ABORTED` ham shu yerda: rejudge eski natijani bekor qildi va
 * yangisi yo'lda. Usiz sahifa eski verdictda qotib qolardi. */
export const isPending = (verdict: string) =>
  verdict === "PENDING" ||
  verdict === "RUNNING" ||
  verdict === "TESTING_ABORTED";

export function VerdictBadge({
  verdict,
  locale,
}: {
  verdict: string;
  locale: Locale;
}) {
  // Noma'lum kod kelsa — xom kodni ko'rsatamiz: yolg'on yorliqdan
  // ko'ra tushunarsiz kod yaxshiroq.
  const label = t(locale, `verdict.${verdict}` as never) || verdict;
  return <Badge color={COLOR[verdict] ?? "neutral"}>{label}</Badge>;
}
