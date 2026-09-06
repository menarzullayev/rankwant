import Link from "next/link";
import type { Metadata } from "next";
import { api, ApiError, type Recommendation } from "@/lib/api";
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

  // Tavsiya faqat kirgan foydalanuvchi uchun — chiqmasa sahifa baribir
  // ishlayveradi (arxiv hamma uchun ochiq).
  let recommended: Recommendation | null = null;
  try {
    recommended = await api.recommendations();
  } catch (error) {
    if (!(error instanceof ApiError) || (error.status !== 401 && error.status !== 403)) {
      throw error;
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">{t(locale, "problems.title")}</h1>

      {recommended && recommended.results.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-1 text-lg font-medium">{t(locale, "recommend.title")}</h2>
          <p className="mb-3 text-xs" style={{ color: "var(--muted)" }}>
            {t(locale, "recommend.target")}: {recommended.target_difficulty}
          </p>
          <div className="flex flex-wrap gap-2">
            {recommended.results.slice(0, 6).map((p) => (
              <Link
                key={p.slug}
                href={`/problems/${p.slug}`}
                className={`rounded border px-3 py-1 text-sm level-${p.level}`}
                style={{ borderColor: "var(--border)", background: "var(--surface)" }}
              >
                {p.title}
              </Link>
            ))}
          </div>
        </section>
      )}
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
