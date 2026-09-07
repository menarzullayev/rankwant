import Link from "next/link";
import type { Metadata } from "next";

import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { api, ApiError, type Recommendation } from "@/lib/api";

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
    if (
      !(error instanceof ApiError) ||
      (error.status !== 401 && error.status !== 403)
    ) {
      throw error;
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
        {t(locale, "problems.title")}
      </h1>

      {recommended && recommended.results.length > 0 && (
        <Card
          title={t(locale, "recommend.title")}
          action={
            <Badge color="brand">
              {t(locale, "recommend.target")}: {recommended.target_difficulty}
            </Badge>
          }
        >
          <div className="flex flex-wrap gap-2">
            {recommended.results.slice(0, 6).map((p) => (
              <Link
                key={p.slug}
                href={`/problems/${p.slug}`}
                className={`level-${p.level} rw-radius-sm border rw-line px-3 py-1.5
 text-theme-sm font-medium transition rw-hover-line
 `}
              >
                {p.title}
              </Link>
            ))}
          </div>
        </Card>
      )}

      <Card bodyClassName="p-0">
        <Table>
          <THead>
            <TH>#</TH>
            <TH>{t(locale, "problems.name")}</TH>
            <TH>{t(locale, "problems.difficulty")}</TH>
            <TH align="right">{t(locale, "problems.solved")}</TH>
          </THead>
          <TBody>
            {data.results.map((p, i) => (
              <TR key={p.slug}>
                <TD className="rw-faint">{i + 1}</TD>
                <TD>
                  <Link
                    href={`/problems/${p.slug}`}
                    className="font-medium rw-strong rw-link-hover"
                  >
                    {p.title}
                  </Link>
                  {p.topics.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {p.topics.map((topic) => (
                        <Badge key={topic}>{topic}</Badge>
                      ))}
                    </div>
                  )}
                </TD>
                <TD>
                  <div className="flex items-center gap-2">
                    <DifficultyBadge value={p.difficulty} />
                    <span className={`level-${p.level} text-theme-xs`}>
                      {p.level_label}
                    </span>
                  </div>
                </TD>
                <TD align="right" className="rw-faint">
                  {p.solved_count}
                </TD>
              </TR>
            ))}
            {data.count === 0 && (
              <EmptyRow colSpan={4}>{t(locale, "empty")}</EmptyRow>
            )}
          </TBody>
        </Table>
      </Card>
    </div>
  );
}
