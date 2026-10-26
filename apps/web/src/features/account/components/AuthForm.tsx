"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Field, type FieldStatus } from "@/components/ui/Field";
import { Checkbox } from "@/components/ui/SelectField";
import { Status } from "@/components/ui/Status";
import { GithubMark, GoogleMark, TelegramMark } from "@/features/account";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";
import { track } from "@/lib/analytics";
import {
  fieldErrors,
  loginSchema,
  optionalUsernameError,
  signUpSchema,
  type RuleKey,
} from "@rankwant/shared/validation";
import { Turnstile } from "@/features/auth";
import { safeNext } from "@/lib/site";
import { useUsernameCheck } from "../useUsernameCheck";
import { PasswordEye, PasswordRules, StrengthBar, passwordRefusalKey } from "./PasswordFields";

type Mode = "login" | "register";

/** Provayder kaliti sozlanmagan bo'lsa tugmasi umuman ko'rinmaydi —
 *  API `/auth/providers/` da faqat tayyorlarini qaytaradi (ADR-0016). */
const PROVIDER_LABEL = {
  google: "auth.withGoogle",
  github: "auth.withGithub",
  telegram: "auth.withTelegram",
} as const;

type Provider = keyof typeof PROVIDER_LABEL;

/** Inputs that can carry their own error. */
type FieldName =
  | "identifier"
  | "first_name"
  | "last_name"
  | "email"
  | "username"
  | "password"
  | "password2";

const bad = (text: string | undefined): FieldStatus | undefined =>
  text ? { kind: "bad", text } : undefined;

/** Brend nomi — tarjima qilinmaydi (Codeforces ham «Div. 2» ni
 *  tarjima qilmaydi). Matn shu yerda turadi, to'liq nomi esa
 *  `aria-label` da. */
const PROVIDER_NAME: Record<Provider, string> = {
  google: "Google",
  github: "GitHub",
  telegram: "Telegram",
};

/** Tugma tartibi — Telegram BIRINCHI va to'liq kenglikda (10-qaror).
 *
 *  Sabab raqamda: yettita raqobatchi saytdan birortasida Telegram yo'q,
 *  o'zbek auditoriyasida esa u asosiy messenjer. Ya'ni bu bizning
 *  farqimiz va u birinchi ko'rinishi kerak — Google/GitHub esa ilgari
 *  birinchi turardi va Telegram faqat ostida qolib ketardi. */
const PROVIDER_ORDER: Provider[] = ["telegram", "google", "github"];

/** Brend ranglari — rasmiy tugma qoidalaridagi kabi. Ular mavzu
 *  tokenlaridan olinmaydi: brend rangi palitraga qarab o'zgarmaydi.
 *
 *  Telegram niki ATAYLAB quyuqlashtirilgan: brend ko'ki `#229ED9` oq matn
 *  bilan 3.02:1 beradi, ya'ni AA (4.5) dan yiqiladi. Ohang saqlanib
 *  yorqinlik tushirildi — `#1a77a4` = 4.95:1. Dizayn tokenlaridagi
 *  `--rw-accent` bilan bir xil yondashuv. */
const BRAND: Record<Provider, string> = {
  // `rw-divider`, not `rw-line`: `--rw-line` is transparent in the `clay`
  // style, so a white button on a near-white ground had no visible edge.
  google: "border rw-divider bg-white text-[#1f1f1f]",
  // The edge only shows in dark mode: #1f2328 on a dark ground has no
  // outline of its own. In light mode the border stays transparent.
  github: "border border-transparent bg-[#1f2328] text-white dark:border-[var(--rw-divider)]",
  telegram: "bg-[#1a77a4] text-white",
};

