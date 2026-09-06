import Link from "next/link";
import type { Metadata } from "next";
import { api } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Masalalar" };

export default async function ProblemsPage() {
  const locale = DEFAULT_LOCALE;
  const data = await api.problems();

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">{t(locale, "problems.title")}</h1>
      <table className="w-full text-sm">
        <thead>
          <tr style={{ color: "var(--muted)" }} className="text-left">
            <th className="pb-2">#</th>
            <th className="pb-2">{t(locale, "problems.title")}</th>
            <th className="pb-2">{t(locale, "problems.difficulty")}</th>
            <th className="pb-2 text-right">{t(locale, "problems.solved")}</th>
          </tr>
        </thead>
        <tbody>
          {data.results.map((p, i) => (
            <tr key={p.slug} className="border-t" style={{ borderColor: "var(--border)" }}>
              <td className="py-2" style={{ color: "var(--muted)" }}>{i + 1}</td>
              <td className="py-2">
                <Link href={`/problems/${p.slug}`} className="hover:underline">
                  {p.title}
                </Link>
                <span className="ml-2 text-xs" style={{ color: "var(--muted)" }}>
                  {p.topics.join(", ")}
                </span>
              </td>
              <td className={`py-2 level-${p.level}`}>{p.level_label}</td>
              <td className="py-2 text-right" style={{ color: "var(--muted)" }}>
                {p.solved_count}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.count === 0 && <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>}
    </div>
  );
}
