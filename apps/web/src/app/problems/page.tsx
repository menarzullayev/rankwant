import type { Metadata, Route } from "next";
import Link from "next/link";

import { DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { PAGE_SIZES, Pager } from "@/components/ui/Pager";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { getLocale } from "@/i18n/server";
import { t, topicName } from "@/i18n/messages";
import { BlogIcon, CheckIcon } from "@/icons";
import { ArchiveSidebar } from "@/components/ArchiveSidebar";
import { ProblemFilters } from "@/components/ProblemFilters";
import { FavouriteToggle } from "@/components/FavouriteToggle";
import { TopicBadges } from "@/components/TopicBadges";
import { VerdictBadge } from "@/components/VerdictBadge";
import {
  api,
  ApiError,
  type ArchiveProgress,
  type TopicSkill,
  type Paginated,
  type Problem,
  type Recommendation,
  type UserPublic,
} from "@/lib/api";
import { getWithSession } from "@/lib/api.server";

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "problems.title") };
}

/** URL dan API ga faqat shu kalitlar o'tadi — qolgani e'tiborsiz
 * qoldiriladi, aks holda ixtiyoriy so'rov qatori backend'ga ochilardi. */
const ALLOWED = [
  "level",
  "topics",
  "solved",
  "attempted",
  "favourite",
  "ordering",
  "search",
  "page",
  "page_size",
  "recommended",
  "statement_locale",
] as const;

const DEFAULT_PAGE_SIZE = 25; // core.pagination.StandardPagination bilan bir xil

