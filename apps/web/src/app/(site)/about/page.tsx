import Link from "next/link";
import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";
import { AboutJourney, SystemGuide } from "@/features/about/server";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api } from "@/lib/api";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.about") };
}

export default async function AboutPage() {
  const locale = await getLocale();
  const languages = await api.languages().catch(() => ({ results: [] as { code: string; name: string; version: string }[] }));

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <header className="space-y-2">
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "about.title")}
        </h1>
        <p className="text-theme-sm rw-dim">{t(locale, "about.lead")}</p>
      </header>

      <AboutJourney />

      <SystemGuide languages={languages.results} />

      <Card title={t(locale, "home.openRating")}>
        <p className="text-theme-sm rw-dim">
          {t(locale, "about.ratingTeaser")}{" "}
          <Link
            href="/rating"
            className="font-medium rw-accent-ink hover:underline"
          >
            {t(locale, "nav.formulas")}
          </Link>
          .
        </p>
      </Card>
    </div>
  );
}
