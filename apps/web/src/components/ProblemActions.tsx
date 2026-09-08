"use client";

import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { rateProblem, setFavourite, type ProblemDetail } from "@/lib/api";

const SCORES = [1, 2, 3, 4, 5];

/** Sevimlilar va masalaga baho — RoboContest sahifasida ikkalasi ham
 * bor. Baho muallif uchun ham, masala tanlayotgan solver uchun ham
 * signal; sevimlilar uzun arxivda yo'qotmaslik uchun. */
export function ProblemActions({ problem }: { problem: ProblemDetail }) {
  const { user, ready } = useSession();
  const [favourite, setFav] = useState(problem.is_favourite);
  const [mine, setMine] = useState(problem.my_rating);
  const [rating, setRating] = useState(problem.rating);
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

  const signedIn = ready && !!user;

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
          {favourite ? "★ Sevimlilarda" : "☆ Sevimlilarga"}
        </button>
      )}

      <div className="flex items-center gap-1.5">
        <span className="rw-faint">
          {rating.average !== null
            ? `${rating.average} · ${rating.count} baho`
            : "Baho yo'q"}
        </span>
        {signedIn && (
          <span className="flex items-center">
            {SCORES.map((score) => (
              <button
                key={score}
                type="button"
                onClick={() => rate(score)}
                aria-label={`${score} baho berish`}
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
