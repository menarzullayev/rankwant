"use client";

import { useCallback, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t, type Locale } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

/** Serverning aniq sababi («Bu username band») bo'lsa — shuni qaytaradi,
 *  aks holda xato kodining tarjimasi. Umumiy «ma'lumot noto'g'ri» odamga
 *  qaysi maydonni tuzatishni aytmasdi. */
export function describeError(locale: Locale, err: unknown): string {
  if (err instanceof ApiError) {
    return err.code === "invalid"
      ? err.text
      : errorText(locale, err.code, err.text);
  }
  return t(locale, "error.error");
}

/** Bitta amalning holati: kutish, xato va «saqlandi».
 *
 *  Ilgari `features/account/components/section-kit.tsx` ichida edi —
 *  ya'ni boshqa feature'lar sozlamalar bo'limidan import qilishga majbur
 *  edi. Umumiy hook umumiy qatlamda turishi kerak (25-prinsip: layer
 *  qoidasi, pastga qarab oqim). */
export function useAction() {
  const locale = useLocale();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  const run = useCallback(
    async (action: () => Promise<unknown>) => {
      setBusy(true);
      setError("");
      setDone(false);
      try {
        await action();
        setDone(true);
        return true;
      } catch (err) {
        setError(describeError(locale, err));
        return false;
      } finally {
        setBusy(false);
      }
    },
    [locale],
  );

  return { busy, error, done, run, setError };
}
