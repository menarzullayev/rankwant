import type { Locale } from "@/i18n/messages";
import { t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import type { UpdateKind, UpdateModule } from "@/lib/api";

/** Tur → CSS sinfi.
 *
 *  Tailwind dinamik sinfni skanerlamaydi, ya'ni `rw-kind-${kind}` yig'indisi
 *  ishlamaydi — nomlar to'liq yoziladi. Ranglarning o'zi `globals.css` da
 *  (`.rw-kind-*`), chunki ular kontrast tekshiruvidan o'tadi.
 */
const KIND_CLASS: Record<UpdateKind, string> = {
  new: "rw-kind-new",
  improved: "rw-kind-improved",
  fixed: "rw-kind-fixed",
  performance: "rw-kind-performance",
  security: "rw-kind-security",
  design: "rw-kind-design",
  content: "rw-kind-content",
  infrastructure: "rw-kind-infrastructure",
  breaking: "rw-kind-breaking",
  deprecated: "rw-kind-deprecated",
};

/** Tur → sinf nomi. Filtr chipi ham shu orqali chiziladi, ya'ni
 *  `rw-kind-${kind}` kabi dinamik satr hech qayerda qolmaydi. */
export function kindClass(kind: UpdateKind): string {
  return KIND_CLASS[kind] ?? "rw-chip";
}

/** Harakatga chaqiruvchi turlar.
 *
 *  `apps/api/updates/models.py` dagi `ACTIONABLE` bilan bir xil bo'lishi
 *  shart: backend `is_actionable` ni shu to'plamdan hisoblaydi, UI esa
 *  ogohlantirish belgisini shundan chizadi. Ikki manba ajralib ketsa
 *  yozuv "oddiy" ko'rinadi-yu, lekin harakat talab qiladi.
 */
const ACTIONABLE: readonly UpdateKind[] = ["breaking", "deprecated"];

export function isActionable(kind: UpdateKind): boolean {
  return ACTIONABLE.includes(kind);
}

export function UpdateKindBadge({
  kind,
  locale,
}: {
  kind: UpdateKind;
  locale: Locale;
}) {
  const actionable = isActionable(kind);
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-theme-xs ${
        actionable ? "font-bold" : "font-semibold"
      } ${kindClass(kind)}`}
    >
      {actionable && <Icon name="status.warning" className="size-3.5 shrink-0" />}
      {t(locale, `update.kind.${kind}`)}
    </span>
  );
}

/** Modul nishoni — neytral. Tur rangli, modul esa faqat guruh nomi. */
export function UpdateModuleBadge({
  module,
  locale,
}: {
  module: UpdateModule;
  locale: Locale;
}) {
  return (
    <span className="inline-flex items-center rounded-full rw-chip px-2.5 py-0.5 text-theme-xs">
      {t(locale, `update.module.${module}`)}
    </span>
  );
}
