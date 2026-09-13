"use client";

import type { Route } from "next";
import Link from "next/link";
import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { ArrowUpIcon } from "@/icons";
import { voteRoadmap } from "@/lib/api";

/** Ovoz tugmasi.
 *
 *  OPTIMISTIK: bosilganda son darhol o'zgaradi, xato bo'lsa qaytariladi.
 *  Sabab — tarmoq kutish sezilarli, ovoz berish esa qaytarib bo'lmaydigan
 *  amal emas, ya'ni xato holatida holatni tiklash arzon.
 *
 *  Serverdan kelgan yakuniy son (`vote_count`) baribir qo'llanadi: boshqa
 *  odam ayni paytda ovoz bergan bo'lsa, taxminiy son noto'g'ri bo'lardi.
 *
 *  MEHMON uchun tugma emas, kirish havolasi: mehmonda hisob yo'q, ya'ni
 *  "bir odam bir ovoz" qoidasini ushlab bo'lmaydi (backend ham 401 beradi).
 */
export function RoadmapVote({
  id,
  initialVoted,
  initialCount,
  compact = false,
}: {
  id: number;
  initialVoted: boolean;
  initialCount: number;
  /** `true` — kanban kartasi uchun kichik ustun ko'rinishi. */
  compact?: boolean;
}) {
  const { user, ready } = useSession();
  const locale = useLocale();
  const [voted, setVoted] = useState(initialVoted);
  const [count, setCount] = useState(initialCount);
  const [busy, setBusy] = useState(false);

  // Sessiya aniqlanmaguncha joy band qilib turamiz — tugma "Kirish" dan
  // "Ovoz" ga sakrashi chalg'itadi.
  if (!ready) {
    return (
      <span
        aria-hidden="true"
        className={compact ? "h-12 w-11" : "h-12 w-32"}
      />
    );
  }

  if (!user) {
    return (
      <Link
        href={"/login?tab=login" as Route}
        title={t(locale, "roadmap.voteLogin")}
        aria-label={t(locale, "roadmap.voteLogin")}
        className={`flex items-center justify-center gap-1 rw-radius-sm border rw-line rw-dim-2 transition rw-hover-bg ${
          compact ? "flex-col px-2.5 py-1.5 text-theme-xs font-semibold" : "px-4 py-3 text-theme-sm"
        }`}
      >
        <ArrowUpIcon className={compact ? "size-4" : "size-5"} />
        {count}
        {!compact && <span>{t(locale, "roadmap.vote")}</span>}
      </Link>
    );
  }

  async function toggle() {
    if (busy) return;
    const next = !voted;
    setVoted(next);
    setCount((value) => value + (next ? 1 : -1));
    setBusy(true);
    try {
      const body = await voteRoadmap(id, next);
      setVoted(body.voted);
      setCount(body.vote_count);
    } catch {
      // Xato — ko'rinishni orqaga qaytaramiz.
      setVoted(!next);
      setCount((value) => value + (next ? -1 : 1));
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      onClick={() => void toggle()}
      aria-pressed={voted}
      aria-label={t(locale, "roadmap.vote")}
      title={voted ? t(locale, "roadmap.voted") : t(locale, "roadmap.vote")}
      className={`flex items-center justify-center gap-1 rw-radius-sm border transition ${
        voted
          ? "rw-accent-soft rw-accent-line"
          : "rw-line rw-dim-2 rw-hover-bg"
      } ${compact ? "flex-col px-2.5 py-1.5 text-theme-xs font-semibold" : "px-4 py-3 text-theme-sm font-medium"}`}
    >
      <ArrowUpIcon className={compact ? "size-4" : "size-5"} />
      {count}
      {!compact && (
        <span>{t(locale, voted ? "roadmap.voted" : "roadmap.vote")}</span>
      )}
    </button>
  );
}
