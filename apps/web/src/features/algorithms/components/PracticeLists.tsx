import type { Route } from "next";
import Link from "next/link";

import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { t, type Locale } from "@/i18n/messages";
import type { ExternalLink, PracticeProblem } from "@/lib/api";

import { VIA_LABEL } from "../catalog";

/** Practice for an algorithm (ADR-0062 § 2.5): our problems first — an
 *  editor's pick, the same problem as an external link, or one picked by
 *  topic and difficulty — then the original's links to other judges. */
export function PracticeLists({
  here,
  elsewhere,
  locale,
}: {
  here: PracticeProblem[];
  elsewhere: ExternalLink[];
  locale: Locale;
}) {
  if (here.length === 0 && elsewhere.length === 0) return null;
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {here.length > 0 && (
        <Card title={t(locale, "algorithms.practiceHere")} bodyClassName="p-0">
          <ul className="rw-divide divide-y">
            {here.map((problem) => (
              <li key={problem.slug}>
                <Link
                  href={`/problems/${problem.slug}` as Route}
                  className="flex min-h-11 items-center gap-3 px-5 py-2.5 transition rw-hover-bg rw-focus-ring"
                >
                  <span className="min-w-0 flex-1 truncate text-theme-sm font-medium rw-strong">
                    {problem.code !== null && <span className="rw-faint">{problem.code}. </span>}
                    {problem.title}
                  </span>
                  <Badge color="neutral">{t(locale, VIA_LABEL[problem.via])}</Badge>
                  <DifficultyBadge value={problem.difficulty} />
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      )}
      {elsewhere.length > 0 && (
        <Card title={t(locale, "algorithms.practiceElsewhere")} bodyClassName="p-0">
          <ul className="rw-divide divide-y">
            {elsewhere.map((link) => (
              <li key={link.url}>
                <a
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer nofollow"
                  className="flex min-h-11 items-center gap-3 px-5 py-2.5 transition rw-hover-bg rw-focus-ring"
                >
                  <span className="min-w-0 flex-1 truncate text-theme-sm rw-strong">{link.title}</span>
                  {link.platform && <span className="shrink-0 text-theme-xs rw-faint">{link.platform}</span>}
                  <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
                </a>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
