"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { deleteJson, postJson, type SessionRow } from "@/lib/api";
import { Hint, Loading, Status, useAction, useLoad } from "./kit";

function PasswordCard({ onChanged }: { onChanged: () => void }) {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  const [mismatch, setMismatch] = useState(false);
  if (!user) return null;

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const element = event.currentTarget;
    const form = new FormData(element);
    const next = String(form.get("new_password") ?? "");
    if (next !== String(form.get("confirm") ?? "")) {
      setMismatch(true);
      return;
    }
    setMismatch(false);
    const ok = await action.run(async () => {
      await postJson("/me/password/", {
        old_password: String(form.get("old_password") ?? ""),
        new_password: next,
      });
      await reload();
    });
    if (ok) {
      element.reset();
      onChanged();
    }
  }

  return (
    <Card title={t(locale, "settings.password")}>
      <form onSubmit={submit} className="flex flex-col gap-4">
        {/* Parol menejeri yangi parolni QAYSI hisobga saqlashni bilishi uchun. */}
        <input
          type="text"
          name="username"
          autoComplete="username"
          defaultValue={user.username}
          readOnly
          tabIndex={-1}
          aria-hidden="true"
          className="sr-only"
        />
        {!user.has_password && <Hint>{t(locale, "settings.passwordSetHint")}</Hint>}
        {user.has_password && (
          <Field
            label={t(locale, "settings.passwordCurrent")}
            name="old_password"
            type="password"
            required
            autoComplete="current-password"
          />
        )}
        <Field
          label={t(locale, "settings.passwordNew")}
          name="new_password"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          hint={t(locale, "auth.passwordHint")}
        />
        <Field
          label={t(locale, "auth.passwordConfirm")}
          name="confirm"
          type="password"
          required
          autoComplete="new-password"
          status={
            mismatch
              ? { kind: "bad", text: t(locale, "auth.passwordMismatch") }
              : undefined
          }
        />
        <Status
          error={action.error}
          done={action.done}
          text={t(locale, "settings.passwordDone")}
        />
        <Button type="submit" busy={action.busy} className="self-start">
          {user.has_password
            ? t(locale, "settings.passwordChange")
            : t(locale, "settings.passwordSet")}
        </Button>
      </form>
    </Card>
  );
}

function EmailCard() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const request = useAction();
  const confirm = useAction();
  const [sentTo, setSentTo] = useState("");
  if (!user) return null;
  const username = user.username;

  async function send(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") ?? "").trim();
    const ok = await request.run(() =>
      postJson("/me/email/", {
        email,
        password: String(form.get("password") ?? ""),
      }),
    );
    if (ok) setSentTo(email);
  }

  async function verify(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const ok = await confirm.run(async () => {
      await postJson("/auth/email/verify/", {
        code: String(form.get("code") ?? "").trim(),
        username,
      });
      await reload();
    });
    if (ok) setSentTo("");
  }

  return (
    <Card title={t(locale, "settings.email")}>
      <p className="flex flex-wrap items-center gap-2 text-theme-sm rw-strong">
        {user.email
          ? fill(t(locale, "settings.emailCurrent"), { email: user.email })
          : t(locale, "settings.emailNone")}
        {user.email && (
          <span
            className={`rw-radius-sm px-2 py-0.5 text-theme-xs ${
              user.email_verified
                ? "rw-ok-soft rw-ok-ink"
                : "rw-warn-soft rw-warn-ink"
            }`}
          >
            {user.email_verified
              ? t(locale, "settings.emailVerified")
              : t(locale, "settings.emailUnverified")}
          </span>
        )}
      </p>
      {confirm.done && (
        <div className="mt-3">
          <Status done text={t(locale, "settings.emailDone")} />
        </div>
      )}
      {sentTo ? (
        <form onSubmit={verify} className="mt-4 flex flex-col gap-4">
          <Hint>{fill(t(locale, "settings.emailCodeSent"), { email: sentTo })}</Hint>
          <Field
            label={t(locale, "settings.emailCode")}
            name="code"
            required
            inputMode="numeric"
            autoComplete="one-time-code"
            maxLength={6}
          />
          <Status error={confirm.error} />
          <div className="flex flex-wrap gap-2">
            <Button type="submit" busy={confirm.busy}>
              {t(locale, "settings.emailConfirm")}
            </Button>
            <Button type="button" variant="outline" onClick={() => setSentTo("")}>
              {t(locale, "admin.cancel")}
            </Button>
          </div>
        </form>
      ) : (
        <form onSubmit={send} className="mt-4 flex flex-col gap-4">
          <Hint>{t(locale, "settings.emailHint")}</Hint>
          <Field
            label={t(locale, "settings.emailNew")}
            name="email"
            type="email"
            required
            autoComplete="email"
          />
          {user.has_password && (
            <Field
              label={t(locale, "settings.passwordCurrent")}
              name="password"
              type="password"
              required
              autoComplete="current-password"
            />
          )}
          <Status error={request.error} />
          <Button type="submit" busy={request.busy} className="self-start">
            {t(locale, "settings.emailSend")}
          </Button>
        </form>
      )}
    </Card>
  );
}