type Props = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function ProblemsPage({ searchParams }: Props) {
  const locale = await getLocale();
  const raw = await searchParams;

  const query = new URLSearchParams();
  for (const name of ALLOWED) {
    const value = raw[name];
    if (typeof value === "string" && value) query.set(name, value);
  }

  // Sessiya bilan — `is_solved` foydalanuvchiga xos, `get()` esa
  // cookie uzatmaydi va hamma uchun `false` qaytarardi.
  const page = Math.max(1, Number(raw.page) || 1);
  const pageSize = PAGE_SIZES.includes(
    Number(raw.page_size) as (typeof PAGE_SIZES)[number],
  )
    ? Number(raw.page_size)
    : DEFAULT_PAGE_SIZE;

  const [
    data,
    topics,
    stats,
    me,
    progress,
    skills,
    roadmaps,
    calendar,
    attempts,
    popular,
  ] = await Promise.all([
    getWithSession<Paginated<Problem>>(
      `/problems/${query.size ? `?${query}` : ""}`,
    ),
    api.topics(),
    api.stats(),
    getWithSession<UserPublic>("/me/").catch(() => null),
    getWithSession<ArchiveProgress>("/problems/progress/"),
    getWithSession<{ topics: TopicSkill[] }>("/problems/skills/").catch(() => ({
      topics: [],
    })),
    api.roadmaps().catch(() => []),
    api.calendar().catch(() => ({ results: [] })),
    api.attempts().catch(() => ({ results: [] })),
    // «Ko'p ko'rilgan» — arxiv filtridan mustaqil, alohida so'rov.
    api
      .problems("?ordering=-view_count&page_size=5")
      .catch(() => ({ results: [] })),
  ]);

  // «Davom ettirish» — urinilgan, lekin yechilmagan birinchi masala.
  // Ro'yxat qiyinlik bo'yicha saralangani uchun bu eng oson qolgani.
  const resume =
    data.results.find((p) => !p.is_solved && p.my_verdict !== null) ?? null;

  const upcoming =
    calendar.results.find((event) => new Date(event.start_at) > new Date()) ??
    null;

  // Sahifa havolasi qolgan filtrlarni saqlaydi.
  const pageHref = (next: number) => {
    const params = new URLSearchParams(query);
    if (next > 1) params.set("page", String(next));
    else params.delete("page");
    return `/problems${params.size ? `?${params}` : ""}` as Route;
  };

  // Hajm o'zgarsa sahifa raqami ma'nosini yo'qotadi — boshidan.
  const sizeHref = (size: number) => {
    const params = new URLSearchParams(query);
    params.delete("page");
    if (size === DEFAULT_PAGE_SIZE) params.delete("page_size");
    else params.set("page_size", String(size));
    return `/problems${params.size ? `?${params}` : ""}` as Route;
  };

  // Tavsiya faqat kirgan foydalanuvchi uchun — chiqmasa sahifa baribir
  // ishlayveradi (arxiv hamma uchun ochiq).
  let recommended: Recommendation | null = null;
  try {
    recommended = await getWithSession<Recommendation>(
      "/problems/recommendation/",
    );
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
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "problems.title")}
        </h1>
        {me && (
          <nav className="flex flex-wrap items-center gap-4 text-theme-sm">
            <Link
              href={{ pathname: "/attempts" }}
              className="rw-accent-ink hover:underline"
            >
              Urinishlarim
            </Link>
            <Link
              href={{ pathname: `/users/${me.username}` }}
              className="rw-accent-ink hover:underline"
            >
              Statistikam
            </Link>
          </nav>
        )}
      </div>

      <ProblemFilters
        signedIn={me !== null}
        locales={stats.statement_locales}
        topics={topics.results.map((topic) => ({
          slug: topic.slug,
          label: topicName(topic, locale),
        }))}
      />

      {/* Ustun shabloni MOBILDA HAM ko'rsatiladi: `grid-cols` siz element
          yashirin `auto` trekka tushadi, u esa mazmun bo'yicha kengayadi va
          `min-w-0` yordam bermaydi — keng bo'lgani TREK. O'lchandi: 412 px
          li telefonda arxiv 629 px bo'lib, yon tomonga siljirdi. */}
      <div className="grid grid-cols-[minmax(0,1fr)] items-start gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,300px)]">
        <Card bodyClassName="p-0">
          <Table>
            <THead>
              <TH>#</TH>
              <TH>{t(locale, "problems.name")}</TH>
              <TH>{t(locale, "problems.difficulty")}</TH>
              {/* Statistika ustunlari tor ekranda yig'iladi — nom, raqam va
                qiyinlik telefonda ham ko'rinib turishi kerak. */}
              <TH align="center" className="hidden md:table-cell">
                ★
              </TH>
              <TH align="right" className="hidden sm:table-cell">
                {t(locale, "problems.solved")}
              </TH>
              <TH align="right" className="hidden lg:table-cell">
                %
              </TH>
              {me && (
                <TH align="center">
                  <span className="sr-only">Sevimlilar</span>☆
                </TH>
              )}
            </THead>
            <TBody>
              {data.results.map((p) => (
                <TR key={p.slug}>
                  <TD className="rw-faint">
                    <span className="font-mono text-theme-xs tabular-nums">
                      {p.code === null
                        ? "—"
                        : `#${String(p.code).padStart(4, "0")}`}
                    </span>
                  </TD>
                  <TD>
                    <div className="flex items-center gap-1.5">
                      {/* Yechilganini bir qarashda ko'rish arxivning eng ko'p
                        ishlatiladigan belgisi — uchala platformada ham bor. */}
                      {p.is_solved && (
                        <span
                          title={t(locale, "problems.solvedByYou")}
                          aria-label={t(locale, "problems.solvedByYou")}
                          role="img"
                          className="inline-flex shrink-0"
                        >
                          <CheckIcon className="size-4 rw-ok-ink" />
                        </span>
                      )}
                      <Link
                        href={`/problems/${p.slug}`}
                        className="font-medium rw-strong rw-link-hover"
                      >
                        {p.title}
                      </Link>
                      {p.has_editorial && (
                        <span
                          title="Yechim tahlili bor"
                          aria-label="Yechim tahlili bor"
                          role="img"
                          className="inline-flex shrink-0 rw-faint"
                        >
                          <BlogIcon className="size-3.5" />
                        </span>
                      )}
                      {/* Testsiz masala — yuborib bo'lmaydi. Ro'yxatda
                          ko'rsatiladi, aks holda foydalanuvchi ochib,
                          qaytib chiqishga vaqt sarflardi. */}
                      {!p.has_tests && (
                        <span
                          title="Testlar tayyorlanmagan — yechim qabul qilinmaydi"
                          className="shrink-0 rw-radius-sm rw-warn-soft px-1.5 py-0.5 text-theme-xs rw-warn-ink"
                        >
                          testsiz
                        </span>
                      )}
                      {/* Yechilmagan, lekin urinilgan — «WA oldim» signali */}
                      {!p.is_solved && p.my_verdict && (
                        <VerdictBadge verdict={p.my_verdict} locale={locale} />
                      )}
                    </div>
                    <TopicBadges topics={p.topics} solved={p.is_solved} />
                  </TD>
                  <TD>
                    <div className="flex items-center gap-2">
                      <DifficultyBadge value={p.difficulty} />
                      <span className={`level-${p.level} text-theme-xs`}>
                        {p.level_label}
                      </span>
                    </div>
                  </TD>
                  <TD align="center" className="hidden md:table-cell">
                    {p.rating.average === null ? (
                      <span className="rw-faint">—</span>
                    ) : (
                      <span
                        className="text-theme-xs rw-dim-2 tabular-nums"
                        title={`${p.rating.count} baho`}
                      >
                        {p.rating.average.toFixed(1)}
                      </span>
                    )}
                  </TD>
                  <TD
                    align="right"
                    className="hidden rw-faint tabular-nums sm:table-cell"
                  >
                    {p.solved_count}
                  </TD>
                  <TD
                    align="right"
                    className="hidden rw-faint tabular-nums lg:table-cell"
                  >
                    {p.success_rate === null ? "—" : `${p.success_rate}%`}
                  </TD>
                  {me && (
                    <TD align="center">
                      <FavouriteToggle
                        slug={p.slug}
                        initial={p.is_favourite}
                        title={p.title}
                      />
                    </TD>
                  )}
                </TR>
              ))}
              {data.count === 0 && (
                <EmptyRow colSpan={me ? 7 : 6}>{t(locale, "empty")}</EmptyRow>
              )}
            </TBody>
          </Table>

          <Pager
            page={page}
            count={data.count}
            pageSize={pageSize}
            href={pageHref}
            sizeHref={sizeHref}
            label="masala"
          />
        </Card>

        <ArchiveSidebar
          locale={locale}
          progress={progress}
          skills={skills.topics}
          recommended={recommended}
          resume={resume}
          upcoming={upcoming}
          roadmaps={roadmaps}
          attempts={attempts.results}
          popular={popular.results}
        />
      </div>
    </div>
  );
}
