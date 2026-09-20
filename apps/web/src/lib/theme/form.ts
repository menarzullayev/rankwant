/** Forma oilalari — yozuv, belgi, radio, fayl, sana (plastina 01/02/04/05/06).
 *
 *  Besh tanlov studio'da muhrlangan: Maydon, Qator, Karta, Jadval, Orol.
 *  CSS `html[data-form]` orqali farqlanadi; standart — Maydon, shuning
 *  uchun atribut yozilmaydi.
 */

export type FormVariant = "maydon" | "qator" | "karta" | "jadval" | "orol";

export const DEFAULT_FORM_VARIANT: FormVariant = "maydon";

export const FORM_VARIANTS: {
  id: FormVariant;
  labelKey: string;
  hintKey: string;
}[] = [
  {
    id: "maydon",
    labelKey: "form.style.maydon",
    hintKey: "form.style.maydonHint",
  },
  {
    id: "qator",
    labelKey: "form.style.qator",
    hintKey: "form.style.qatorHint",
  },
  {
    id: "karta",
    labelKey: "form.style.karta",
    hintKey: "form.style.kartaHint",
  },
  {
    id: "jadval",
    labelKey: "form.style.jadval",
    hintKey: "form.style.jadvalHint",
  },
  {
    id: "orol",
    labelKey: "form.style.orol",
    hintKey: "form.style.orolHint",
  },
];

export function clampFormVariant(value: unknown): FormVariant {
  return FORM_VARIANTS.some((v) => v.id === value)
    ? (value as FormVariant)
    : DEFAULT_FORM_VARIANT;
}

export function currentFormVariant(): FormVariant {
  if (typeof document === "undefined") return DEFAULT_FORM_VARIANT;
  return clampFormVariant(document.documentElement.dataset.form);
}
