import type { Route } from "next";
import Link from "next/link";

import { Card } from "@/components/ui/Card";
import { fill, t, type Locale } from "@/i18n/messages";
import type { Certificate, Paginated } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { formatDate } from "@rankwant/shared/format";
import { MedalDot } from "./Medal";
import { SectionHint } from "./SectionHint";

/** Daraja rangi faqat chegarada (bezak) — matn standart tokenlarda qoladi. */
const TIER_CLASS: Record<Certificate["tier"], string> = {
  gold: "rw-cert-gold",
  silver: "rw-cert-silver",
  bronze: "rw-cert-bronze",
  top10: "rw-cert-top10",
  participant: "rw-cert-participant",
};

function TierDot({ tier }: { tier: Certificate["tier"] }) {
  if (tier === "gold" || tier === "silver" || tier === "bronze") return <MedalDot tier={tier} />;
  return (
    <span
      aria-hidden="true"
      className={`inline-block size-4 shrink-0 rounded-full ${tier === "top10" ? "rw-accent-soft border-2 border-[var(--rw-accent)]" : "rw-medal-none"}`}
    />
  );
}

export function CertificateCard({
  cert,
  locale,
  withName = false,
}: {
  cert: Certificate;
  locale: Locale;
  withName?: boolean;
}) {
  return (
    <article className={`rw-radius border-2 rw-surface p-5 ${TIER_CLASS[cert.tier]}`}>
      <p className="flex items-center gap-2 text-theme-xs font-semibold uppercase tracking-wide rw-dim">
        <TierDot tier={cert.tier} />
        {t(locale, `cert.tier.${cert.tier}`)}
      </p>
      {withName && <p className="mt-3 text-title-sm font-bold rw-strong">{cert.name}</p>}
      <h3 className="mt-2 text-theme-xl font-semibold rw-strong">{cert.contest.title}</h3>
      <p className="mt-1 text-theme-sm rw-dim">
        {fill(t(locale, "cert.place"), { place: cert.place, total: cert.participants })} ·{" "}
        {formatDate(cert.contest.end_at, locale)}
      </p>
      <p className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-theme-sm">
        {!withName && (
          <Link href={`/certificates/${cert.id}` as Route} className="rw-accent-ink hover:underline">
            {t(locale, "cert.verify")}
          </Link>
        )}
        <a
          href={`/api/v1/certificates/${cert.id}/pdf/`}
          target="_blank"
          rel="noopener"
          className="rw-accent-ink hover:underline"
        >
          PDF
        </a>
      </p>
    </article>
  );
}

/** Profildagi «Sertifikatlar» tabi (ADR-0019). */
export async function CertificatesTab({
  username,
  page,
  locale,
}: {
  username: string;
  page: number;
  locale: Locale;
}) {
  const data = await getWithSession<Paginated<Certificate>>(
    `/users/${username}/certificates/?page=${page}`,
  );
  const link = (to: number) => `/users/${username}/certificates?page=${to}` as Route;

  return (
    <section className="space-y-4">
      <SectionHint>{t(locale, "profile.certificatesHint")}</SectionHint>
      {data.results.length === 0 ? (
        <Card>
          <p className="text-theme-sm rw-faint">{t(locale, "profile.certificatesEmpty")}</p>
        </Card>
      ) : (
        <ul className="grid gap-4 md:grid-cols-2">
          {data.results.map((cert) => (
            <li key={cert.id}>
              <CertificateCard cert={cert} locale={locale} />
            </li>
          ))}
        </ul>
      )}
      {(data.previous || data.next) && (
        <div className="flex justify-between text-theme-sm">
          {data.previous ? (
            <Link href={link(page - 1)} className="rw-accent-ink hover:underline">
              ← {t(locale, "profile.prev")}
            </Link>
          ) : (
            <span />
          )}
          {data.next && (
            <Link href={link(page + 1)} className="rw-accent-ink hover:underline">
              {t(locale, "profile.next")} →
            </Link>
          )}
        </div>
      )}
    </section>
  );
}
