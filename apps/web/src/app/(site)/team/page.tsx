import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "team.title") };
}

export default async function TeamPage() {
  const locale = await getLocale();
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
        {t(locale, "team.title")}
      </h1>
      <Card>
        <p className="text-theme-sm rw-dim">{t(locale, "team.intro")}
        </p>
        <p className="mt-3 text-theme-sm rw-dim">
          Bog&apos;lanish:{" "}
          <a
            href="https://github.com/menarzullayev/rankwant"
            className="rw-accent-ink hover:underline"
          >
            github.com/menarzullayev/rankwant
          </a>
        </p>
      </Card>
    </div>
  );
}
