"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";

type Mode = "login" | "register";

export function AuthForm({ mode }: { mode: Mode }) {
  const locale = DEFAULT_LOCALE;
  const router = useRouter();
  const { reload } = useSession();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setBusy(true);
    const form = new FormData(event.currentTarget);
    const payload = Object.fromEntries(form) as Record<string, string>;

    try {
      if (mode === "register") {
        await postJson("/auth/register/", payload);
        // Register sessiya ochmaydi (ADR-0008) — darhol login qilamiz.
        await postJson("/auth/login/", {
          username: payload.username,
          password: payload.password,
        });
      } else {
        await postJson("/auth/login/", payload);
      }
      // Sessiyani darhol yangilaymiz: header client komponenti bo'lgani
      // uchun `router.push` uni qayta mount qilmaydi va kirgandan keyin
      // ham «Kirish» tugmasi qolib ketardi.
      await reload();
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <Field label={t(locale, "auth.username")} name="username" required autoComplete="username" />
      {mode === "register" && (
        <Field label={t(locale, "auth.email")} name="email" type="email" required />
      )}
      <Field
        label={t(locale, "auth.password")}
        name="password"
        type="password"
        required
        autoComplete={mode === "login" ? "current-password" : "new-password"}
      />

      {error && (
        <p className="rounded-lg bg-error-50 px-3 py-2 text-theme-sm text-error-600 dark:bg-error-500/12 dark:text-error-400">
          {error}
        </p>
      )}

      <Button type="submit" disabled={busy}>
        {t(locale, mode === "login" ? "auth.login" : "auth.register")}
      </Button>

      <p className="text-center text-theme-sm text-gray-500 dark:text-gray-400">
        {t(locale, mode === "login" ? "auth.noAccount" : "auth.hasAccount")}{" "}
        <Link
          href={mode === "login" ? "/register" : "/login"}
          className="font-medium text-brand-500 hover:underline"
        >
          {t(locale, mode === "login" ? "auth.register" : "auth.login")}
        </Link>
      </p>
    </form>
  );
}
