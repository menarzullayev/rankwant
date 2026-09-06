import Link from "next/link";
import type { Metadata } from "next";
import { api } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Musobaqalar" };

function statusKey(c: { is_running: boolean; is_finished: boolean }): string {
  if (c.is_running) return "contests.running";
  return c.is_finished ? "contests.finished" : "contests.upcoming";
}

export default async function ContestsPage() {
  const locale = DEFAULT_LOCALE;
  const data = await api.contests();

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">{t(locale, "contests.title")}</h1>
      <ul className="space-y-3">
        {data.results.map((c) => (
          <li
            key={c.slug}
            className="rounded-lg border p-4"
            style={{ borderColor: "var(--border)", background: "var(--surface)" }}
          >
            <Link href={`/contests/${c.slug}`} className="font-medium hover:underline">
              {c.title}
            </Link>
            <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
              {t(locale, statusKey(c))}
              {c.is_rated && ` · ${t(locale, "contests.rated")}`}
              {" · "}
              {new Date(c.start_at).toLocaleString(locale)}
            </p>
          </li>
        ))}
      </ul>
      {data.count === 0 && <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>}
    </div>
  );
}
