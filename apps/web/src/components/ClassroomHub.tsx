"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError, getJson, postJson, type Classroom } from "@/lib/api";

/** Sinflar shaxsiy (egasi yoki a'zo) — sessiya kerak, brauzerda yuklanadi. */
export function ClassroomHub() {
  const locale = useLocale();
  const { user, ready } = useSession();
  const [rooms, setRooms] = useState<Classroom[]>([]);
  const [error, setError] = useState("");

  const load = () =>
    getJson<Classroom[]>("/classrooms/")
      .then(setRooms)
      .catch(() => setRooms([]));
  useEffect(() => {
    if (user) void load();
  }, [user]);

  async function create(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const f = Object.fromEntries(new FormData(e.currentTarget));
    try {
      await postJson("/classrooms/", f);
      (e.target as HTMLFormElement).reset();
      await load();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
    }
  }

  async function join(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const f = Object.fromEntries(new FormData(e.currentTarget));
    try {
      await postJson("/classrooms/join/", f);
      (e.target as HTMLFormElement).reset();
      await load();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
    }
  }

  if (ready && !user) {
    return (
      <Card>
        <p className="text-theme-sm rw-faint">{t(locale, "auth.login")} →</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {error && <p className="text-theme-sm rw-bad-ink">{error}</p>}
      <div className="grid gap-4 md:grid-cols-2">
        <Card title={t(locale, "classroom.join")}>
          <form onSubmit={join} className="flex gap-2">
            <Field
              label={t(locale, "classroom.code")}
              name="join_code"
              required
            />
            <div className="flex items-end">
              <Button type="submit">→</Button>
            </div>
          </form>
        </Card>
        <Card title={t(locale, "classroom.create")}>
          <form onSubmit={create} className="grid gap-2">
            <Field label="Nomi" name="name" required />
            <Field label="Slug" name="slug" required pattern="[a-z0-9-]+" />
            <Field label="Tavsif" name="description" />
            <div>
              <Button type="submit">{t(locale, "classroom.create")}</Button>
            </div>
          </form>
        </Card>
      </div>
      <Card title={t(locale, "nav.classroom")} bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {rooms.map((r) => (
            <li key={r.slug} className="flex items-center gap-3 px-5 py-3">
              <Link
                href={`/classroom/${r.slug}`}
                className="min-w-0 flex-1 font-medium rw-strong rw-link-hover"
              >
                {r.name}
                <span className="ml-2 text-theme-xs font-normal rw-faint">
                  @{r.owner}
                </span>
              </Link>
              <Badge>
                {r.member_count} {t(locale, "classroom.members").toLowerCase()}
              </Badge>
            </li>
          ))}
          {rooms.length === 0 && (
            <li className="px-5 py-6 text-center text-theme-sm rw-faint">
              {t(locale, "empty")}
            </li>
          )}
        </ul>
      </Card>
    </div>
  );
}
