"use client";

import { GuestPrompt } from "@/components/auth/SignInPopover";
import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import {
  rateProblem,
  setFavourite,
  voteProblem,
  type ProblemDetail,
} from "@/lib/api";

const SCORES = [1, 2, 3, 4, 5] as const;

const actionBtn =
  "inline-flex min-h-7 min-w-7 items-center justify-center rw-radius-sm px-2.5 text-theme-sm font-semibold transition rw-hover-bg rw-focus-ring";

/** Sevimlilar va masalaga baho — prototip `.actions` (P0) bilan mos. */
export function ProblemActions({ problem }: { problem: ProblemDetail }) {
  const { user, ready } = useSession();
  const locale = useLocale();
  const [favourite, setFav] = useState(problem.is_favourite);
  const [mine, setMine] = useState(problem.my_rating);
  const [rating, setRating] = useState(problem.rating);
  const [votes, setVotes] = useState(problem.votes);
  const [busy, setBusy] = useState(false);

  const ratingSummaryId = `problem-rating-${problem.slug}`;

  async function toggleFavourite() {
    if (busy) return;
    const next = !favourite;
    setBusy(true);
    setFav(next);
    try {
      await setFavourite(problem.slug, next);
    } catch {
      setFav(!next);
    } finally {
      setBusy(false);
    }
  }

  async function rate(score: number) {
    if (busy) return;
    setBusy(true);
    try {
      const result = await rateProblem(problem.slug, score);
      setMine(result.my_rating);
      setRating({ average: result.average, count: result.count });
    } catch {
      // keep prior state
    } finally {
      setBusy(false);
    }
  }

  async function vote(value: -1 | 1) {
    if (busy) return;
    setBusy(true);
    try {
      setVotes(
        await voteProblem(problem.slug, votes.mine === value ? 0 : value),
      );
    } catch {
      // keep prior state
    } finally {
      setBusy(false);
    }
  }

  const signedIn = ready && !!user;

  const voteClass = (active: boolean, disabled: boolean) =>
    `${actionBtn} tabular-nums ${
      disabled
        ? "cursor-not-allowed border border-dashed rw-line rw-panel-2 rw-faint"
        : active
          ? "rw-accent-ink rw-accent-soft"
          : "rw-dim"
    }`;

  return (
    <div
      className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-theme-sm rw-dim"
      data-problem-actions=""
    >
      {ready && !user && (
        <GuestPrompt
          reason="favourite"
          trigger={(props) => (
            <button {...props} className={`${actionBtn} gap-1.5 rw-dim`}>
              {t(locale, "problem.addFavourite")}
            </button>
          )}
        />
      )}
      {signedIn && (
        <button
          type="button"
          onClick={toggleFavourite}
          aria-pressed={favourite}
          className={`${actionBtn} gap-1.5 ${
            favourite ? "rw-accent-ink rw-accent-soft" : "rw-dim"
          }`}
        >
          {favourite
            ? t(locale, "problem.inFavourites")
            : t(locale, "problem.addFavourite")}
        </button>
      )}

      {ready && !user && (
        <GuestPrompt
          reason="vote"
          trigger={(props) => (
            <button
              {...props}
              aria-label={`${t(locale, "problem.voteUp")} — ▲ ${votes.up}, ${t(locale, "problem.voteDown")} — ▼ ${votes.down}`}
              className={`${actionBtn} gap-2 tabular-nums rw-dim`}
            >
              <span>▲ {votes.up}</span>
              <span>▼ {votes.down}</span>
            </button>
          )}
        />
      )}
      {signedIn && (
      <span
        className="inline-flex items-center gap-0.5"
        role="group"
        aria-label={`${t(locale, "problem.voteUp")}, ${t(locale, "problem.voteDown")}`}
      >
        <button
          type="button"
          onClick={() => vote(1)}
          disabled={!signedIn}
          aria-pressed={votes.mine === 1}
          aria-label={`${t(locale, "problem.voteUp")} — ▲ ${votes.up}`}
          title={t(locale, "problem.voteUpTitle")}
          className={voteClass(votes.mine === 1, !signedIn)}
        >
          ▲ {votes.up}
        </button>
        <button
          type="button"
          onClick={() => vote(-1)}
          disabled={!signedIn}
          aria-pressed={votes.mine === -1}
          aria-label={`${t(locale, "problem.voteDown")} — ▼ ${votes.down}`}
          title={t(locale, "problem.voteDownTitle")}
          className={voteClass(votes.mine === -1, !signedIn)}
        >
          ▼ {votes.down}
        </button>
      </span>
      )}

      <span className="inline-flex flex-wrap items-center gap-2.5">
        <span id={ratingSummaryId} className="rw-faint tabular-nums">
          {rating.average !== null
            ? fill(t(locale, "problem.ratingSummary"), {
                average: rating.average,
                count: rating.count,
              })
            : t(locale, "problem.ratingEmpty")}
        </span>
        {signedIn && (
          <span
            className="inline-flex items-center"
            role="group"
            aria-labelledby={ratingSummaryId}
          >
            {SCORES.map((score) => {
              const on = mine !== null && score <= mine;
              return (
                <button
                  key={score}
                  type="button"
                  onClick={() => rate(score)}
                  aria-pressed={on}
                  aria-label={fill(t(locale, "problem.rateWith"), { score })}
                  className={`min-h-7 min-w-[26px] px-0.5 text-theme-base transition rw-focus-ring ${
                    on ? "rw-accent-ink" : "rw-faint rw-hover-bg"
                  }`}
                >
                  ★
                </button>
              );
            })}
          </span>
        )}
      </span>
    </div>
  );
}
