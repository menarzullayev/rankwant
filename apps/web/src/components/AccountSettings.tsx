"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { API_BASE, ApiError, deleteJson } from "@/lib/api";

export function AccountSettings() {
  const locale = useLocale();
  const router = useRouter();
  const { clear } = useSession();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<"export" | "delete" | null>(null);

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

  async function onDelete(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!window.confirm(t(locale, "settings.deleteConfirm"))) return;
    setError("");
    setBusy("delete");
    const password = String(new FormData(event.currentTarget).get("password"));
    try {
      await deleteJson("/me/", { password });
      clear();
      router.push("/");
    } catch (err) {
      // 400 — faqat parol xatosi bo'lishi mumkin (boshqa maydon yo'q).
      setError(
        err instanceof ApiError
          ? err.status === 400
            ? t(locale, "settings.deleteError")
            : errorText(locale, err.code, err.text)
          : String(err),
      );
      setBusy(null);
    }
  }

  return (
    <div className="space-y-6">
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
        <p className="text-theme-sm rw-dim">
          {t(locale, "settings.deleteHint")}
        </p>
        <form onSubmit={onDelete} className="mt-4 flex flex-col gap-4">
          <Field
            label={t(locale, "settings.deletePassword")}
            name="password"
            type="password"
            required
            autoComplete="current-password"
          />
          {error && (
            <p className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink">
              {error}
            </p>
          )}
          <Button
            type="submit"
            variant="outline"
            className="self-start rw-bad-ink"
            disabled={busy !== null}
          >
            {t(locale, "settings.deleteAction")}
          </Button>
        </form>
      </Card>
    </div>
  );
}
