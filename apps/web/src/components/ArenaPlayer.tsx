"use client";

import { useCallback, useEffect, useState } from "react";

import { Markdown } from "@/components/Markdown";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import {
  API_BASE,
  ApiError,
  getJson,
  postJson,
  type ArenaCurrent,
  type ArenaDetail,
  type ArenaStanding,
} from "@/lib/api";

/** Jonli raund. Joriy savol serverdan har 2 s so'raladi — server vaqti
 * haqiqat manbai (mijoz taymeri emas), standings SSE bilan. */
export function ArenaPlayer({ initial }: { initial: ArenaDetail }) {
  const locale = useLocale();
  const { user, ready } = useSession();
  const [arena, setArena] = useState(initial);
  const [current, setCurrent] = useState<ArenaCurrent | null>(null);
  const [rows, setRows] = useState<ArenaStanding[]>([]);
  // Ommaviy jadval eng yaxshi 500 tani beradi — bu chegara CDN keshi
  // uchun. O'z qatorini unga qo'shib bo'lmaydi (javob har kimga
  // boshqacha bo'lib qolardi), shuning uchun alohida olinadi.
  const [me, setMe] = useState<ArenaStanding | null>(null);
  const [left, setLeft] = useState(0);
  const [feedback, setFeedback] = useState<string>("");
  const [error, setError] = useState("");

  const refreshArena = useCallback(async () => {
    setArena(await getJson<ArenaDetail>(`/arena/${initial.slug}/`));
  }, [initial.slug]);

  // Joriy savol — faqat qo'shilgan va raund yurayotganda
  useEffect(() => {
    if (!user || !arena.joined) return;
    let alive = true;
    const tick = async () => {
      try {
        const c = await getJson<ArenaCurrent>(`/arena/${arena.slug}/current/`);
        if (alive) setCurrent(c);
      } catch (e) {
        if (alive && e instanceof ApiError) {
          setCurrent(null);
          if (e.code === "not_running") await refreshArena();
        }
      }
    };
    void tick();
    const h = setInterval(tick, 2000);
    return () => {
      alive = false;
      clearInterval(h);
    };
  }, [user, arena.joined, arena.slug, refreshArena]);

  // Qolgan soniyalar — server deadline'idan
  useEffect(() => {
    if (!current) return;
    const h = setInterval(() => {
      setLeft(
        Math.max(
          0,
          Math.round(
            (new Date(current.deadline).getTime() - Date.now()) / 1000,
          ),
        ),
      );
    }, 250);
    return () => clearInterval(h);
  }, [current]);

  // Standings — polling. SSE olib tashlandi: har ulanish gunicorn
  // ishchisini band qilardi va to'rtta tomoshabin API ni to'xtatardi
  // (contests/views.py dagi izoh). Javob chekkada keshlanadi.
  useEffect(() => {
    const fetchRows = () =>
      fetch(`${API_BASE}/arena/${arena.slug}/standings/`)
        .then((r) => r.json())
        .then((d) => setRows(d.results ?? []))
        .catch(() => {});
    const fetchMe = () =>
      // Kirmagan yoki qatnashmagan foydalanuvchida 404 — bu xato emas.
      getJson<ArenaStanding>(`/arena/${arena.slug}/standings/me/`)
        .then(setMe)
        .catch(() => setMe(null));

    void fetchRows();
    void fetchMe();
    const poll = setInterval(() => {
      void fetchRows();
      void fetchMe();
    }, 5000);
    return () => clearInterval(poll);
  }, [arena.slug]);

  async function join() {
    try {
      setArena(await postJson<ArenaDetail>(`/arena/${arena.slug}/join/`, {}));
    } catch (e) {
      setError(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    }
  }

  async function answer(choiceId: number) {
    if (!current) return;
    try {
      const r = await postJson<{ is_correct: boolean; points: number }>(
        `/arena/${arena.slug}/answer/`,
        { question_id: current.question.id, choice_id: choiceId },
      );
      setFeedback(r.is_correct ? `✓ +${r.points}` : "✗ 0");
      setCurrent({ ...current, answered: true });
    } catch (e) {
      setError(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <div className="space-y-4">
        {error && <p className="text-theme-sm rw-bad-ink">{error}</p>}
        {ready && !user && (
          <Card>
            <p className="text-theme-sm rw-faint">
              {t(locale, "auth.login")} →
            </p>
          </Card>
        )}
        {user && !arena.joined && !arena.is_finished && (
          <Card>
            <Button onClick={join}>{t(locale, "arena.join")}</Button>
          </Card>
        )}
        {user && arena.joined && !current && !arena.is_finished && (
          <Card>
            <Badge color="success">{t(locale, "arena.joined")}</Badge>
            <p className="mt-2 text-theme-sm rw-faint">
              {t(locale, "arena.waiting")} —{" "}
              {new Date(arena.start_at).toLocaleTimeString(locale)}
            </p>
          </Card>
        )}
        {arena.is_finished && (
          <Card>
            <Badge>{t(locale, "arena.finished")}</Badge>
          </Card>
        )}
        {current && (
          <Card
            title={`${current.index + 1} / ${arena.question_count}`}
            action={
              <span
                className={`text-title-sm font-bold ${left <= 5 ? "rw-bad-ink" : "rw-accent-ink"}`}
              >
                {left}s
              </span>
            }
          >
            <Markdown>{current.question.text}</Markdown>
            <div className="mt-4 grid gap-2">
              {current.question.choices.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  disabled={current.answered}
                  onClick={() => answer(c.id)}
                  className="rw-radius-sm border rw-line px-4 py-2.5 text-left text-theme-sm transition rw-hover-line disabled:opacity-60"
                >
                  {c.text}
                </button>
              ))}
            </div>
            {current.answered && (
              <p className="mt-3 text-theme-sm font-medium rw-dim">
                {t(locale, "arena.answered")} {feedback}
              </p>
            )}
          </Card>
        )}
      </div>

      <Card title={t(locale, "standings.title")} bodyClassName="p-0">
        <Table>
          <THead>
            <TH>#</TH>
            <TH>{t(locale, "standings.user")}</TH>
            <TH align="right">{t(locale, "tournament.points")}</TH>
            <TH align="right">✓</TH>
          </THead>
          <TBody>
            {rows.map((r) => (
              <TR key={r.username}>
                <TD className="rw-faint">{r.rank}</TD>
                <TD className="font-medium">{r.display_name || r.username}</TD>
                <TD align="right" className="font-semibold">
                  {r.score}
                </TD>
                <TD align="right">{r.correct_count}</TD>
              </TR>
            ))}
            {me && !rows.some((r) => r.username === me.username) && (
              <TR key={me.username}>
                <TD className="font-semibold rw-accent-ink">{me.rank}</TD>
                <TD className="font-medium rw-accent-ink">
                  {me.display_name || me.username}{" "}
                  <span className="rw-dim-2">
                    · {t(locale, "standings.you")}
                  </span>
                </TD>
                <TD align="right" className="font-semibold">
                  {me.score}
                </TD>
                <TD align="right">{me.correct_count}</TD>
              </TR>
            )}
            {rows.length === 0 && !me && (
              <EmptyRow colSpan={4}>{t(locale, "common.empty")}</EmptyRow>
            )}
          </TBody>
        </Table>
      </Card>
    </div>
  );
}
