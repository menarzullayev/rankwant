/** Navigatsiya sozlamalari — yagona manba (D46).
 *
 * kep.uz o'lchovi (2026-09-15, Playwright):
 *   · Sidenav — chapda 300 px, faqat keng ekranda; 1024 dan kichikda umuman
 *     chizilmaydi (header 65 px qoladi), ya'ni burger yo'q — shunchaki yo'qoladi.
 *   · Topnav  — header to'liq kenglik; `nav` elementi umuman yo'q.
 *   · Shape   — faqat balandlik: 83 / 39 / 103 px. Radius hammasida 0.
 *   · Aktiv band: radius 8 px + yarim shaffof fon.
 *   · Submenu: 7 ta trigger (`aria-haspopup`).
 *
 * Biz bundan kengroq qilamiz: shape ga **radius va stil** ham qo'shamiz
 * (kep.uz da faqat balandlik), sidenav esa yig'ilgan/kengaytirilgan
 * holatni saqlaydi (kep.uz da bunday holat yo'q).
 */

/** Navigatsiya joylashuvi. */
export type NavMode = "sidenav" | "topnav";

/** Yuqori panelning shakli — balandlik VA burchak. */
export type NavShape = "default" | "slim" | "stacked";

export const DEFAULT_NAV_MODE: NavMode = "sidenav";
export const DEFAULT_NAV_SHAPE: NavShape = "default";

/** Yon panel o'lchamlari (px). Yig'ilganda faqat ikonka — band nomini
 *  o'qish uchun sichqoncha ustiga keltirganda vaqtincha kengayadi. */
export const SIDENAV_WIDTH = 260;
export const SIDENAV_COLLAPSED = 86;

/** Yuqori panel balandligi — kep.uz dagi 83/39/103 ga mos, lekin
 *  mobil/planshetda siqiqroq (`h-mobile`). */
export const TOPNAV_HEIGHT: Record<NavShape, { base: number; mobile: number }> =
  {
    default: { base: 83, mobile: 65 },
    slim: { base: 39, mobile: 39 },
    stacked: { base: 103, mobile: 88 },
  };

/** Shakl tavsifi — panelda shu ro'yxat chiqadi. */
export type NavShapeDef = {
  id: NavShape;
  labelKey: string;
  hintKey: string;
  /** Burchak radiusi: `default` yumaloq, `slim` keskin (0), `stacked` katta. */
  radiusClass: string;
};

export const NAV_SHAPES: NavShapeDef[] = [
  {
    id: "default",
    labelKey: "navShape.default.label",
    hintKey: "navShape.default.hint",
    radiusClass: "rw-radius",
  },
  {
    id: "slim",
    labelKey: "navShape.slim.label",
    hintKey: "navShape.slim.hint",
    radiusClass: "rounded-none",
  },
  {
    id: "stacked",
    labelKey: "navShape.stacked.label",
    hintKey: "navShape.stacked.hint",
    radiusClass: "rw-radius-lg",
  },
];

/** Rejim tavsifi. */
export const NAV_MODES: {
  id: NavMode;
  labelKey: string;
  hintKey: string;
}[] = [
  { id: "sidenav", labelKey: "navMode.sidenav.label", hintKey: "navMode.sidenav.hint" },
  { id: "topnav", labelKey: "navMode.topnav.label", hintKey: "navMode.topnav.hint" },
];

export const NAV_MODE_IDS: NavMode[] = NAV_MODES.map((m) => m.id);
export const NAV_SHAPE_IDS: NavShape[] = NAV_SHAPES.map((s) => s.id);

/** Noto'g'ri qiymat (buzuk localStorage yoki havola) standartga qaytadi. */
export function clampNavMode(value: unknown): NavMode {
  return value === "topnav" || value === "sidenav" ? value : DEFAULT_NAV_MODE;
}

export function clampNavShape(value: unknown): NavShape {
  return NAV_SHAPE_IDS.includes(value as NavShape)
    ? (value as NavShape)
    : DEFAULT_NAV_SHAPE;
}

/** Shakl bo'yicha yuqori panel klassi — bitta joyda, komponentda emas. */
export function topnavShapeClass(shape: NavShape): string {
  const def = NAV_SHAPES.find((s) => s.id === shape) ?? NAV_SHAPES[0];
  switch (shape) {
    case "slim":
      // Bir qator: logo va bandlar yonma-yon, balandlik minimal.
      return `${def.radiusClass} h-[39px]`;
    case "stacked":
      // Ikki qator: ustunida logo, ostida bandlar — kep.uz dagi 103 px.
      return `${def.radiusClass} h-auto min-h-[88px] flex-col gap-1 py-2 lg:min-h-[103px]`;
    default:
      return `${def.radiusClass} h-[65px] lg:h-[83px]`;
  }
}
