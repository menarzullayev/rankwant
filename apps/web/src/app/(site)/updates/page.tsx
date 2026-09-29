import type { Metadata, Route } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { Card } from "@/components/ui/Card";
import { PAGE_SIZES, Pager } from "@/components/ui/Pager";
import {
  UpdateKindBadge,
  UpdateModuleBadge,
  kindClass,
} from "@/features/updates";
import { excerpt } from "@/components/ui/Markdown";
import { getLocale } from "@/i18n/server";
import { date, t, type Locale } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import {
  api,
  ApiError,
  UPDATE_KINDS,
  type SystemUpdate,
  type UpdateKind,
} from "@/lib/api";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return {
    title: t(locale, "update.title"),
    description: t(locale, "update.lead"),
  };
}

/** URL dan API ga faqat shu kalitlar o'tadi — ixtiyoriy so'rov qatori
 *  backend'ga ochilib ketmasin (`problems` sahifasidagi bilan bir xil). */
const ALLOWED = ["kind", "page", "page_size"] as const;

function isKind(value: string): value is UpdateKind {
  return (UPDATE_KINDS as string[]).includes(value);
}

/** Bitta yozuv qatori — arxivda ham, "diqqat" blokida ham shu. */
function UpdateRow({
  row,
  locale,
}: {
  row: SystemUpdate;
  locale: Locale;
}) {
  return (
    <Link
      href={`/updates/${row.id}`}
      className="block px-5 py-4 transition rw-hover-bg"
    >
      <span className="flex flex-wrap items-center gap-2">
        <UpdateKindBadge kind={row.kind} locale={locale} />
        <UpdateModuleBadge module={row.module} locale={locale} />
        {row.version && (
          <span className="text-theme-xs tabular-nums rw-faint">
            {row.version}
          </span>
        )}
      </span>
      <span className="mt-2 block font-medium rw-strong">{row.title}</span>
      {row.body && (
        <span className="mt-1 block text-theme-sm rw-dim">
          {excerpt(row.body, 150)}
        </span>
      )}
    </Link>
  );
}

