/** `updates` — feature'ning ommaviy yuzasi.
 *
 * Tashqaridan faqat shu fayl orqali import qilinadi:
 * `import { X } from "@/features/updates"`.
 * Ichki tuzilma (`components/`, `api/`) — xususiy.
 */

export { UpdateKindBadge, UpdateModuleBadge, isActionable, kindClass } from "./components/UpdateKindBadge";

export { UpdateReadMarker } from "./components/UpdateReadMarker";

/** Qobiq vidjeti — `layout/HeaderActions` shu yerni yuqoridagi
 *  qatorga qo'yadi. Feature o'z widgetini beradi, qobiq esa uni
 *  faqat nom bilan chaqiradi. */
export { UpdatesBell } from "./components/UpdatesBell";
