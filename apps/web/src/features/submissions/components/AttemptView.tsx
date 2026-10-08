"use client";

import { SignInGate } from "@/components/auth/SignInGate";
import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo } from "react";

import { CodeCopy } from "@/components/kit/CopyControl";
import { TimeLine } from "@/components/kit/TimeStamp";
import { Status } from "@/components/kit/Feedback";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { UserName } from "@/components/ui/Identity";
import { Loading } from "@/components/ui/Loading";
import { Verdict } from "@/components/ui/Verdict";
import { useSession } from "@/context/SessionContext";
import { HackPanel } from "@/features/hackathons";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import type { AttemptDetail } from "@/lib/api";
import { highlight, type TokenKind } from "@/lib/highlight";
import { useLoad } from "@/lib/hooks";
import { isPendingVerdict } from "@/lib/theme/verdict";

/** Token colours come from the theme's own inks, so the code reads in
 *  every style and in both modes. */
const TOKEN_CLASS: Record<TokenKind, string> = {
  plain: "",
  comment: "rw-faint italic",
  string: "rw-ok-ink",
  number: "rw-warn-ink",
  keyword: "rw-accent-ink",
};

const PASSED = "AC";
/** The stand-in language of an answer-files attempt: nothing to edit. */
const ANSWER_LANGUAGE = "answer";

/** Bitta urinishning sahifasi.
 *
 * Ma'lumot MIJOZDA olinadi, serverda emas: manba kod faqat egasiga va
 * hack huquqi bor odamga qaytariladi, SSR yordamchisi esa cookie
 * yubormaydi — server tomonda so'ralganda manba hech qachon kelmasdi.
 */
export function AttemptView({ id }: { id: number }) {
  const locale = useLocale();
  const router = useRouter();
  const { user } = useSession();
  const { data, error } = useLoad<AttemptDetail>(`/attempts/${id}/`);

  const tokens = useMemo(
    () => (data?.source_code ? highlight(data.source_code, data.language) : []),
    [data],
  );

  if (error) return <Status error={error} />;
  if (!data) return <Loading />;

  const problemHref = `/problems/${data.problem}` as Route;
  const problemName = data.problem_title || data.problem;
  const judged = !isPendingVerdict(data.verdict);
  const passed = data.test_results.filter((test) => test.verdict === PASSED).length;
  const total = Math.max(data.tests_total, data.test_results.length);
  const mine = Boolean(user) && user!.username === data.username;

  /** Opens the problem with this source in the editor. The editor keeps
   *  a draft per problem and language in this browser; writing the draft
   *  is the whole hand-off, so nothing new travels in the URL. */
  const editAndResubmit = () => {
    try {
      localStorage.setItem(`rw:draft:${data.problem}:${data.language}`, data.source_code ?? "");
      localStorage.setItem("rw:language", data.language);
    } catch {
      // Storage is closed (private mode): the problem still opens, with
      // whatever draft the editor already has.
    }
    router.push(problemHref);
  };

  const facts: [string, React.ReactNode][] = [
    [t(locale, "attempts.language"), data.language_name || data.language],
  ];
  if (judged && data.language !== ANSWER_LANGUAGE) {
    facts.push(
      [t(locale, "attempts.col.runTime"), `${data.time_ms} ms`],
      [t(locale, "col.memory"), `${Math.round(data.memory_kb / 1024)} MB`],
    );
  }
  facts.push([t(locale, "attempts.col.codeSize"), `${data.source_size} B`]);
  if (total > 0 && judged) {
    facts.push([
      t(locale, "attempt.tests"),
      fill(t(locale, "attempt.testsPassed"), { passed, total }),
    ]);
  }
  if (data.score > 0) facts.push([t(locale, "col.points"), data.score]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-title-sm font-bold rw-strong">
            {fill(t(locale, "attempt.title"), { id })}
          </h1>
          <p className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-theme-sm rw-dim">
            <Link href={problemHref} className="font-medium rw-link-hover">
              {data.problem_code !== null && (
                <span className="mr-1.5 font-mono text-theme-xs rw-faint tabular-nums">
                  #{String(data.problem_code).padStart(4, "0")}
                </span>
              )}
              {problemName}
            </Link>
            <UserName username={data.username} title={data.user_title} locale={locale} />
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <ButtonLink href={problemHref} variant="outline">
            {t(locale, "attempt.toProblem")}
          </ButtonLink>
          {mine && data.source_code && data.language !== ANSWER_LANGUAGE && (
            <Button type="button" onClick={editAndResubmit}>
              {t(locale, "attempt.editResubmit")}
            </Button>
          )}
        </div>
      </div>

      <Card>
        <div className="flex flex-wrap items-center gap-2">
          <Verdict verdict={data.verdict} variant="full" />
          {data.failed_test_index !== null && (
            <span className="text-theme-sm rw-bad-ink">
              {fill(t(locale, "attempt.failedAt"), { index: data.failed_test_index })}
            </span>
          )}
        </div>

        <TimeLine
          locale={locale}
          events={[{ at: data.created_at, label: t(locale, "attempts.col.submitted") }]}
        />

        <dl className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
          {facts.map(([label, value]) => (
            <div key={label} className="rw-radius-sm rw-field-bg px-3 py-2">
              <dt className="text-theme-xs rw-faint">{label}</dt>
              <dd className="text-theme-sm font-medium rw-strong tabular-nums">{value}</dd>
            </div>
          ))}
        </dl>

        {data.compile_output && (
          <pre tabIndex={0} className="mt-4 max-h-56 rw-scroll rw-radius-sm rw-field-bg p-3 text-theme-xs rw-dim-2">
            {data.compile_output}
          </pre>
        )}

        {data.test_results.length > 0 && (
          <ol className="mt-4 flex flex-wrap gap-1" aria-label={t(locale, "attempt.tests")}>
            {data.test_results.map((test) => {
              const tip = fill(t(locale, "submit.testTooltip"), {
                index: test.index,
                verdict: test.verdict,
                time: test.time_ms,
              });
              return (
                <li
                  key={test.index}
                  title={tip}
                  aria-label={tip}
                  className={`flex size-7 items-center justify-center rw-radius-sm text-theme-xs font-medium ${
                    test.verdict === PASSED ? "rw-ok-soft rw-ok-ink" : "rw-bad-soft rw-bad-ink"
                  }`}
                >
                  {test.index}
                </li>
              );
            })}
          </ol>
        )}
      </Card>

      {/* A guest is never sent the source (the API leaves it out); the
          card says how to see it instead of an empty box. */}
      {!user && !data.source_code ? (
        <SignInGate reason="source" />
      ) : (
      <Card title={t(locale, "attempt.source")}>
        {data.source_code ? (
          <CodeCopy text={data.source_code} filename={data.language_name || data.language}>
            <pre tabIndex={0} className="max-h-[32rem] rw-scroll rw-radius-sm rw-field-bg p-3 font-mono text-theme-xs rw-strong">
              <code>
                {tokens.map((token, index) =>
                  token.kind === "plain" ? (
                    token.text
                  ) : (
                    <span key={index} className={TOKEN_CLASS[token.kind]}>
                      {token.text}
                    </span>
                  ),
                )}
              </code>
            </pre>
          </CodeCopy>
        ) : (
          <p className="text-theme-sm rw-faint">{t(locale, "attempt.sourceHidden")}</p>
        )}
      </Card>
      )}

      <HackPanel attempt={data} />
    </div>
  );
}
