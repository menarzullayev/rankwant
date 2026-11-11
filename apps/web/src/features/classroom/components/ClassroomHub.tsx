"use client";

import { SignInGate } from "@/components/auth/SignInGate";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { Segmented } from "@/components/ui/Segmented";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import {
  getJson,
  postJson,
  type Classroom,
  type ClassroomJoinMode,
  type ClassroomJoinResult,
} from "@/lib/api";
import { quotaFull, quotaOf, type Quota, type Quotas } from "@/lib/quotas";

import { failure } from "./failure";
import { RoleBadge } from "./RoleBadge";

/** Sinflar shaxsiy (egasi yoki a'zo) — sessiya kerak, brauzerda yuklanadi. */
export function ClassroomHub() {
  const locale = useLocale();
  const { user, ready } = useSession();
  const [rooms, setRooms] = useState<Classroom[]>([]);
  const [quota, setQuota] = useState<Quota | null>(null);
  const [mode, setMode] = useState<ClassroomJoinMode>("approval");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(() => {
    void getJson<Classroom[]>("/classrooms/")
      .then(setRooms)
      .catch(() => setRooms([]));
    void getJson<Quotas>("/me/quotas/")
      .then((all) => setQuota(quotaOf(all, "classrooms")))
      .catch(() => setQuota(null));
  }, []);
  useEffect(() => {
    if (user) load();
  }, [user, load]);

  async function create(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setNotice("");
    const form = e.currentTarget;
    try {
      await postJson("/classrooms/", { ...Object.fromEntries(new FormData(form)), join_mode: mode });
      form.reset();
      load();
    } catch (err) {
      setError(failure(locale, err));
    }
  }

  async function join(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setNotice("");
    const form = e.currentTarget;
    try {
      const result = await postJson<ClassroomJoinResult>(
        "/classrooms/join/",
        Object.fromEntries(new FormData(form)),
      );
      form.reset();
      setNotice(t(locale, result.status === "pending" ? "classroom.pending" : "classroom.joined"));
      load();
    } catch (err) {
      setError(failure(locale, err));
    }
  }

  if (ready && !user) {
    return <SignInGate reason="classroom" />;
  }

  const full = quota !== null && quotaFull(quota);

  return (
    <div className="space-y-6">
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      {notice && (
        <p role="status" className="text-theme-sm rw-ok-ink">
          {notice}
        </p>
      )}
      <div className="grid gap-4 md:grid-cols-2">
        <Card title={t(locale, "classroom.join")}>
          <form onSubmit={join} className="flex gap-2">
            <Field label={t(locale, "classroom.code")} name="join_code" required />
            <div className="flex items-end">
              <Button type="submit">{t(locale, "classroom.invite.join")}</Button>
            </div>
          </form>
        </Card>
        <Card title={t(locale, "classroom.create")}>
          <form onSubmit={create} className="grid gap-3">
            <Field label={t(locale, "admin.label.text.name")} name="name" required />
            <Field
              label={t(locale, "admin.label.text.slug")}
              name="slug"
              required
              pattern="[a-z0-9\-]+"
            />
            <Field label={t(locale, "admin.label.text.description")} name="description" />
            <div className="space-y-1">
              <Segmented<ClassroomJoinMode>
                label={t(locale, "classroom.joinMode")}
                value={mode}
                onChange={setMode}
                options={[
                  { value: "approval", label: t(locale, "classroom.joinMode.approval") },
                  { value: "instant", label: t(locale, "classroom.joinMode.instant") },
                ]}
              />
              <p className="text-theme-xs rw-dim">{t(locale, "classroom.joinMode.hint")}</p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" disabled={full}>
                {t(locale, "classroom.create")}
              </Button>
              {quota && quota.limit !== null && (
                <span className={`text-theme-xs ${full ? "rw-bad-ink" : "rw-faint"}`}>
                  {fill(t(locale, "classroom.quota"), { count: quota.used, limit: quota.limit })}
                </span>
              )}
            </div>
          </form>
        </Card>
      </div>
      <Card title={t(locale, "nav.classroom")} bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {rooms.map((r) => (
            <li key={r.slug} className="flex flex-wrap items-center gap-3 px-5 py-3">
              <Link
                href={`/classroom/${r.slug}`}
                className="min-w-0 flex-1 font-medium rw-strong rw-link-hover"
              >
                {r.name}
                <span className="ml-2 text-theme-xs font-normal rw-faint">@{r.owner}</span>
              </Link>
              {r.my_role !== "student" && <RoleBadge role={r.my_role} />}
              <Badge>{fill(t(locale, "classroom.students"), { count: r.member_count })}</Badge>
            </li>
          ))}
          {rooms.length === 0 && (
            <li className="px-5 py-6 text-center text-theme-sm rw-faint">
              {t(locale, "common.empty")}
            </li>
          )}
        </ul>
      </Card>
    </div>
  );
}
