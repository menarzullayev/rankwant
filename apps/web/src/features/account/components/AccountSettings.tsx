"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { Status } from "@/components/ui/Status";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { date, errorText, fill, t } from "@/i18n/messages";
import { API_BASE, ApiError, deleteJson, postJson } from "@/lib/api";

const DAY_MS = 24 * 60 * 60 * 1000;

export function AccountSettings() {
  const locale = useLocale();
  const confirm = useConfirm();
  const { user, reload } = useSession();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<"export" | "delete" | "restore" | null>(null);
  // Read once per mount: a countdown that ticked would re-render the page
  // every second to change a number that moves once a day.
  const [now] = useState(() => Date.now());

  async function download() {
    setError("");
    setBusy("export");
    try {
      // `<a download>` emas: eksport sessiya cookie'sini talab qiladi va
      // shift 429 qaytarishi mumkin — bunda foydalanuvchi jimgina bo'sh
      // fayl olardi.
      const res = await fetch(`${API_BASE}/me/export/`, {
        credentials: "include",
        headers: { Accept: "application/json" },
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new ApiError(
          res.status,
          body?.error?.code ?? "error",
          body?.error?.message ?? res.statusText,
        );
      }
      const url = URL.createObjectURL(await res.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = "rankwant-export.json";
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.text)
          : String(err),
      );
    } finally {
      setBusy(null);
    }
  }

  /** Starts the 14-day wait. Nothing is removed yet, and the session stays:
   *  the page then shows the date and the way to cancel. */
  async function onDelete(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const password = String(new FormData(event.currentTarget).get("password"));
    if (
      !(await confirm(t(locale, "settings.deleteConfirmGrace"), {
        danger: true,
        kind: "modal",
      }))
    )
      return;
    setError("");
    setBusy("delete");
    try {
      await deleteJson("/me/", { password });
      await reload();
    } catch (err) {
      // 400 — faqat parol xatosi bo'lishi mumkin (boshqa maydon yo'q).
      setError(
        err instanceof ApiError
          ? err.status === 400
            ? t(locale, "settings.deleteError")
            : errorText(locale, err.code, err.text)
          : String(err),
      );
    } finally {
      setBusy(null);
    }
  }

  async function restore() {
    setError("");
    setBusy("restore");
    try {
      await postJson("/me/restore/", {});
      await reload();
    } catch (err) {
      setError(
        err instanceof ApiError ? errorText(locale, err.code, err.text) : String(err),
      );
    } finally {
      setBusy(null);
    }
  }

  const due = user?.deletion_scheduled_for ?? null;
  // Rounded, not rounded up: right after the request the gap is 14 days
  // and a few seconds, which must read "14", not "15".
  const daysLeft = due ? Math.max(0, Math.round((+new Date(due) - now) / DAY_MS)) : 0;

  return (
    <div className="space-y-6">
      {due && (
        <div
          role="status"
          className="flex flex-wrap items-center justify-between gap-3 rw-radius rw-warn-soft px-5 py-4"
        >
          <p className="text-theme-sm font-medium rw-warn-ink">
            {fill(t(locale, "settings.deletePending"), {
              date: date(due, locale),
              days: String(daysLeft),
            })}
          </p>
          <Button busy={busy === "restore"} disabled={busy !== null} onClick={restore}>
            {t(locale, "settings.deleteCancel")}
          </Button>
        </div>
      )}

      <Card title={t(locale, "settings.export")}>
        <p className="text-theme-sm rw-dim">
          {t(locale, "settings.exportHint")}
        </p>
        <Button
          variant="outline"
          className="mt-4"
          onClick={download}
          disabled={busy !== null}
        >
          {t(locale, "settings.exportAction")}
        </Button>
      </Card>

      <Card title={t(locale, "settings.delete")}>
        <p className="text-theme-sm rw-strong">{t(locale, "settings.deleteGrace")}</p>
        <p className="mt-2 text-theme-sm rw-dim">
          {t(locale, "settings.deleteHint")}
        </p>
        {due ? (
          <p className="mt-4 text-theme-sm rw-dim">{t(locale, "settings.deleteRestoreHint")}</p>
        ) : (
          <form onSubmit={onDelete} className="mt-4 flex flex-col gap-4">
            <Field
              label={t(locale, "settings.deletePassword")}
              name="password"
              type="password"
              required
              autoComplete="current-password"
            />
            <Button
              type="submit"
              variant="outline"
              className="self-start rw-bad-ink"
              disabled={busy !== null}
            >
              {t(locale, "settings.deleteStart")}
            </Button>
          </form>
        )}
        {error && (
          <div className="mt-4">
            <Status status="bad" variant="alert" alert label={error} />
          </div>
        )}
      </Card>
    </div>
  );
}
