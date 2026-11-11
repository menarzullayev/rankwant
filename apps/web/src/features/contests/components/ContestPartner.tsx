import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Markdown } from "@/components/ui/Markdown";
import { dateTime, t, type Locale, type MessageKey } from "@/i18n/messages";

import type { ContestDetail } from "../api/contests";

const LINK = "font-medium rw-accent-ink hover:underline";

/** What the contest officially is and what it mirrors (ADR-0063), said
 *  above everything else: it changes how the reader takes the results. */
export function ContestStatus({ contest, locale }: { contest: ContestDetail; locale: Locale }) {
  // `?? null` / `?? []`: a response cached before these fields existed
  // (the web can start before the API during a deploy) must not crash the page.
  const source = contest.mirror_source ?? null;
  if (!contest.official_title && !source) return null;
  return (
    <div className="space-y-2" data-contest-status="">
      {contest.official_title && (
        <p className="rw-radius-sm border rw-line rw-surface px-3 py-2 text-theme-sm" data-official="">
          <Badge color="success">{t(locale, "contests.official")}</Badge>{" "}
          <span className="rw-strong">{contest.official_title}</span>
          {contest.official_url && (
            <>
              {" · "}
              <a href={contest.official_url} target="_blank" rel="noopener noreferrer" className={LINK}>
                {t(locale, "contest.official.document")}
                <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
              </a>
            </>
          )}
        </p>
      )}
      {source && (
        <p className="rw-radius-sm border rw-line rw-surface px-3 py-2 text-theme-sm" data-mirror-of={source.kind}>
          <Badge color="info">{t(locale, "contests.mirror")}</Badge>{" "}
          {t(locale, "contest.mirror.of")}{" "}
          <Link
            href={source.kind === "contest" ? `/contests/${source.slug}` : `/olympiads/${source.slug}`}
            className={LINK}
          >
            {source.title}
          </Link>
          . {t(locale, "contest.mirror.unrated")}
        </p>
      )}
    </div>
  );
}

/** The partner, the prizes and the mirrors of this contest (ADR-0063). */
export function ContestPartner({ contest, locale }: { contest: ContestDetail; locale: Locale }) {
  const partner = contest.partner ?? null;
  const mirrors = contest.mirrors ?? [];
  return (
    <>
      {partner && (
        <Card title={t(locale, "contest.partner")}>
          <div className="flex items-start gap-4" data-partner={partner.slug}>
            {partner.logo_url && (
              /* eslint-disable-next-line @next/next/no-img-element --
                 the logo is an address the staff entered (a site path or
                 https), like a team photo; next/image would need every host
                 listed. */
              <img
                src={partner.logo_url}
                alt=""
                className="size-14 shrink-0 rw-radius-sm border rw-line object-contain"
              />
            )}
            <div className="min-w-0 space-y-1">
              <p className="font-semibold rw-strong">{partner.name}</p>
              <p className="text-theme-xs rw-dim">
                {t(locale, `org.kind.${partner.kind}` as MessageKey)}
              </p>
              {partner.about && (
                <p className="whitespace-pre-line text-theme-sm rw-dim">{partner.about}</p>
              )}
              {partner.website && (
                <a
                  href={partner.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`text-theme-sm ${LINK}`}
                >
                  {t(locale, "contest.partner.website")}
                  <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
                </a>
              )}
            </div>
          </div>
        </Card>
      )}
      {contest.prizes && (
        <Card title={t(locale, "contest.prizes")}>
          <div data-prizes="">
            <Markdown>{contest.prizes}</Markdown>
          </div>
        </Card>
      )}
      {mirrors.length > 0 && (
        <Card title={t(locale, "contest.mirrors")} bodyClassName="p-0">
          <ul className="rw-divide divide-y" data-mirrors="">
            {mirrors.map((mirror) => (
              <li key={mirror.slug}>
                <Link
                  href={`/contests/${mirror.slug}`}
                  className="flex flex-wrap items-baseline justify-between gap-2 px-5 py-3 transition rw-hover-bg"
                >
                  <span className="font-medium rw-strong">{mirror.title}</span>
                  <span className="text-theme-xs rw-faint">{dateTime(mirror.start_at, locale)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </>
  );
}

