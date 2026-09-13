"use client";

import type { Route } from "next";
import { useState } from "react";

import { Markdown } from "@/components/Markdown";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { ApiError, unlockEditorial, type EditorialState } from "@/lib/api";
import Link from "next/link";

/** Yechim tahlili — ADR-0013 spoyler darvozasi.
 *
 * Masalani yechgan odam bepul ko'radi; yechmagani Qvant sarflaydi.
 * Bu paywall emas: bepul yo'l — masalani yechish — har doim ochiq, va
 * u asosiy yo'l. Qvant faqat sabrsizlikni sotib oladi. */
export function Editorial({
  slug,
  text,
  state,
}: {
  slug: string;
  text: string;
  state: EditorialState;
}) {
  const { user, ready } = useSession();
  const [open, setOpen] = useState(false);
  const [body, setBody] = useState(text);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function unlock() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const result = await unlockEditorial(slug);
      setBody(result.editorial);
      setOpen(true);
    } catch (caught) {
      setError(
        caught instanceof ApiError && caught.status === 402
          ? `Balans yetarli emas — ${state.price} Qvant kerak`
          : "Ochib bo'lmadi, qaytadan urinib ko'ring",
      );
    } finally {
      setBusy(false);
    }
  }

  if (!ready) return null;

  if (!user) {
    return (
      <Card title="Yechim tahlili">
        <p className="text-theme-sm rw-faint">
          Tahlil hisobga kirgan foydalanuvchilar uchun.{" "}
          <Link href={"/login?tab=login" as Route} className="underline rw-accent-ink">
            Kirish
          </Link>
        </p>
      </Card>
    );
  }

  if (!body) {
    return (
      <Card title="Yechim tahlili">
        <div className="space-y-3">
          <p className="text-theme-sm rw-faint">
            Masalani yechsangiz tahlil <strong>bepul</strong> ochiladi — va
            o&apos;shanda undan haqiqiy foyda bo&apos;ladi. Hoziroq
            ko&apos;rmoqchi bo&apos;lsangiz {state.price} Qvant.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="outline" onClick={unlock} disabled={busy}>
              {busy ? "Ochilmoqda…" : `Ochish — ${state.price} Qvant`}
            </Button>
            {error && <span className="text-theme-sm rw-bad-ink">{error}</span>}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card
      title="Yechim tahlili"
      action={
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          className="rw-radius-sm px-2.5 py-1 text-theme-sm font-medium rw-accent-ink transition rw-hover-accent"
        >
          {open ? "Yashirish" : "Ko'rsatish"}
        </button>
      }
    >
      {open ? (
        <Markdown>{body}</Markdown>
      ) : (
        <p className="text-theme-sm rw-faint">
          {state.access === "solved"
            ? "Masalani yechdingiz — tahlil ochiq."
            : "Tahlil ochiq."}{" "}
          O&apos;zingiz urinib ko&apos;rgach oching.
        </p>
      )}
    </Card>
  );
}
