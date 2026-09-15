"use client";

import { createElement } from "react";

import { useCustomizer } from "@/context/CustomizerContext";
import { resolveIcon, usePackMap } from "@/icons/registry";
import { clampIconPack, changesWithPack } from "@/lib/theme/icon-packs";

/** Semantik ikonka — foydalanuvchi tanlagan to'plamdan (D4, D10, D18).
 *
 *  ```tsx
 *  <Icon name="nav.problems" />
 *  <Icon name="action.search" className="size-4" />
 *  ```
 *
 *  ── Qamrov (D20 ①) ─────────────────────────────────────────────────
 *
 *  `nav.*`, `action.*`, `status.*` — to'plamga bo'ysunadi.
 *  `verdict.*`, `brand.*` — **qat'iy**: ular bu komponentdan o'tmaydi
 *  (`Verdict` o'z Phosphor to'plamini ishlatadi). Sabab: qo'llanma va
 *  video darsliklar verdikt belgisiga tayanadi.
 *
 *  Agar bu yerga qat'iy kalit berilsa, u **standart to'plamda** chiziladi —
 *  ya'ni noto'g'ri ishlatilsa ham foydalanuvchi kutgan belgi o'zgarmaydi.
 *
 *  ── O'lcham (D3) ───────────────────────────────────────────────────
 *
 *  `size` — 16/20/24/32 shkalasi. Berilmasa `md` (24px), ya'ni D19:
 *  mobil moslashuvda o'lcham o'zgarmaydi, faqat matn qisqaradi.
 */
const SIZE: Record<"sm" | "md" | "lg" | "xl", string> = {
  sm: "size-4", // 16px
  md: "size-5", // 20px
  lg: "size-6", // 24px
  xl: "size-8", // 32px
};

export function Icon({
  name,
  size = "md",
  className,
  pack,
}: {
  /** Semantik kalit (D18): `nav.problems`, `action.submit`, `status.warning`. */
  name: string;
  /** D3 shkalasi. D19: mobil uchun alohida qiymat yo'q. */
  size?: keyof typeof SIZE;
  /** Qo'shimcha sinf. Berilsa `size` ni bekor qiladi. */
  className?: string;
  /** To'plamni majburan tanlash — namuna va testlar uchun. */
  pack?: string;
}) {
  const { appearance } = useCustomizer();
  // ⚠️ `usePackMap` hookni SHARTSIZ chaqirish kerak — shuning uchun qat'iy
  // kalitda ham chaqiriladi, faqat natijasi ishlatilmaydi.
  const selected = clampIconPack(pack ?? appearance.iconPack);
  const map = usePackMap(selected);
  const Cmp = resolveIcon(name, selected, map);

  if (!Cmp) return null;
  // ⚠️ `createElement`, JSX emas: komponent render paytida tanlanadi
  // (to'plam xaritasidan), `react-hooks/static-components` esa JSX'dagi
  // dinamik komponentni statik deb hisoblay olmaydi. Xulqi bir xil.
  return createElement(Cmp, { className: className ?? SIZE[size] });
}

/** Shu kalit to'plam almashganda o'zgaradimi — Customizer namunasi va
 *  testlar uchun. */
export { changesWithPack };