export function AuthForm({
  mode,
  providers,
  turnstileSiteKey = "",
  next: nextRaw,
  link,
  social,
}: {
  mode: Mode;
  /** Read on the server, so the buttons are in the HTML and do not wait for JS. */
  providers: string[];
  /** Turnstile site key. Empty: the check is not configured. */
  turnstileSiteKey?: string;
  /** `?next=` is read on the server: a client search-params hook pushed the
   *  whole form into a Suspense fallback and drew a skeleton first. */
  next?: string | null;
  /** Provider linking (`?link=`) — ADR-0016. */
  link?: string | null;
  /** The exchange failed (`?social=`). */
  social?: string | null;
}) {
  const locale = useLocale();
  const router = useRouter();
  const linking = link ?? null;
  const socialFailed = social ?? null;
  // Only an internal path passes `safeNext`; anything else would be an open redirect.
  const next = safeNext(nextRaw ?? null);
  const { reload } = useSession();
  const [error, setError] = useState("");
  // Seconds left of a lock (`Retry-After`). While it runs the button counts down.
  const [retryAfter, setRetryAfter] = useState(0);
  const [busy, setBusy] = useState(false);
  const [visible, setVisible] = useState(false);
  const [email, setEmail] = useState("");
  // Optional handle on step 1, controlled so its free/taken note can follow it.
  const [handle, setHandle] = useState("");
  const [pass, setPass] = useState("");
  const [pass2, setPass2] = useState("");
  // The password the server turned down: the strength bar never rates it above "very weak".
  const [refusedPass, setRefusedPass] = useState<string | null>(null);
  // "Remember me" is off by default: a shared computer must not stay signed in.
  const [remember, setRemember] = useState(false);
  // The Turnstile token may be empty (check not configured, script not loaded):
  // the server decides.
  const [captcha, setCaptcha] = useState("");
  // The e-mail is taken: show the two ways out (sign in / reset).
  const [blocked, setBlocked] = useState<{ kind: "email" } | null>(null);
  // Errors sit ON their field (`aria-invalid` + note), not in one alert under the form.
  const [invalid, setInvalid] = useState<Partial<Record<FieldName, string>>>({});
  // Step-1 handle note, strongest first: a refusal from the last submit, then a
  // format problem, then the live free/taken answer. The format is judged
  // locally, so a malformed name never costs a request.
  const handleFormat = optionalUsernameError(handle);
  const handleLive = useUsernameCheck(handle, mode === "register" && !handleFormat);
  const handleStatus =
    bad(invalid.username) ??
    (handleFormat && handle.trim().length >= 3
      ? bad(t(locale, handleFormat))
      : handleLive);
  // "Form started" is sent once; sending it on every focus would swell the funnel.
  const started = useRef(false);
  // Autofocus only where there is a mouse: on a phone the keyboard would jump up
  // and cover the brand and the heading.
  const firstField = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (window.matchMedia("(pointer: fine)").matches) firstField.current?.focus();
  }, [mode]);

  useEffect(() => {
    if (retryAfter <= 0) return;
    const timer = setTimeout(() => setRetryAfter((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [retryAfter]);

  const emailStatus: FieldStatus | undefined =
    mode === "register" && email.length > 3 && fieldErrors(signUpSchema.safeParse({
      first_name: "x",
      last_name: "x",
      email,
      password: "dummy-pass",
      password2: "dummy-pass",
    })).email
      ? { kind: "bad", text: t(locale, "auth.emailInvalid") }
      : undefined;

  const matchStatus: FieldStatus | undefined = !pass2
    ? undefined
    : pass === pass2
      ? { kind: "ok", text: t(locale, "auth.passwordMatch") }
      : { kind: "bad", text: t(locale, "auth.passwordMismatch") };

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setBlocked(null);
    const formEl = event.currentTarget;
    const payload = Object.fromEntries(new FormData(formEl)) as Record<string, string>;

    // Rules live in `@rankwant/shared/validation`; the page does not repeat them.
    const issues =
      mode === "register"
        ? fieldErrors(
            signUpSchema.safeParse({
              first_name: payload.first_name ?? "",
              last_name: payload.last_name ?? "",
              email: payload.email ?? "",
              password: payload.password ?? "",
              password2: payload.password2 ?? "",
            }),
          )
        : fieldErrors(
            loginSchema.safeParse({
              identifier: payload.identifier ?? "",
              password: payload.password ?? "",
            }),
          );
    // The handle is optional on step 1: only a typed one is checked.
    const handleIssue =
      mode === "register" ? optionalUsernameError(payload.username ?? "") : undefined;
    const all: Partial<Record<FieldName, RuleKey>> = {
      ...issues,
      ...(handleIssue ? { username: handleIssue } : {}),
    };
    const order: FieldName[] =
      mode === "register"
        ? ["first_name", "last_name", "email", "username", "password", "password2"]
        : ["identifier", "password"];
    const failed = order.filter((name) => all[name]);
    if (failed.length) {
      setInvalid(Object.fromEntries(failed.map((name) => [name, t(locale, all[name]!)])));
      formEl.querySelector<HTMLInputElement>(`[name="${failed[0]}"]`)?.focus();
      track("auth.form_error", { mode, reason: all[failed[0]] });
      return;
    }
    setInvalid({});

    setBusy(true);
    try {
      if (mode === "register") {
        // Consent is the text under the button (browsewrap): registering is
        // the act, and the server stamps the time. A blank handle gets a
        // temporary one and the next step asks again.
        const typed = (payload.username ?? "").trim();
        await postJson("/auth/register/", {
          email: payload.email,
          first_name: payload.first_name.trim(),
          last_name: payload.last_name.trim(),
          ...(typed ? { username: typed } : {}),
          password: payload.password,
          // The page language: the confirmation e-mail goes out in it.
          locale,
          turnstile_token: captcha,
        });
        // Register opens no session (ADR-0008): sign in with this very e-mail.
        await postJson("/auth/login/", {
          identifier: payload.email,
          password: payload.password,
        });
      } else {
        // `identifier` is the handle OR the e-mail.
        await postJson("/auth/login/", {
          identifier: payload.identifier,
          password: payload.password,
          remember,
        });
      }
      // Reload the session at once: the header is a client component, and
      // `router.push` would leave "Sign in" showing after the sign-in.
      await reload();
      // Sent BEFORE `router.push`; `keepalive` lets it arrive after the page changes.
      track(mode === "register" ? "auth.register_done" : "auth.login_done", { mode });
      // After sign-up, step 2 (`/onboarding`); `next` rides along so the
      // destination is not lost on the detour.
      router.push(
        (mode === "register"
          ? `/onboarding?welcome=1${next ? `&next=${encodeURIComponent(next)}` : ""}`
          : (next ?? "/")) as Route,
      );
    } catch (err) {
      // Only the API code is sent, never the text: it may contain what the
      // person typed (an e-mail).
      track("auth.form_error", {
        mode,
        reason: err instanceof ApiError ? err.code : "network",
      });
      setRetryAfter(err instanceof ApiError ? err.retryAfter : 0);
      if (mode === "register" && err instanceof ApiError) {
        // A refusal belongs to its field, in the page language.
        const refused: Partial<Record<FieldName, string>> = {};
        if (err.field("email") !== null) {
          refused.email = t(locale, "auth.emailTaken");
          setBlocked({ kind: "email" });
        }
        if (err.field("username") !== null) refused.username = t(locale, "auth.usernameTaken");
        // The server lists every rule the password broke; say each one, in the page language.
        const reasons = err.details.password;
        if (Array.isArray(reasons) && reasons.length) {
          refused.password = reasons
            .filter((reason): reason is string => typeof reason === "string")
            .map((reason) => {
              const key = passwordRefusalKey(reason);
              return key ? t(locale, key) : reason;
            })
            .join(" ");
          setRefusedPass(String(payload.password ?? ""));
        }
        const firstRefused = (["email", "username", "password"] as const).find(
          (name) => refused[name],
        );
        if (firstRefused) {
          setInvalid(refused);
          formEl.querySelector<HTMLInputElement>(`[name="${firstRefused}"]`)?.focus();
          return;
        }
      }
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.text)
          : String(err),
      );
    } finally {
      setBusy(false);
    }
  }

  const eye = <PasswordEye visible={visible} onToggle={() => setVisible((v) => !v)} />;

  if (mode === "login" && linking) {
    return <LinkAccount provider={linking} />;
  }

  const wait = `${Math.floor(retryAfter / 60)}:${String(retryAfter % 60).padStart(2, "0")}`;

  return (
    <div className="flex flex-col gap-4">
      {socialFailed && (
        <Status status="bad" variant="alert" alert label={t(locale, "auth.socialError")} />
      )}
      <form
        onSubmit={onSubmit}
        // `noValidate`: the browser's own bubbles ("Please fill out this field")
        // are in the browser's language and cover our notes. Ours sit on the
        // field, in the page language, with `aria-invalid`.
        noValidate
        // POST, not the default GET: before hydration (or with JS off) a
        // native submit would put `?identifier=…&password=…` in the URL,
        // and from there in history and server logs.
        method="post"
        // The first typed character is "form started". Not `onFocus`: the
        // page opens with a field focused, so opening would count as intent.
        onInput={() => {
          if (Object.keys(invalid).length) setInvalid({});
          if (started.current) return;
          started.current = true;
          track("auth.form_started", { mode });
        }}
        className="flex flex-col gap-3.5"
      >
        {mode === "register" ? (
          <>
            <div className="grid gap-3.5 sm:grid-cols-2">
              <Field
                ref={firstField}
                label={t(locale, "settings.firstName")}
                name="first_name"
                required
                autoComplete="given-name"
                maxLength={80}
                placeholder={t(locale, "auth.firstNamePlaceholder")}
                status={bad(invalid.first_name)}
              />
              <Field
                label={t(locale, "settings.lastName")}
                name="last_name"
                required
                autoComplete="family-name"
                maxLength={80}
                placeholder={t(locale, "auth.lastNamePlaceholder")}
                status={bad(invalid.last_name)}
              />
            </div>
            <Field
              label={t(locale, "auth.email")}
              name="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoCapitalize="none"
              spellCheck={false}
              placeholder={t(locale, "auth.emailPlaceholder")}
              status={bad(invalid.email) ?? emailStatus}
            />
            {blocked?.kind === "email" && (
              <p className="-mt-2 text-theme-sm rw-dim">
                <Link
                  href={"/login?tab=login" as Route}
                  className="inline-flex min-h-11 items-center rw-accent-ink underline rw-focus-ring"
                >
                  {t(locale, "auth.tabLogin")}
                </Link>
                {" · "}
                <Link
                  href={"/login?tab=reset-password" as Route}
                  className="inline-flex min-h-11 items-center rw-accent-ink underline rw-focus-ring"
                >
                  {t(locale, "auth.tabReset")}
                </Link>
              </p>
            )}
            <Field
              label={t(locale, "auth.usernameOptional")}
              name="username"
              autoComplete="username"
              maxLength={30}
              autoCapitalize="none"
              spellCheck={false}
              value={handle}
              onChange={(e) => {
                setHandle(e.target.value);
                if (invalid.username) setInvalid((prev) => ({ ...prev, username: undefined }));
              }}
              placeholder={t(locale, "auth.usernamePlaceholder")}
              hint={t(locale, "auth.usernameOptionalHint")}
              status={handleStatus}
            />
          </>
        ) : (
          <Field
            ref={firstField}
            label={t(locale, "auth.usernameOrEmail")}
            name="identifier"
            required
            // `username` covers both a handle and an e-mail in a password manager.
            autoComplete="username"
            autoCapitalize="none"
            spellCheck={false}
            placeholder={t(locale, "auth.usernamePlaceholder")}
            status={bad(invalid.identifier)}
          />
        )}
        <Field
          label={t(locale, "auth.password")}
          name="password"
          type={visible ? "text" : "password"}
          required
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          value={mode === "register" ? pass : undefined}
          onChange={
            mode === "register"
              ? (e) => {
                  setPass(e.target.value);
                  if (refusedPass !== null && e.target.value !== refusedPass) setRefusedPass(null);
                }
              : undefined
          }
          status={bad(invalid.password)}
          trailing={eye}
          // "Forgot password?" sits on the label row, where the eye looks for it.
          labelAction={
            mode === "login" ? (
              <Link
                href={"/login?tab=reset-password" as Route}
                className="inline-flex min-h-11 items-center text-theme-sm rw-accent-ink underline rw-focus-ring"
              >
                {t(locale, "auth.forgot")}
              </Link>
            ) : undefined
          }
        />
        {mode === "register" && <PasswordRules value={pass} />}
        {mode === "register" && (
          <StrengthBar value={pass} refused={refusedPass !== null && pass === refusedPass} />
        )}
        {mode === "register" && (
          <Field
            label={t(locale, "auth.passwordConfirm")}
            name="password2"
            type={visible ? "text" : "password"}
            required
            autoComplete="new-password"
            value={pass2}
            onChange={(e) => setPass2(e.target.value)}
            status={bad(invalid.password2) ?? matchStatus}
          />
        )}

        {mode === "login" && (
          <Checkbox
            name="remember"
            // `py-3`: the label is the tap target; a bare 20 px row is under 44 px.
            className="-mt-1 py-3"
            checked={remember}
            onChange={(e) => setRemember(e.target.checked)}
          >
            {t(locale, "auth.remember")}
          </Checkbox>
        )}

        {error && (
          // No `aria-live`: `role="alert"` already announces; both would read it twice.
          <Status status="bad" variant="alert" alert label={error}>
            {retryAfter >= 60 && (
              <>
                {" "}
                {t(locale, "auth.throttledWaitMinutes").replace(
                  "{minutes}",
                  String(Math.ceil(retryAfter / 60)),
                )}
              </>
            )}
            {retryAfter > 0 && retryAfter < 60 && (
              <>
                {" "}
                {t(locale, "auth.throttledWait").replace("{seconds}", String(retryAfter))}
              </>
            )}
            {retryAfter > 0 && mode === "login" && (
              // The lock holds the sign-in, not the reset: a person locked out
              // by someone else's guesses can still get in.
              <>
                {" "}
                <Link
                  href={"/login?tab=reset-password" as Route}
                  className="inline-flex min-h-11 items-center underline rw-focus-ring"
                >
                  {t(locale, "auth.tabReset")}
                </Link>
              </>
            )}
          </Status>
        )}

        {/* Turnstile on sign-up only: opening an account is the bot target;
            sign-in already has the password and the throttle. */}
        {mode === "register" && (
          <Turnstile siteKey={turnstileSiteKey} locale={locale} onToken={setCaptcha} />
        )}

        <Button
          type="submit"
          // The server would refuse anyway; a click would only make a 429.
          disabled={retryAfter > 0}
          busy={busy}
          busyLabel={t(locale, mode === "login" ? "auth.loggingIn" : "auth.registering")}
        >
          {retryAfter > 0
            ? t(locale, "auth.waitButton").replace("{time}", wait)
            : t(locale, mode === "login" ? "auth.login" : "auth.createAccount")}
        </Button>
        {/* The only place the legal text appears (2026-10-26): consent for the
            e-mail form and for the buttons below. the consent time is
            written from it, so it must stay next to the button. */}
        <Legal />
      </form>

      {providers.length > 0 && (
        <>
          <div className="flex items-center gap-3">
            <span className="h-px flex-1 border-t rw-divider" />
            <span className="text-theme-xs rw-dim">{t(locale, "auth.orWith")}</span>
            <span className="h-px flex-1 border-t rw-divider" />
          </div>
          {/* Three full-width 44 px buttons, icon + name. The brand name is not
              translated; the full phrase is the `aria-label`. */}
          <div className="flex flex-col gap-2">
            {PROVIDER_ORDER.filter((p) => providers.includes(p)).map((p) => (
              <a
                key={p}
                // `next` goes to the provider too: the server keeps it in the
                // session and returns the person there from the callback.
                href={`/api/v1/auth/${p}/start/${
                  next ? `?next=${encodeURIComponent(next)}` : ""
                }`}
                aria-label={t(locale, PROVIDER_LABEL[p])}
                className={`flex h-11 items-center justify-center gap-2 rw-radius-sm text-theme-sm font-medium transition rw-focus-ring hover:brightness-95 ${BRAND[p]}`}
              >
                {p === "telegram" ? <TelegramMark /> : p === "google" ? <GoogleMark /> : <GithubMark />}
                <span className="truncate">{PROVIDER_NAME[p]}</span>
              </a>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

/** Shartlar va maxfiylik havolalari — matn tarjimada `{terms}` va
 *  `{privacy}` o'rinlari bilan keladi, ya'ni har bir til so'z tartibini
 *  O'ZI belgilaydi. Jumlani bo'laklab yig'ish shu sababdan.
 *
 *  Ikki joyda ishlatiladi, chunki sahifada ikki xil rozilik nuqtasi bor:
 *  majburiy checkbox (`auth.termsAccept`) — email bilan ro'yxat uchun,
 *  ijtimoiy tugmalar ostidagi matn (`auth.socialConsent`) — OAuth uchun.
 *  Har biri o'z nuqtasida hujjatga ishora qiladi; footer'dagi havolalar
 *  esa umumiy navigatsiya.
 *
 *  Havolalar DOIMIY tagchiziq bilan chiziladi. Sabab WCAG 1.4.1: ular
 *  matn ICHIDA turadi va atrofdagi so'zdan faqat rang bilan ajralsa,
 *  farq 1.24:1 bo'ladi (talab 3:1) — ya'ni rang ko'rmaydigan odam uchun
 *  havola umuman bilinmaydi. Lighthouse buni `link-in-text-block` deb
 *  belgilaydi. `.rw-md a` ham xuddi shu sababdan tagchiziqli. */
function LegalLinks({ messageKey }: { messageKey: "auth.socialConsent" }) {
  const locale = useLocale();
  const parts = t(locale, messageKey).split(/(\{terms\}|\{privacy\})/);
  return (
    <>
      {/* YANGI OYNADA: hujjat o'sha oynada ochilsa, yarim to'ldirilgan
          forma yo'qoladi va odam email bilan parolni qaytadan yozadi. */}
      {parts.map((part, i) =>
        part === "{terms}" ? (
          <Link
            key={i}
            href="/terms"
            target="_blank"
            rel="noreferrer"
            // `py-3.5`: an inline link is as tall as its line (15 px); the
            // padding makes the tap area 44 px without changing the layout.
            className="rw-accent-ink underline py-3.5"
          >
            {t(locale, "footer.terms")}
          </Link>
        ) : part === "{privacy}" ? (
          <Link
            key={i}
            href="/privacy"
            target="_blank"
            rel="noreferrer"
            className="rw-accent-ink underline py-3.5"
          >
            {t(locale, "footer.privacy")}
          </Link>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </>
  );
}

function Legal() {
  return (
    <p className="text-center text-theme-xs rw-dim">
      <LegalLinks messageKey="auth.socialConsent" />
    </p>
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
    <form method="post" onSubmit={onSubmit} className="flex flex-col gap-4">
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
        <Status status="bad" variant="alert" alert label={error} />
      )}
      <Button type="submit" disabled={busy}>
        {t(locale, "auth.linkCta")}
      </Button>
      <p className="text-center text-theme-sm">
        <Link
          href={"/login?tab=reset-password" as Route}
          className="rw-accent-ink underline"
        >
          {t(locale, "auth.forgot")}
        </Link>
      </p>
    </form>
  );
}


