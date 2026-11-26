"use client";

import type { Route } from "next";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { ButtonLink } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import { loginHref } from "@/lib/access";

/** What a guest is asked to sign in for. Each has a title; the large
 *  blocks have a sentence of their own, the rest share one. */
export type GateReason =
  | "solve"
  | "editorial"
  | "source"
  | "quiz"
  | "arena"
  | "hackathon"
  | "duel"
  | "contest"
  | "course"
  | "classroom"
  | "qvant"
  | "follow"
  | "vote"
  | "favourite"
  | "report"
  | "comment"
  | "blog";

const BODY: Partial<Record<GateReason, MessageKey>> = {
  solve: "gate.solve.body",
  editorial: "gate.editorial.body",
  source: "gate.source.body",
};

export const gateTitle = (reason: GateReason) => `gate.${reason}.title` as MessageKey;
export const gateBody = (reason: GateReason) => BODY[reason] ?? "gate.personal.body";

/** The address to come back to: this page, with its query.
 *
 *  The query is read after mount. A search-params hook would push every
 *  page that shows a gate into a Suspense fallback (measured on the
 *  sign-in form, 2026-09-21); the path alone is right for the first paint
 *  and the query joins it a moment later. */
export function useReturnTo(): string {
  const pathname = usePathname() ?? "/";
  const [query, setQuery] = useState("");
  useEffect(() => {
    // Read once the browser has the address; nothing to subscribe to.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setQuery(window.location.search);
  }, [pathname]);
  return `${pathname}${query}`;
}

/** The two links every gate ends with. */
export function SignInLinks({ next }: { next: string }) {
  const locale = useLocale();
  return (
    <div className="flex flex-wrap gap-2">
      <ButtonLink href={loginHref(next, "login") as Route}>{t(locale, "auth.login")}</ButtonLink>
      <ButtonLink href={loginHref(next, "register") as Route} variant="outline">
        {t(locale, "auth.register")}
      </ButtonLink>
    </div>
  );
}

/** The gate's title and two actions as a bar fixed to the bottom of the
 *  screen, below `xl` only. The solve card stands after the statement there
 *  and a phone reader met it 2.5 screens down (A+B at 375 px: 2 043 of 2 970
 *  px, measured 2026-11-26); the bar keeps the way in on screen, like the
 *  signed-in reader's editor sheet, and clears the side menu the same way
 *  (`--rw-shell-inset`). The card itself stays. */
export function SignInBar({ reason }: { reason: GateReason }) {
  const locale = useLocale();
  const next = useReturnTo();
  return (
    <>
      {/* Room for the bar, so the page's end (the footer) is not covered. */}
      <div aria-hidden className="h-28 xl:hidden" />
      <div
        data-gate-bar={reason}
        className="fixed inset-x-0 bottom-0 z-30 border-t rw-divider rw-surface px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] shadow-[0_-8px_32px_rgba(0,0,0,.12)] lg:left-[var(--rw-shell-inset,0px)] xl:hidden"
      >
        <p className="mb-2 text-theme-sm font-semibold rw-strong">
          {t(locale, gateTitle(reason))}
        </p>
        <SignInLinks next={next} />
      </div>
    </>
  );
}

/** The card a guest sees where a signed-in block would be (ADR-0054).
 *
 *  One component for every such place, so the wording, the two actions and
 *  the way back are the same everywhere. It replaces the block — the block
 *  itself is not rendered, hidden or disabled underneath.
 */
export function SignInGate({
  reason,
  centered = false,
  className = "",
}: {
  reason: GateReason;
  /** A block that fills a column (the solve panel) centres its content. */
  centered?: boolean;
  className?: string;
}) {
  const locale = useLocale();
  const next = useReturnTo();
  return (
    <section
      aria-labelledby={`gate-${reason}`}
      data-gate={reason}
      className={`rw-radius border border-dashed border-[var(--rw-accent)] rw-surface p-5 ${
        centered ? "flex flex-col items-center gap-3 px-5 py-10 text-center" : "space-y-3"
      } ${className}`}
    >
      <h2 id={`gate-${reason}`} className="text-theme-base font-semibold rw-strong">
        {t(locale, gateTitle(reason))}
      </h2>
      <p className="text-theme-sm rw-dim">{t(locale, gateBody(reason))}</p>
      <SignInLinks next={next} />
      <p className="text-theme-xs rw-dim">{t(locale, "gate.returnNote")}</p>
    </section>
  );
}
