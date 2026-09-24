import { Card } from "@/components/ui/Card";
import { ContentName } from "@/components/ui/UzFallbackBadge";
import { fill, t, type Locale } from "@/i18n/messages";
import type { TopicStrength as Topic } from "@/lib/api";
import { SectionHint } from "./SectionHint";

/** Mavzu kuchi — Skills formulasi mavzu kesimida (`problems/skills/` bilan bir hisob). */
export function TopicStrength({ topics, locale }: { topics: Topic[]; locale: Locale }) {
  const shown = topics.filter((topic) => topic.solved > 0 || topic.stuck > 0).slice(0, 12);
  const max = Math.max(...shown.map((topic) => topic.rating), 1);
  return (
    <Card title={t(locale, "profile.topicsTitle")} bodyClassName="space-y-4">
      <SectionHint>{t(locale, "profile.topicsHint")}</SectionHint>
      {shown.length === 0 ? (
        <p className="text-theme-sm rw-faint">{t(locale, "common.empty")}</p>
      ) : (
        <ul className="space-y-3">
          {shown.map((topic) => (
            <li key={topic.slug}>
              <div className="flex items-baseline justify-between gap-2 text-theme-sm">
                <span className="min-w-0 truncate rw-strong">
                  <ContentName row={topic} locale={locale} />
                </span>
                <span className="shrink-0 tabular-nums rw-faint">
                  {topic.rating} · {topic.solved}/{topic.total}
                  {topic.stuck > 0 && (
                    <span className="ml-1 rw-warn-ink">
                      {fill(t(locale, "profile.topicStuck"), { n: topic.stuck })}
                    </span>
                  )}
                </span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${Math.round((topic.rating / max) * 100)}%`,
                    background: "var(--rw-accent)",
                  }}
                />
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
