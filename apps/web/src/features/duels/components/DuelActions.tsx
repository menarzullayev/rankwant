"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { dateTime, errorText, t } from "@/i18n/messages";
import {
  ApiError,
  getJson,
  postJson,
  type Duel,
  type DuelRecord,
} from "@/lib/api";

function DuelRow({
  d,
  me,
  onAction,
}: {
  d: Duel;
  me: string | null;
  onAction: (slug: string, a: string) => void;
}) {
  const locale = useLocale();
  const color =
    d.status === "open"
      ? "info"
      : d.status === "accepted"
        ? "success"
        : d.status === "finished"
          ? "neutral"
          : "error";
  return (
    <li className="flex flex-wrap items-center gap-3 px-5 py-3">
      <div className="min-w-0 flex-1">
        <Link
          href={`/duels/${d.slug}`}
          className="font-medium rw-strong rw-link-hover"
        >
          {d.title}
        </Link>
        <p className="text-theme-xs rw-faint">
          @{d.challenger}
          {d.opponent && ` vs @${d.opponent}`} · {d.problem_count}{" "}
          {t(locale, "duel.problems")} · ~{d.difficulty} · {d.duration_minutes}{" "}
          {t(locale, "duel.minutes")} ·{" "}
          {dateTime(d.start_at, locale)}
        </p>
      </div>
      <Badge color={color}>{d.status}</Badge>
      {d.status === "finished" && (
        <Badge color={d.is_draw ? "neutral" : "brand"}>
          {d.is_draw ? "draw" : `🏆 ${d.winner}`} {d.challenger_solved}:
          {d.opponent_solved}
        </Badge>
      )}
      {me && d.status === "open" && d.challenger !== me && (
        <Button
          variant="outline"
          className="h-9"
          onClick={() => onAction(d.slug, "accept")}
        >
          {t(locale, "duel.accept")}
        </Button>
      )}
      {me && d.status === "open" && d.challenger === me && (
        <Button
          variant="outline"
          className="h-9"
          onClick={() => onAction(d.slug, "cancel")}
        >
          {t(locale, "duel.cancel")}
        </Button>
      )}
    </li>
  );
}

export function DuelActions({ waiting }: { waiting: Duel[] }) {
  const locale = useLocale();
  const router = useRouter();
  const { user, ready } = useSession();
  const [mine, setMine] = useState<{
    record: DuelRecord;
    results: Duel[];
  } | null>(null);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  // Bir marta, mount'da: 15 daqiqadan keyin (MIN_LEAD_MINUTES dan katta)
  const [local] = useState(() => {
    const d = new Date(Date.now() + 15 * 60_000);
    d.setSeconds(0, 0);
    return new Date(d.getTime() - d.getTimezoneOffset() * 60_000)
      .toISOString()
      .slice(0, 16);
  });

  useEffect(() => {
    if (!user) return;
    getJson<{ record: DuelRecord; results: Duel[] }>("/duels/mine/")
      .then(setMine)
      .catch(() => {});
  }, [user]);

  async function act(slug: string, action: string) {
    setError("");
    try {
      await postJson(`/duels/${slug}/${action}/`, {});
      router.refresh();
      if (user) setMine(await getJson("/duels/mine/"));
    } catch (e) {
      setError(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    }
  }

  async function create(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const f = new FormData(e.currentTarget);
    try {
      await postJson("/duels/", {
        title: f.get("title"),
        problem_count: Number(f.get("problem_count")),
        difficulty: Number(f.get("difficulty")),
        duration_minutes: Number(f.get("duration_minutes")),
        start_at: new Date(String(f.get("start_at"))).toISOString(),
      });
      setShowForm(false);
      router.refresh();
      if (user) setMine(await getJson("/duels/mine/"));
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
    }
  }

  return (
    <div className="space-y-6">
      {error && <p className="text-theme-sm rw-bad-ink">{error}</p>}
      {ready && user && (
        <Card
          title={t(locale, "duel.mine")}
          action={
            <div className="flex items-center gap-3">
              {mine && (
                <Badge color="brand">
                  {t(locale, "duel.record")} {mine.record.wins}/
                  {mine.record.draws}/{mine.record.losses}
                </Badge>
              )}
              <Button className="h-9" onClick={() => setShowForm((v) => !v)}>
                {t(locale, "duel.create")}
              </Button>
            </div>
          }
          bodyClassName="p-0"
        >
          {showForm && (
            <form
              onSubmit={create}
              className="grid gap-3 border-b rw-divider p-5 md:grid-cols-2"
            >
              <Field
                label={t(locale, "admin.label.text.name")}
                name="title"
                required
                defaultValue="Blitz"
              />
              <Field
                label={t(locale, "duel.startAt")}
                name="start_at"
                type="datetime-local"
                required
                defaultValue={local}
              />
              <Field
                label={t(locale, "duel.problems")}
                name="problem_count"
                type="number"
                min={1}
                max={8}
                defaultValue={4}
              />
              <Field
                label={t(locale, "problems.difficulty")}
                name="difficulty"
                type="number"
                min={800}
                max={3500}
                step={100}
                defaultValue={1200}
              />
              <Field
                label={t(locale, "duel.minutes")}
                name="duration_minutes"
                type="number"
                min={15}
                max={240}
                defaultValue={60}
              />
              <div className="flex items-end">
                <Button type="submit">{t(locale, "duel.create")}</Button>
              </div>
            </form>
          )}
          <ul className="divide-y rw-divide">
            {(mine?.results ?? []).map((d) => (
              <DuelRow key={d.slug} d={d} me={user.username} onAction={act} />
            ))}
            {mine && mine.results.length === 0 && (
              <li className="px-5 py-6 text-center text-theme-sm rw-faint">
                {t(locale, "common.empty")}
              </li>
            )}
          </ul>
        </Card>
      )}

      <Card title={t(locale, "duel.waiting")} bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {waiting.map((d) => (
            <DuelRow
              key={d.slug}
              d={d}
              me={user?.username ?? null}
              onAction={act}
            />
          ))}
          {waiting.length === 0 && (
            <li className="px-5 py-6 text-center text-theme-sm rw-faint">
              {t(locale, "common.empty")}
            </li>
          )}
        </ul>
      </Card>
    </div>
  );
}
