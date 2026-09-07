import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = { title: "Jamoa" };

export default function TeamPage() {
  const locale = DEFAULT_LOCALE;
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
        {t(locale, "team.title")}
      </h1>
      <Card>
        <p className="text-theme-sm rw-dim">
          RankWant — O&apos;zbekiston va dunyo uchun sport dasturlash
          platformasi. Ochiq reyting, o&apos;z judge, o&apos;z kontent. Loyiha
          hozir ochiq preview bosqichida.
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
