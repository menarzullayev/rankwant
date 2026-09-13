"use client";

import type { Route } from "next";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";

/** Bitta sahifa, ikki holat: xatdagi havolada `token` bo'lsa — yangi parol,
 *  bo'lmasa — havola so'rash. Ikkalasi bir manzilda turadi, chunki
 *  foydalanuvchi uchun bu bitta ish: parolni tiklash. */
export function ResetForm() {
  const token = useSearchParams().get("token") ?? "";
  return token ? <SetNew token={token} /> : <Request />;
}

function Request() {
  const locale = useLocale();
  const [state, setState] = useState<"idle" | "busy" | "sent">("idle");
  const [error, setError] = useState("");

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setState("busy");
    const login = String(new FormData(event.currentTarget).get("login") ?? "");
    try {
      await postJson("/auth/password-reset/", { login });
      // Javob hisob bor-yo'qligini OSHKOR QILMAYDI (ADR-0015), shuning
      // uchun matn ham ikkala holatda bir xil.
      setState("sent");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.text)
          : String(err),
      );
      setState("idle");
    }
  }

  if (state === "sent") {
    return (
      <p className="text-theme-sm rw-strong">{t(locale, "reset.sent")}</p>
    );
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <p className="text-theme-sm rw-dim">{t(locale, "reset.intro")}</p>
      <Field
        label={t(locale, "reset.loginHint")}
        name="login"
        required
        autoComplete="username"
      />
      {error && (
        <p
          role="alert"
          className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink"
        >
          {error}
        </p>
      )}
      <Button type="submit" disabled={state === "busy"}>
        {t(locale, "reset.send")}
      </Button>
      <p className="text-center text-theme-sm rw-dim">
        {/* Endi bu QAYTISH emas, bo'lim almashinuvi (1-qaror): uchala
            forma bitta kartada, ya'ni odam sahifadan chiqmaydi.
            `replace` — orqaga tugmasi bo'limlar zanjirini yasamasin. */}
        <Link href={"/kirish?tab=login" as Route} className="rw-accent-ink hover:underline">
          {t(locale, "auth.login")}
        </Link>
      </p>
    </form>
  );
}

function SetNew({ token }: { token: string }) {
  const locale = useLocale();
  const [state, setState] = useState<"idle" | "busy" | "done">("idle");
  const [error, setError] = useState("");
  const [visible, setVisible] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    const password = String(form.get("password") ?? "");
    if (password !== String(form.get("password2") ?? "")) {
      setError(t(locale, "auth.passwordMismatch"));
      return;
    }
    setState("busy");
    try {
      await postJson("/auth/password-reset/confirm/", { token, password });
      setState("done");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.code === "invalid_token"
            ? t(locale, "reset.invalid")
            : errorText(locale, err.code, err.text)
          : String(err),
      );
      setState("idle");
    }
  }

  if (state === "done") {
    return (
      <div className="flex flex-col gap-4">
        <p className="text-theme-sm rw-strong">{t(locale, "reset.done")}</p>
        <Link
          href={"/kirish?tab=login" as Route}
          className="flex h-11 items-center justify-center rw-radius-sm rw-accent-bg text-theme-sm font-medium rw-accent-fg"
        >
          {t(locale, "auth.login")}
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <p className="text-theme-sm rw-dim">{t(locale, "reset.newIntro")}</p>
      <Field
        label={t(locale, "auth.password")}
        name="password"
        type={visible ? "text" : "password"}
        required
        minLength={8}
        autoComplete="new-password"
        hint={t(locale, "auth.passwordHint")}
        trailing={
          <button
            type="button"
            onClick={() => setVisible((v) => !v)}
            aria-pressed={visible}
            aria-label={t(locale, "auth.togglePassword")}
            className="grid h-9 w-9 place-items-center rw-radius-sm rw-dim transition rw-focus-ring"
          >
            {visible ? "●" : "○"}
          </button>
        }
      />
      <Field
        label={t(locale, "auth.passwordConfirm")}
        name="password2"
        type={visible ? "text" : "password"}
        required
        autoComplete="new-password"
      />
      {error && (
        <p
          role="alert"
          className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink"
        >
          {error}
        </p>
      )}
      <Button type="submit" disabled={state === "busy"}>
        {t(locale, "reset.save")}
      </Button>
    </form>
  );
}
