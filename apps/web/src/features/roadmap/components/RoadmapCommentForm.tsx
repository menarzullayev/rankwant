"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { ApiError, postRoadmapComment } from "@/lib/api";

/** Izoh yozish formasi — faqat kirganlarga.
 *
 *  Moderatsiya KEYIN (post-moderation): izoh darhol ko'rinadi, jamoa
 *  kerak bo'lsa yashiradi. Shu sababli bu yerda "tasdiq kutilmoqda"
 *  degan holat YO'Q — u yolg'on bo'lardi.
 *
 *  Yuborilgach `router.refresh()`: izoh serverda qayta chiziladi, ya'ni
 *  ro'yxat tartibi va soni bir joyda (serverda) hisoblanadi.
 */
export function RoadmapCommentForm({ itemId }: { itemId: number }) {
  const { user, ready } = useSession();
  const locale = useLocale();
  const router = useRouter();
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Hooklar yuqorida — bu qaytish ulardan KEYIN turadi.
  if (!ready) return null;

  if (!user) {
    return (
      <p className="text-theme-sm rw-dim">
        <Link
          href={"/login?tab=login" as Route}
          className="font-medium rw-accent-ink hover:underline"
        >
          {t(locale, "roadmap.commentLogin")}
        </Link>
      </p>
    );
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (busy || body.trim() === "") return;
    setBusy(true);
    setError(null);
    try {
      await postRoadmapComment(itemId, body.trim());
      setBody("");
      router.refresh();
    } catch (caught) {
      setError(
        caught instanceof ApiError ? caught.text : t(locale, "error.error"),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-2">
      <textarea
        value={body}
        onChange={(event) => setBody(event.target.value)}
        rows={3}
        placeholder={t(locale, "roadmap.commentPlaceholder")}
        className="w-full rw-radius-sm border rw-line rw-field-bg px-3 py-2 text-theme-sm rw-strong rw-focus-line rw-placeholder rw-fm-inp"
      />
      {error && <p className="text-theme-sm rw-bad-ink">{error}</p>}
      <button
        type="submit"
        disabled={busy || body.trim() === ""}
        className="rw-radius-sm rw-accent-bg px-4 py-2 text-theme-sm font-medium disabled:opacity-60"
      >
        {busy ? t(locale, "roadmap.sending") : t(locale, "roadmap.commentSend")}
      </button>
    </form>
  );
}
