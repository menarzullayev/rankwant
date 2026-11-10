import { UserName } from "@/components/ui/Identity";
import { Card } from "@/components/ui/Card";
import { t, type Locale } from "@/i18n/messages";
import type { ContestDetail } from "@/lib/api";

/** «Musobaqani tayyorlaganlar» — told always (ADR-0055, part 2).
 *
 *  It is also why these people sit in the table with a star: they knew
 *  the problems before the start, so they take part unrated.
 */
export function ContestCrew({
  crew,
  locale,
}: {
  crew: ContestDetail["crew"];
  locale: Locale;
}) {
  const groups = [
    { key: "authors", label: "contest.crew.authors", people: crew.authors },
    { key: "testers", label: "contest.crew.testers", people: crew.testers },
    { key: "jury", label: "contest.crew.jury", people: crew.jury },
  ].filter((group) => group.people.length > 0);
  if (groups.length === 0) return null;
  return (
    <Card title={t(locale, "contest.crew.title")}>
      <div className="grid gap-4 sm:grid-cols-3" data-contest-crew="">
        {groups.map((group) => (
          <div key={group.key}>
            <h3 className="mb-1 text-theme-xs font-semibold rw-dim">{t(locale, group.label)}</h3>
            <ul className="flex flex-wrap gap-x-3 gap-y-1">
              {group.people.map((person) => (
                <li key={person.username}>
                  <UserName username={person.username} title={person.user_title} locale={locale} />
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <p className="mt-3 text-theme-xs rw-dim">{t(locale, "contest.crew.note")}</p>
    </Card>
  );
}
