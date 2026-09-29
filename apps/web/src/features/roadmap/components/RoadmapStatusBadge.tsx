import { Badge, type BadgeColor } from "@/components/ui/Badge";
import type { Locale } from "@/i18n/messages";
import { t } from "@/i18n/messages";
import type { RoadmapStatus } from "@/lib/api";

/** Holat → rang. `apps/api/roadmap/models.py` `Status` bilan bir xil.
 *
 *  Rang YAGONA tashuvchi emas: yonida har doim matn turadi. Rangni
 *  ajratib ololmaydigan odam uchun ma'no yo'qolmasligi kerak.
 *  `declined` — xato emas, shuning uchun `error` emas: u shunchaki
 *  yopilgan taklif. */
const COLORS: Record<RoadmapStatus, BadgeColor> = {
  suggested: "info",
  planned: "brand",
  in_progress: "warning",
  released: "success",
  declined: "neutral",
};

export function RoadmapStatusBadge({
  status,
  locale,
}: {
  status: RoadmapStatus;
  locale: Locale;
}) {
  return (
    <Badge color={COLORS[status] ?? "neutral"}>
      {t(locale, `roadmap.status.${status}`)}
    </Badge>
  );
}
