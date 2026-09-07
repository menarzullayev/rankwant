"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { getJson, type Duel } from "@/lib/api";

/** Masalalar faqat ishtirokchiga va faqat boshlangach — sessiya kerak,
 *  shuning uchun brauzerda qayta so'raladi. */
export function DuelDetail({ initial }: { initial: Duel }) {
  const locale = DEFAULT_LOCALE;
  const { user } = useSession();
  const [duel, setDuel] = useState(initial);

  useEffect(() => {
    if (!user) return;
    const load = () => getJson<Duel>(`/duels/${initial.slug}/`).then(setDuel).catch(() => {});
    void load();
    const h = setInterval(load, 15000);
    return () => clearInterval(h);
  }, [user, initial.slug]);

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex flex-wrap items-center gap-3 text-theme-sm">
          <span className="font-semibold text-gray-800 dark:text-white/90">@{duel.challenger}</span>
          <span className="text-gray-400">vs</span>
          <span className="font-semibold text-gray-800 dark:text-white/90">
            {duel.opponent ? `@${duel.opponent}` : "…"}
          </span>
          <Badge color={duel.status === "finished" ? "neutral" : duel.is_running ? "success" : "info"}>
            {duel.status}
          </Badge>
          {duel.status === "finished" && (
            <Badge color="brand">
              {duel.is_draw ? "draw" : `🏆 ${duel.winner}`} · {duel.challenger_solved}:{duel.opponent_solved}
            </Badge>
          )}
        </div>
        <p className="mt-2 text-theme-xs text-gray-400">
          {new Date(duel.start_at).toLocaleString(locale)} — {new Date(duel.end_at).toLocaleTimeString(locale)} ·{" "}
          {duel.problem_count} {t(locale, "duel.problems")} · ~{duel.difficulty}
        </p>
      </Card>
      <Card title={t(locale, "nav.problems")}>
        {duel.problems.length === 0 ? (
          <p className="text-theme-sm text-gray-400">
            {duel.status === "open" ? t(locale, "duel.waiting") : duel.is_running ? "…" : t(locale, "arena.waiting")}
          </p>
        ) : (
          <ul className="grid gap-2 md:grid-cols-2">
            {duel.problems.map((p) => (
              <li key={p.slug}>
                <Link
                  href={`/problems/${p.slug}`}
                  className="flex items-center justify-between rounded-lg border border-gray-200 px-4 py-2.5
                    text-theme-sm hover:border-brand-400 dark:border-[#232936]"
                >
                  <span>{p.order}. {p.title}</span>
                  <DifficultyBadge value={p.difficulty} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
