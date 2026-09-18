import type { AppearancePrefs } from "@/lib/api";

/** Uslub ham hidratsiyadan oldin qo'yiladi — `data-style` butun token
 *  qatlamini almashtiradi, kechikkanda sahifa ko'z oldida sakrardi.
 *
 *  With no choice saved on this device, the team default (D37) applies from
 *  the first paint, the same style the customizer shows. It used to be a
 *  fixed `clay`, so a team default showed up only in the panel (APP-14). */
export function styleInit(fallback: string): string {
  const style = JSON.stringify(fallback);
  return `try{var s=localStorage.getItem("style");document.documentElement.dataset.style=s||${style}}catch(e){
document.documentElement.dataset.style=${style}}`;
}

/** The team default appearance as a JS string literal, for the first-paint
 *  scripts. `<` is escaped, so no value can close the `<script>` tag. */
export function teamDefaultLiteral(appearance: AppearancePrefs): string {
  return JSON.stringify(JSON.stringify(appearance)).replace(/</g, "\\u003c");
}
