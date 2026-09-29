import type { Metadata } from "next";

import { DuelActions } from "@/features/duels";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.duels") };
}

export default async function DuelsPage() {
  const locale = await getLocale();
  const waiting = await api.duels();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.duels")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">{t(locale, "duels.intro")}
        </p>
      </header>
      <DuelActions waiting={waiting.results} />
    </div>
  );
}
