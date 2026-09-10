"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError, getJson, postJson } from "@/lib/api";

type Mode = "login" | "register";

/** Provayder kaliti sozlanmagan bo'lsa tugmasi umuman ko'rinmaydi —
 *  API `/auth/providers/` da faqat tayyorlarini qaytaradi (ADR-0016). */
const PROVIDER_LABEL = {
  google: "auth.withGoogle",
  github: "auth.withGithub",
  telegram: "auth.withTelegram",
} as const;

type Provider = keyof typeof PROVIDER_LABEL;

export function AuthForm({ mode }: { mode: Mode }) {
  const locale = useLocale();
  const router = useRouter();
  const params = useSearchParams();
  // Provayder bizni shu ikki holatda qaytaradi: bog'lash kerak
  // (`?link=`) yoki almashuv yiqildi (`?social=`) — ADR-0016.
  const linking = params.get("link");
  const socialFailed = params.get("social");
  const { reload } = useSession();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [visible, setVisible] = useState(false);
  const [providers, setProviders] = useState<Provider[]>([]);

  useEffect(() => {
    getJson<{ providers: Provider[] }>("/auth/providers/")
      .then((data) => setProviders(data.providers))
      // Ro'yxat kelmasa forma baribir ishlaydi — parol asosiy yo'l.
      .catch(() => setProviders([]));
  }, []);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    const payload = Object.fromEntries(form) as Record<string, string>;

    if (mode === "register" && payload.password !== payload.password2) {
      setError(t(locale, "auth.passwordMismatch"));
      return;
    }
    delete payload.password2;

    setBusy(true);
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

  const eye = (
    <button
      type="button"
      onClick={() => setVisible((v) => !v)}
      aria-pressed={visible}
      aria-label={t(locale, "auth.togglePassword")}
      title={t(locale, "auth.togglePassword")}
      className="grid h-9 w-9 place-items-center rw-radius-sm rw-dim transition hover:rw-strong rw-focus-ring"
    >
      {visible ? <EyeOff /> : <Eye />}
    </button>
  );

  if (mode === "login" && linking) {
    return <LinkAccount provider={linking} />;
  }

  return (
    <div className="flex flex-col gap-5">
      {socialFailed && (
        <p
          role="alert"
          className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink"
        >
          {t(locale, "auth.socialError")}
        </p>
      )}
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <Field
          label={t(locale, "auth.username")}
          name="username"
          required
          autoComplete="username"
          minLength={mode === "register" ? 3 : undefined}
          maxLength={mode === "register" ? 20 : undefined}
          hint={mode === "register" ? t(locale, "auth.usernameHint") : undefined}
        />
        {mode === "register" && (
          <Field
            label={t(locale, "auth.email")}
            name="email"
            type="email"
            required
            autoComplete="email"
          />
        )}
        <Field
          label={t(locale, "auth.password")}
          name="password"
          type={visible ? "text" : "password"}
          required
          minLength={mode === "register" ? 8 : undefined}
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          hint={mode === "register" ? t(locale, "auth.passwordHint") : undefined}
          trailing={eye}
        />
        {mode === "register" && (
          <Field
            label={t(locale, "auth.passwordConfirm")}
            name="password2"
            type={visible ? "text" : "password"}
            required
            autoComplete="new-password"
          />
        )}

        {mode === "login" && (
          <p className="-mt-1 text-right text-theme-sm">
            <Link
              href="/parolni-tiklash"
              className="rw-accent-ink hover:underline"
            >
              {t(locale, "auth.forgot")}
            </Link>
          </p>
        )}

        {error && (
          <p
            role="alert"
            className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink"
          >
            {error}
          </p>
        )}

        <Button type="submit" disabled={busy}>
          {t(locale, mode === "login" ? "auth.login" : "auth.register")}
        </Button>
      </form>

      {providers.length > 0 && (
        <>
          <div className="flex items-center gap-3">
            <span className="h-px flex-1 border-t rw-line" />
            <span className="text-theme-xs rw-dim">
              {t(locale, "auth.orWith")}
            </span>
            <span className="h-px flex-1 border-t rw-line" />
          </div>
          <div className="flex flex-col gap-2">
            {providers.map((p) => (
              <a
                key={p}
                href={`/api/v1/auth/${p}/start/`}
                className="flex h-11 items-center justify-center gap-2 rw-radius-sm border rw-line text-theme-sm font-medium rw-strong transition rw-hover-bg rw-focus-ring"
              >
                {t(locale, PROVIDER_LABEL[p])}
              </a>
            ))}
          </div>
        </>
      )}

      <p className="text-center text-theme-sm rw-dim">
        {t(locale, mode === "login" ? "auth.noAccount" : "auth.hasAccount")}{" "}
        <Link
          href={mode === "login" ? "/register" : "/login"}
          className="font-medium rw-accent-ink hover:underline"
        >
          {t(locale, mode === "login" ? "auth.register" : "auth.login")}
        </Link>
      </p>
    </div>
  );
}

/** Bog'lash HECH QACHON avtomatik emas: emailni tasdiqlash majburiy
 *  emas, ya'ni tasdiqlanmagan begona manzil bilan ochilgan hisob o'sha
 *  manzilning haqiqiy egasiga ochib berilardi (ADR-0016). */
function LinkAccount({ provider }: { provider: string }) {
  const locale = useLocale();
  const router = useRouter();
  const { reload } = useSession();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setBusy(true);
    const password = String(
      new FormData(event.currentTarget).get("password") ?? "",
    );
    try {
      await postJson("/auth/link/", { password });
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
      <p className="text-theme-sm rw-strong">{t(locale, "auth.linkTitle")}</p>
      <p className="text-theme-sm rw-dim">
        {t(locale, "auth.linkBody")} ({provider})
      </p>
      <Field
        label={t(locale, "auth.password")}
        name="password"
        type="password"
        required
        autoComplete="current-password"
      />
      {error && (
        <p
          role="alert"
          className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink"
        >
          {error}
        </p>
      )}
      <Button type="submit" disabled={busy}>
        {t(locale, "auth.linkCta")}
      </Button>
      <p className="text-center text-theme-sm">
        <Link href="/parolni-tiklash" className="rw-accent-ink hover:underline">
          {t(locale, "auth.forgot")}
        </Link>
      </p>
    </form>
  );
}

function Eye() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

function EyeOff() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M2 12s3.6-7 10-7c2 0 3.8.7 5.3 1.6M22 12s-3.6 7-10 7c-2 0-3.8-.7-5.3-1.6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <path
        d="m4 4 16 16"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}
