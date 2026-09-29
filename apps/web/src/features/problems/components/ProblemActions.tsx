"use client";

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

const SCORES = [1, 2, 3, 4, 5];

/** Sevimlilar va masalaga baho — RoboContest sahifasida ikkalasi ham
 * bor. Baho muallif uchun ham, masala tanlayotgan solver uchun ham
 * signal; sevimlilar uzun arxivda yo'qotmaslik uchun. */
export function ProblemActions({ problem }: { problem: ProblemDetail }) {
  const { user, ready } = useSession();
  const locale = useLocale();
  const [favourite, setFav] = useState(problem.is_favourite);
  const [mine, setMine] = useState(problem.my_rating);
  const [rating, setRating] = useState(problem.rating);
  const [votes, setVotes] = useState(problem.votes);
  const [busy, setBusy] = useState(false);

  async function toggleFavourite() {
    if (busy) return;
    const next = !favourite;
    setBusy(true);
    setFav(next); // optimistik — tugma darhol javob berishi kerak
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
      // Baho saqlanmadi — mavjud holat o'zgarmaydi.
    } finally {
      setBusy(false);
    }
  }

  /** Ovoz — bir bosish. Yulduzli bahodan farqi shunda: yulduz masalaning
   * SIFATINI o'lchaydi va o'ylashni talab qiladi, ovoz esa «yoqdimi?»
   * degan oddiy savolga javob va shu sababli ancha ko'p yig'iladi. */
  async function vote(value: -1 | 1) {
    if (busy) return;
    setBusy(true);
    try {
      // Ikkinchi marta bosish ovozni olib tashlaydi.
      setVotes(
        await voteProblem(problem.slug, votes.mine === value ? 0 : value),
      );
    } catch {
      // Ovoz saqlanmadi — mavjud holat o'zgarmaydi.
    } finally {
      setBusy(false);
    }
  }

  const signedIn = ready && !!user;
  const voteStyle = (active: boolean) =>
    `rw-radius-sm px-2 py-1 font-medium tabular-nums transition rw-hover-bg ${
      active ? "rw-accent-ink" : "rw-dim"
    }`;

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-theme-sm">
      {signedIn && (
        <button
          type="button"
          onClick={toggleFavourite}
          aria-pressed={favourite}
          className={`rw-radius-sm px-2.5 py-1 font-medium transition rw-hover-bg ${
            favourite ? "rw-accent-ink" : "rw-dim"
          }`}
        >
          {t(locale, favourite ? "problem.inFavourites" : "problem.addFavourite")}
        </button>
      )}

      <div className="flex items-center gap-0.5">
        <button
          type="button"
          onClick={() => vote(1)}
          disabled={!signedIn}
          aria-pressed={votes.mine === 1}
          // ⚠️ Ko'rinadigan matn — `▲ 12`. Ilgari `aria-label="Yoqdi"`
          // edi, ya'ni ovoz bilan boshqaradigan foydalanuvchi ekranda
          // ko'rgan raqamni ayta olmasdi (WCAG 2.5.3, «Label in Name»).
          // Lighthouse tutdi: `label-content-name-mismatch`. Endi nom
          // ko'rinadigan matnni O'Z ICHIGA OLADI.
          aria-label={`${t(locale, "problem.voteUp")} — ▲ ${votes.up}`}
          title={t(locale, "problem.voteUpTitle")}
          className={voteStyle(votes.mine === 1)}
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
          className={voteStyle(votes.mine === -1)}
        >
          ▼ {votes.down}
        </button>
      </div>

      <div className="flex items-center gap-1.5">
        <span className="rw-faint">
          {rating.average !== null
            ? fill(t(locale, "problem.ratingSummary"), {
                average: rating.average,
                count: rating.count,
              })
            : t(locale, "problem.ratingEmpty")}
        </span>
        {signedIn && (
          <span className="flex items-center">
            {SCORES.map((score) => (
              <button
                key={score}
                type="button"
                onClick={() => rate(score)}
                aria-label={fill(t(locale, "problem.rateWith"), { score })}
                className={`px-0.5 transition ${
                  mine !== null && score <= mine ? "rw-accent-ink" : "rw-faint"
                }`}
              >
                ★
              </button>
            ))}
          </span>
        )}
      </div>
    </div>
  );
}
