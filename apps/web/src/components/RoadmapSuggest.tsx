"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { ApiError, suggestRoadmapItem } from "@/lib/api";

/** Taklif formasi — faqat kirganlarga.
 *
 *  Taklif darhol ochiq ro'yxatda "Ko'rib chiqilmoqda" holatida ko'rinadi
 *  (qaror shunday). Shu sababli forma ostida buni OSHKOR aytadigan izoh
 *  bor: odam nima yozayotganini va u kimga ko'rinishini bilishi kerak.
 *
 *  Muvaffaqiyatdan keyin `router.refresh()` — yangi band server
 *  komponentida qayta chiziladi. Ro'yxatni brauzerda qo'lda qo'shish
 *  o'rniga shu yo'l tanlandi: tartib va hisoblar (ovoz, izoh soni)
 *  serverda bir joyda hisoblanadi.
 */
export function RoadmapSuggest() {
  const { user, ready } = useSession();
  const locale = useLocale();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Hooklar yuqorida — bu qaytish ulardan KEYIN turadi.
  if (!ready || !user) return null;

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      await suggestRoadmapItem(title.trim(), body.trim());
      setTitle("");
      setBody("");
      setOpen(false);
      router.refresh();
    } catch (caught) {
      // API maydon xatosi bo'lsa uning matni ko'rsatiladi (`ApiError.text`),
      // aks holda umumiy xabar — bo'sh ekran qoldirmaymiz.
      setError(
        caught instanceof ApiError
          ? caught.text
          : t(locale, "error.error"),
      );
    } finally {
      setBusy(false);
    }
  }

  const field =
    "w-full rw-radius-sm border rw-line rw-field-bg px-3 py-2 text-theme-sm rw-strong rw-focus-line";

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rw-radius-sm rw-accent-bg px-4 py-2 text-theme-sm font-medium"
      >
        {t(locale, "roadmap.suggest")}
      </button>
    );
  }

  return (
    <form onSubmit={submit} className="rw-panel w-full space-y-3 p-5">
      <h2 className="text-theme-xl font-semibold rw-strong">
        {t(locale, "roadmap.suggest")}
      </h2>

      <label className="block">
        <span className="mb-1 block text-theme-sm rw-dim">
          {t(locale, "roadmap.suggestTitle")}
        </span>
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          maxLength={200}
          required
          className={field}
        />
      </label>

      <label className="block">
        <span className="mb-1 block text-theme-sm rw-dim">
          {t(locale, "roadmap.suggestBody")}
        </span>
        <textarea
          value={body}
          onChange={(event) => setBody(event.target.value)}
          rows={4}
          className={field}
        />
      </label>

      <p className="text-theme-xs rw-faint">{t(locale, "roadmap.suggestHint")}</p>

      {error && <p className="text-theme-sm rw-bad-ink">{error}</p>}

      <div className="flex flex-wrap gap-3">
        <button
          type="submit"
          disabled={busy || title.trim() === ""}
          className="rw-radius-sm rw-accent-bg px-4 py-2 text-theme-sm font-medium disabled:opacity-60"
        >
          {busy ? t(locale, "roadmap.sending") : t(locale, "roadmap.suggestSend")}
        </button>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="rw-radius-sm border rw-line px-4 py-2 text-theme-sm rw-dim-2 transition rw-hover-bg"
        >
          {t(locale, "roadmap.suggestCancel")}
        </button>
      </div>
    </form>
  );
}