/** «Chrome · Windows» — to'liq User-Agent satrini hech kim o'qimaydi. */
function describeAgent(ua: string): string {
  const browser = /Edg\//.test(ua)
    ? "Edge"
    : /OPR\//.test(ua)
      ? "Opera"
      : /YaBrowser/.test(ua)
        ? "Yandex"
        : /Firefox\//.test(ua)
          ? "Firefox"
          : /Chrome\//.test(ua)
            ? "Chrome"
            : /Safari\//.test(ua)
              ? "Safari"
              : "";
  const os = /iPhone|iPad/.test(ua)
    ? "iOS"
    : /Android/.test(ua)
      ? "Android"
      : /Windows/.test(ua)
        ? "Windows"
        : /Mac OS X/.test(ua)
          ? "macOS"
          : /Linux/.test(ua)
            ? "Linux"
            : "";
  return [browser, os].filter(Boolean).join(" · ");
}

function SessionsCard({ version }: { version: number }) {
  const locale = useLocale();
  const router = useRouter();
  const { clear } = useSession();
  // `v` — parol almashgach ro'yxat qayta so'ralishi uchun: boshqa
  // qurilmalar o'sha zahoti uziladi.
  const sessions = useLoad<SessionRow[]>(`/me/sessions/?v=${version}`);
  const action = useAction();
  const rows = sessions.data ?? [];

  async function end(row: SessionRow) {
    await action.run(async () => {
      await deleteJson(`/me/sessions/${row.id}/`);
      if (row.current) {
        clear();
        router.push("/login");
        return;
      }
      sessions.reload();
    });
  }

  return (
    <Card title={t(locale, "settings.sessions")}>
      <Hint>{t(locale, "settings.sessionsHint")}</Hint>
      {!sessions.data && !sessions.error && (
        <div className="mt-3">
          <Loading />
        </div>
      )}
      <ul className="mt-4 divide-y rw-divide">
        {rows.map((row) => (
          <li key={row.id} className="flex flex-wrap items-center gap-3 py-3">
            <div className="min-w-0 flex-1">
              <p className="flex flex-wrap items-center gap-2 text-theme-sm font-medium rw-strong">
                {describeAgent(row.user_agent) || t(locale, "settings.sessionUnknown")}
                {row.current && (
                  <span className="rw-radius-sm rw-ok-soft px-2 py-0.5 text-theme-xs rw-ok-ink">
                    {t(locale, "settings.sessionCurrent")}
                  </span>
                )}
              </p>
              <p className="text-theme-xs rw-faint">
                {[
                  row.ip,
                  fill(t(locale, "settings.sessionSeen"), {
                    time: new Date(row.last_seen).toLocaleString(locale),
                  }),
                ]
                  .filter(Boolean)
                  .join(" · ")}
              </p>
            </div>
            <Button
              variant="outline"
              className="h-9 px-3"
              disabled={action.busy}
              onClick={() => end(row)}
            >
              {t(locale, "settings.sessionEnd")}
            </Button>
          </li>
        ))}
      </ul>
      <div className="mt-2 space-y-3">
        <Status error={action.error || sessions.error} />
        {rows.some((row) => !row.current) && (
          <Button
            variant="outline"
            busy={action.busy}
            onClick={() =>
              action.run(async () => {
                await deleteJson("/me/sessions/");
                sessions.reload();
              })
            }
          >
            {t(locale, "settings.sessionEndOthers")}
          </Button>
        )}
      </div>
    </Card>
  );
}

export function SecuritySection() {
  const [version, setVersion] = useState(0);
  return (
    <>
      <PasswordCard onChanged={() => setVersion((v) => v + 1)} />
      <EmailCard />
      <SessionsCard version={version} />
    </>
  );
}
