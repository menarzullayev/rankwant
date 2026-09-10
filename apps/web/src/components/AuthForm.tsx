"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";

type Mode = "login" | "register";

export function AuthForm({ mode }: { mode: Mode }) {
  const locale = useLocale();
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
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.text)
          : String(err),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <Field
        label={t(locale, "auth.username")}
        name="username"
        required
        autoComplete="username"
      />
      {mode === "register" && (
        <Field
          label={t(locale, "auth.email")}
          name="email"
          type="email"
          required
        />
      )}
      <Field
        label={t(locale, "auth.password")}
        name="password"
        type="password"
        required
        autoComplete={mode === "login" ? "current-password" : "new-password"}
      />

      {error && (
        <p className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}

      <Button type="submit" disabled={busy}>
        {t(locale, mode === "login" ? "auth.login" : "auth.register")}
      </Button>

      <p className="text-center text-theme-sm rw-dim">
        {t(locale, mode === "login" ? "auth.noAccount" : "auth.hasAccount")}{" "}
        <Link
          href={mode === "login" ? "/register" : "/login"}
          className="font-medium rw-accent-ink hover:underline"
        >
          {t(locale, mode === "login" ? "auth.register" : "auth.login")}
        </Link>
      </p>
    </form>
  );
}
