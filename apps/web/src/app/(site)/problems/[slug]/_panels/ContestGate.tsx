import type { Route } from "next";

import { ButtonLink } from "@/components/ui/Button";
import { fill, t, type Locale } from "@/i18n/messages";
import type { ProblemDetail } from "@/lib/api";

type Held = NonNullable<ProblemDetail["contest"]>;

/** What stands in the solve panel while a problem belongs to a contest and
 *  this visitor cannot send to it (ADR-0055).
 *
 *  - `register` — the contest is on and the visitor is not registered;
 *  - `ended`    — the contest is over and not finalized yet: the problem
 *    reaches the archive, and takes solutions again, when it is.
 *
 *  The statement beside it stays open either way.
 */
export function ContestGate({
  held,
  kind,
  locale,
}: {
  held: Held;
  kind: "register" | "ended";
  locale: Locale;
}) {
  const register = kind === "register";
  return (
    <section
      aria-labelledby="contest-gate"
      data-gate={`contest-${kind}`}
      className="flex flex-col items-center gap-3 rw-radius border border-dashed border-[var(--rw-accent)] rw-surface px-5 py-10 text-center"
    >
      <h2 id="contest-gate" className="text-theme-base font-semibold rw-strong">
        {register
          ? fill(t(locale, "contest.gate.registerTitle"), { contest: held.title })
          : t(locale, "contest.gate.endedTitle")}
      </h2>
      <p className="text-theme-sm rw-dim">
        {t(locale, register ? "contest.gate.registerBody" : "contest.gate.endedBody")}
      </p>
      <ButtonLink href={`/contests/${held.slug}` as Route}>
        {t(locale, "contest.gate.cta")}
      </ButtonLink>
    </section>
  );
}
