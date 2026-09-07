import type { Metadata } from "next";

import { DuelActions } from "@/components/DuelActions";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Duel" };

export default async function DuelsPage() {
  const locale = DEFAULT_LOCALE;
  const waiting = await api.duels();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.duels")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">
          Chaqiriq tashlang, kimdir qabul qiladi, belgilangan vaqtda bir xil
          masalalarni yechasiz. G&apos;olib Challenges reytingida Elo oladi.
        </p>
      </header>
      <DuelActions waiting={waiting.results} />
    </div>
  );
}
