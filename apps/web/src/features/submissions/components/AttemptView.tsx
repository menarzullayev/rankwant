"use client";

import Link from "next/link";

import { TimeLine } from "@/components/kit/TimeStamp";
import { CodeCopy } from "@/components/kit/CopyControl";
import { HackPanel } from "@/features/hackathons";
import { Card } from "@/components/ui/Card";
import { Verdict } from "@/components/ui/Verdict";
import { Loading } from "@/components/ui/Loading";
import { Status } from "@/components/kit/Feedback";
import { useLoad } from "@/lib/hooks";
import { UserName } from "@/components/ui/Identity";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import type { AttemptDetail } from "@/lib/api";

/** Bitta urinishning sahifasi.
 *
 * Ma'lumot MIJOZDA olinadi, serverda emas: manba kod faqat egasiga va
 * hack huquqi bor odamga qaytariladi, SSR yordamchisi esa cookie
 * yubormaydi — server tomonda so'ralganda manba hech qachon kelmasdi.
 */
export function AttemptView({ id }: { id: number }) {
  const locale = useLocale();
  const { data, error } = useLoad<AttemptDetail>(`/attempts/${id}/`);

  if (error) return <Status error={error} />;
  if (!data) return <Loading />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="text-title-sm font-bold rw-strong">
          {fill(t(locale, "attempt.title"), { id })}
        </h1>
        <Link
          href={`/problems/${data.problem}`}
          className="text-theme-sm font-medium rw-link-hover"
        >
          {data.problem}
        </Link>
      </div>

      <Card>
        <div className="flex flex-wrap items-center gap-3">
          <Verdict verdict={data.verdict} />
          <UserName
            username={data.username}
            title={data.user_title}
            locale={locale}
          />
          <span className="text-theme-sm rw-dim">
            {data.language} · {data.time_ms} ms ·{" "}
            {Math.round(data.memory_kb / 1024)} MB
          </span>
        </div>
        <TimeLine
          locale={locale}
          events={[
            {
              at: data.created_at,
              label: fill(t(locale, "attempt.title"), { id }),
            },
          ]}
        />

        {data.failed_test_index !== null && (
          <p className="mt-3 text-theme-sm rw-bad-ink">
            {fill(t(locale, "attempt.failedAt"), {
              index: data.failed_test_index,
            })}
          </p>
        )}

        {data.compile_output && (
          <pre className="mt-3 max-h-56 overflow-auto rw-radius-sm rw-field-bg p-3 text-theme-xs rw-dim-2">
            {data.compile_output}
          </pre>
        )}

        {data.test_results.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {data.test_results.map((test) => (
              <span
                key={test.index}
                title={fill(t(locale, "submit.testTooltip"), {
                  index: test.index,
                  verdict: test.verdict,
                  time: test.time_ms,
                })}
                className={`flex size-7 items-center justify-center rw-radius-sm text-theme-xs font-medium ${
                  test.verdict === "AC"
                    ? "rw-ok-soft rw-ok-ink"
                    : "rw-bad-soft rw-bad-ink"
                }`}
              >
                {test.index}
              </span>
            ))}
          </div>
        )}
      </Card>

      <Card title={t(locale, "attempt.source")}>
        {data.source_code ? (
          <CodeCopy text={data.source_code} filename={t(locale, "attempt.source")}>
            <pre className="max-h-[32rem] overflow-auto rw-radius-sm rw-field-bg p-3 font-mono text-theme-xs rw-strong">
              {data.source_code}
            </pre>
          </CodeCopy>
        ) : (
          <p className="text-theme-sm rw-faint">
            {t(locale, "attempt.sourceHidden")}
          </p>
        )}
      </Card>

      <HackPanel attempt={data} />
    </div>
  );
}
