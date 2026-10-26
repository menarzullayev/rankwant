"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Field, type FieldStatus } from "@/components/ui/Field";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";
import { fieldErrors, resetSchema } from "@rankwant/shared/validation";
import { PasswordEye, PasswordRules, StrengthBar, passwordRefusalKey } from "./PasswordFields";

const bad = (text: string | undefined): FieldStatus | undefined =>
  text ? { kind: "bad", text } : undefined;

/** Focus the first field only where there is a mouse: on a phone the keyboard
 *  would jump up and hide the heading. */
function useFineFocus() {
  const ref = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (window.matchMedia("(pointer: fine)").matches) ref.current?.focus();
  }, []);
  return ref;
}

/** Bitta sahifa, ikki holat: xatdagi havolada `token` bo'lsa — yangi parol,
 *  bo'lmasa — havola so'rash. Ikkalasi bir manzilda turadi, chunki
 *  foydalanuvchi uchun bu bitta ish: parolni tiklash. */
export function ResetForm({ token = "" }: { token?: string }) {
  return token ? <SetNew token={token} /> : <Request />;
}

function Request() {
  const locale = useLocale();
  const [state, setState] = useState<"idle" | "busy" | "sent">("idle");
  const [error, setError] = useState("");
  const first = useFineFocus();

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
    <form method="post" noValidate onSubmit={onSubmit} className="flex flex-col gap-3.5">
      <p className="text-theme-sm rw-dim">{t(locale, "reset.intro")}</p>
      <Field
        ref={first}
        label={t(locale, "reset.loginHint")}
        name="login"
        required
        autoComplete="username"
        autoCapitalize="none"
        spellCheck={false}
      />
      {error && <Status status="bad" variant="alert" alert label={error} />}
      <Button type="submit" disabled={state === "busy"}>
        {t(locale, "reset.send")}
      </Button>
      <p className="text-center text-theme-sm rw-dim">
        {/* Endi bu QAYTISH emas, bo'lim almashinuvi (1-qaror): uchala
            forma bitta kartada, ya'ni odam sahifadan chiqmaydi.
            `replace` — orqaga tugmasi bo'limlar zanjirini yasamasin. */}
        <Link
          href={"/login?tab=login" as Route}
          className="inline-flex min-h-11 items-center rw-accent-ink underline rw-focus-ring"
        >
          {t(locale, "auth.login")}
        </Link>
      </p>
    </form>
  );
}

function SetNew({ token }: { token: string }) {
  const locale = useLocale();
  const router = useRouter();
  const { reload } = useSession();
  const [busy, setBusy] = useState(false);
  const [invalid, setInvalid] = useState<{ password?: string; password2?: string }>({});
  const [error, setError] = useState("");
  const [visible, setVisible] = useState(false);
  const [pass, setPass] = useState("");
  const [refused, setRefused] = useState<string | null>(null);
  const first = useFineFocus();

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    const password = String(form.get("password") ?? "");
    const password2 = String(form.get("password2") ?? "");
    // The rules live in `@rankwant/shared/validation`; this page does not repeat them.
    const issues = fieldErrors(resetSchema.safeParse({ password, password2 }));
    if (issues.password || issues.password2) {
      setInvalid({
        password: issues.password && t(locale, issues.password),
        password2: issues.password2 && t(locale, issues.password2),
      });
      return;
    }
    setInvalid({});
    setBusy(true);
    try {
      // The link proved the mailbox: the server signs this device in and ends
      // the sessions on every other device. Reload the session and go home.
      await postJson("/auth/password-reset/confirm/", { token, password });
      await reload();
      router.push("/");
    } catch (err) {
      if (err instanceof ApiError && err.code === "invalid_token") {
        setError(t(locale, "reset.invalid"));
      } else if (err instanceof ApiError && err.code === "invalid") {
        // Django's validators answer in English with `code: "invalid"`.
        const key = passwordRefusalKey(err.text);
        setInvalid({ password: key ? t(locale, key) : err.text });
        setRefused(password);
      } else {
        setError(
          err instanceof ApiError ? errorText(locale, err.code, err.text) : String(err),
        );
      }
      setBusy(false);
    }
  }

  return (
    <form method="post" noValidate onSubmit={onSubmit} className="flex flex-col gap-3.5">
      <p className="text-theme-sm rw-dim">{t(locale, "reset.newIntro")}</p>
      <Field
        ref={first}
        label={t(locale, "auth.password")}
        name="password"
        type={visible ? "text" : "password"}
        required
        autoComplete="new-password"
        value={pass}
        onChange={(e) => {
          setPass(e.target.value);
          if (refused !== null && e.target.value !== refused) setRefused(null);
        }}
        status={bad(invalid.password)}
        trailing={<PasswordEye visible={visible} onToggle={() => setVisible((v) => !v)} />}
      />
      <PasswordRules value={pass} />
      <StrengthBar value={pass} refused={refused !== null && pass === refused} />
      <Field
        label={t(locale, "auth.passwordConfirm")}
        name="password2"
        type={visible ? "text" : "password"}
        required
        autoComplete="new-password"
        status={bad(invalid.password2)}
      />
      {error && (
        <Status status="bad" variant="alert" alert label={error}>
          {" "}
          <Link
            href={"/login?tab=reset-password" as Route}
            className="inline-flex min-h-11 items-center underline rw-focus-ring"
          >
            {t(locale, "reset.send")}
          </Link>
        </Status>
      )}
      <Button type="submit" busy={busy} busyLabel={t(locale, "reset.save")}>
        {t(locale, "reset.save")}
      </Button>
    </form>
  );
}
