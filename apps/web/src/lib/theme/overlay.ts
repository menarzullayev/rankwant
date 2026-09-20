/** Oyna oilalari — tasdiq, modal, tooltip va menyu (plastina 01/06/07/08).
 *
 *  To'rtta tanlov studio'da muhrlangan: Qog'oz (markaz + scrim), Soyabon
 *  (anchor, scrim yo'q), Projektor (vinyetka), Orol (blur + 28px).
 *  CSS `html[data-overlay]` orqali farqlanadi; standart — Qog'oz, shuning
 *  uchun atribut yozilmaydi.
 */

export type OverlayVariant = "qogoz" | "soyabon" | "projektor" | "orol";

export type OverlayKind = "confirm" | "modal" | "menu" | "tip";

export type OverlayPlace = "center" | "anchor";

export type Box = {
  left: number;
  top: number;
  right: number;
  bottom: number;
  width: number;
  height: number;
};

export const DEFAULT_OVERLAY_VARIANT: OverlayVariant = "qogoz";

export const OVERLAY_VARIANTS: {
  id: OverlayVariant;
  labelKey: string;
  hintKey: string;
}[] = [
  {
    id: "qogoz",
    labelKey: "overlay.style.qogoz",
    hintKey: "overlay.style.qogozHint",
  },
  {
    id: "soyabon",
    labelKey: "overlay.style.soyabon",
    hintKey: "overlay.style.soyabonHint",
  },
  {
    id: "projektor",
    labelKey: "overlay.style.projektor",
    hintKey: "overlay.style.projektorHint",
  },
  {
    id: "orol",
    labelKey: "overlay.style.orol",
    hintKey: "overlay.style.orolHint",
  },
];

export function clampOverlayVariant(value: unknown): OverlayVariant {
  return OVERLAY_VARIANTS.some((v) => v.id === value)
    ? (value as OverlayVariant)
    : DEFAULT_OVERLAY_VARIANT;
}

/** Qayerga qo'yish: Soyabon hammasi triggerga yopishadi; Projektor
 *  menyusi ham markazda (studio 07). Tooltip har doim anchor. */
export function overlayPlace(
  variant: OverlayVariant,
  kind: OverlayKind,
): OverlayPlace {
  if (kind === "tip") return "anchor";
  if (variant === "soyabon") return "anchor";
  if (variant === "projektor" && kind === "menu") return "center";
  if (kind === "menu") return "anchor";
  return "center";
}

/** Overlay'ni trigger yoniga qo'yadi, viewportdan chiqarmaydi. */
export function placeNear(
  anchor: Box,
  size: { width: number; height: number },
  viewport: { width: number; height: number },
  where: "below" | "above" | "menu",
  pad = 8,
): { x: number; y: number } {
  const w = Math.max(0, size.width);
  const h = Math.max(0, size.height);
  let x = where === "menu" ? anchor.right - w : anchor.left;
  let y = where === "above" ? anchor.top - h - 6 : anchor.bottom + 6;
  const maxX = Math.max(pad, viewport.width - w - pad);
  const maxY = Math.max(pad, viewport.height - h - pad);
  x = Math.min(Math.max(pad, x), maxX);
  y = Math.min(Math.max(pad, y), maxY);
  return { x, y };
}

/** Tip tepada, qolgani trigger yonida. */
const KIND_SIDE: Record<OverlayKind, "below" | "above" | "menu"> = {
  tip: "above",
  confirm: "menu",
  modal: "menu",
  menu: "menu",
};

export function placeForKind(
  kind: OverlayKind,
  anchor: Box,
  size: { width: number; height: number },
  viewport: { width: number; height: number },
): { x: number; y: number } {
  return placeNear(anchor, size, viewport, KIND_SIDE[kind]);
}

export function boxFromDomRect(r: DOMRect): Box {
  return {
    left: r.left,
    top: r.top,
    right: r.right,
    bottom: r.bottom,
    width: r.width,
    height: r.height,
  };
}

let lastAnchor: Box | null = null;

export function rememberOverlayAnchor(target: EventTarget | null): void {
  if (!(target instanceof Element)) return;
  const el =
    target.closest("button, a, [role='button'], [data-ov-anchor]") ?? target;
  if (!(el instanceof Element)) return;
  lastAnchor = boxFromDomRect(el.getBoundingClientRect());
}

export function lastOverlayAnchor(): Box {
  if (lastAnchor) return lastAnchor;
  if (typeof window === "undefined") {
    return { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 };
  }
  const w = window.innerWidth;
  const h = window.innerHeight;
  return {
    left: w / 2 - 20,
    top: h / 2 - 20,
    right: w / 2 + 20,
    bottom: h / 2 + 20,
    width: 40,
    height: 40,
  };
}

export function startOverlayAnchors(): () => void {
  const on = (event: Event) => rememberOverlayAnchor(event.target);
  document.addEventListener("pointerdown", on, true);
  document.addEventListener("focusin", on, true);
  return () => {
    document.removeEventListener("pointerdown", on, true);
    document.removeEventListener("focusin", on, true);
  };
}

export function currentOverlayVariant(): OverlayVariant {
  if (typeof document === "undefined") return DEFAULT_OVERLAY_VARIANT;
  return clampOverlayVariant(document.documentElement.dataset.overlay);
}