type Props = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function UpdatesPage({ searchParams }: Props) {
  const locale = await getLocale();
  const raw = await searchParams;

  const query = new URLSearchParams();
  for (const name of ALLOWED) {
    const value = raw[name];
    if (typeof value === "string" && value) query.set(name, value);
  }

  const kindRaw = typeof raw.kind === "string" ? raw.kind : "";
  const kind = isKind(kindRaw) ? kindRaw : "";
  const page = Math.max(1, Number(raw.page) || 1);
  const sizeRaw = Number(raw.page_size);
  const pageSize = (PAGE_SIZES as readonly number[]).includes(sizeRaw)
    ? sizeRaw
    : PAGE_SIZES[0];

  // Ikki mustaqil so'rov — ketma-ket kutish sahifani sekinlashtiradi.
  const [data, actionable] = await Promise.all([
    api.updates(query.size ? `?${query}` : "").catch(
      (error: unknown): { count: number; results: SystemUpdate[] } | null => {
        // Sahifa raqami oraliqdan chiqsa DRF 404 beradi (masalan filtr
        // o'zgargandan keyin eski havola qolgan bo'lsa). Bo'sh sahifa
        // ko'rsatish ham, "yuklab bo'lmadi" deyish ham noto'g'ri —
        // filtrni saqlab 1-sahifaga qaytaramiz.
        if (error instanceof ApiError && error.status === 404 && page > 1) {
          redirect(
            `/updates${kind ? `?kind=${encodeURIComponent(kind)}` : ""}` as Route,
          );
        }
        if (!(error instanceof ApiError)) throw error;
        return null;
      },
    ),
    api.updatesActionable().catch((): SystemUpdate[] => []),
  ]);

  if (data === null) {
    return (
      <div className="space-y-6">
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "update.title")}
        </h1>
        <Card>
          <p className="text-theme-sm rw-dim">{t(locale, "update.unavailable")}</p>
        </Card>
      </div>
    );
  }

  /** Kun bo'yicha guruh. API `-released_at` bo'yicha saralaydi, ya'ni bir
   *  kunning yozuvlari ketma-ket keladi — qayta saralash kerak emas. */
  const days: { day: string; rows: SystemUpdate[] }[] = [];
  for (const row of data.results) {
    const last = days[days.length - 1];
    if (last && last.day === row.released_at) last.rows.push(row);
    else days.push({ day: row.released_at, rows: [row] });
  }

  /** Filtr havolasi — `page` tashlanadi (yangi filtrda 1-sahifa kerak),
   *  `page_size` saqlanadi (odam tanlovi filtrdan ustun). */
  const kindHref = (value: UpdateKind | ""): Route => {
    const params = new URLSearchParams();
    if (value) params.set("kind", value);
    if (pageSize !== PAGE_SIZES[0]) params.set("page_size", String(pageSize));
    return `/updates${params.size ? `?${params}` : ""}` as Route;
  };

  const pageHref = (target: number): Route => {
    const params = new URLSearchParams(query);
    if (target > 1) params.set("page", String(target));
    else params.delete("page");
    return `/updates${params.size ? `?${params}` : ""}` as Route;
  };

  // Hajm o'zgarsa sahifa raqami ma'nosini yo'qotadi — boshidan. Aks holda
  // 3-sahifada turib 100 taga o'tilsa DRF "Invalid page" bilan 404 beradi.
  const sizeHref = (size: number): Route => {
    const params = new URLSearchParams(query);
    params.delete("page");
    if (size === PAGE_SIZES[0]) params.delete("page_size");
    else params.set("page_size", String(size));
    return `/updates${params.size ? `?${params}` : ""}` as Route;
  };

  const chip = "rounded-full px-3 py-1.5 text-theme-xs font-medium transition";

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "update.title")}
        </h1>
        <p className="max-w-3xl text-theme-sm rw-dim">
          {t(locale, "update.lead")}
        </p>
      </header>

      {/* Qaror 11: `breaking`/`deprecated` harakatga chaqiradi, ya'ni ular
          RANGDA ham, JOYLASHUVDA ham ajralib turishi shart. Bu — joylashuv. */}
      {actionable.length > 0 && (
        <section className="rw-panel p-5">
          <h2 className="flex items-center gap-2 text-theme-xl font-semibold rw-strong">
            <span className="inline-flex size-8 shrink-0 items-center justify-center rounded-full rw-kind-breaking">
              <Icon name="status.warning" className="size-4" />
            </span>
            {t(locale, "update.actionable")}
          </h2>
          <p className="mt-2 text-theme-sm rw-dim">
            {t(locale, "update.actionableHint")}
          </p>
          <ul className="mt-4 divide-y rw-divide">
            {actionable.map((row) => (
              <li key={row.id}>
                <UpdateRow row={row} locale={locale} />
              </li>
            ))}
          </ul>
        </section>
      )}

      <nav
        aria-label={t(locale, "update.filterLabel")}
        className="flex flex-wrap items-center gap-2"
      >
        <Link
          href={kindHref("")}
          aria-current={kind === "" ? "true" : undefined}
          className={`${chip} ${kind === "" ? "rw-accent-bg" : "rw-chip rw-dim-2 rw-hover-bg"}`}
        >
          {t(locale, "update.filterAll")}
        </Link>
        {UPDATE_KINDS.map((value) => (
          <Link
            key={value}
            href={kindHref(value)}
            aria-current={kind === value ? "true" : undefined}
            className={
              kind === value
                ? `${kindClass(value)} ${chip}`
                : `${chip} rw-chip rw-dim-2 rw-hover-bg`
            }
          >
            {t(locale, `update.kind.${value}`)}
          </Link>
        ))}
      </nav>

      {data.count === 0 ? (
        <Card>
          <p className="text-theme-sm rw-dim">{t(locale, "common.empty")}</p>
        </Card>
      ) : (
        days.map((group) => (
          <section key={group.day} className="space-y-3">
            <h2 className="text-theme-sm font-semibold rw-dim-2">
              {date(group.day, locale)}
            </h2>
            <Card bodyClassName="p-0">
              <ul className="divide-y rw-divide">
                {group.rows.map((row) => (
                  <li key={row.id}>
                    <UpdateRow row={row} locale={locale} />
                  </li>
                ))}
              </ul>
            </Card>
          </section>
        ))
      )}

      <Card bodyClassName="p-0">
        <Pager
          locale={locale}
          page={page}
          count={data.count}
          pageSize={pageSize}
          href={pageHref}
          sizeHref={sizeHref}
          label={t(locale, "update.entry")}
        />
      </Card>
    </div>
  );
}
