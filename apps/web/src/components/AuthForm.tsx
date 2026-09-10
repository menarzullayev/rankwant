"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Field, type FieldStatus } from "@/components/ui/Field";
import { GithubMark, GoogleMark } from "@/components/ProviderMark";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError, getJson, postJson } from "@/lib/api";
import { strength } from "@/lib/password";

type Mode = "login" | "register";

/** Provayder kaliti sozlanmagan bo'lsa tugmasi umuman ko'rinmaydi —
 *  API `/auth/providers/` da faqat tayyorlarini qaytaradi (ADR-0016). */
const PROVIDER_LABEL = {
  google: "auth.withGoogle",
  github: "auth.withGithub",
  telegram: "auth.withTelegram",
} as const;

type Provider = keyof typeof PROVIDER_LABEL;

/** Brend ranglari — rasmiy tugma qoidalaridagi kabi. Ular mavzu
 *  tokenlaridan olinmaydi: brend rangi palitraga qarab o'zgarmaydi. */
const BRAND: Record<Provider, string> = {
  google: "border rw-line bg-white text-[#1f1f1f]",
  github: "bg-[#1f2328] text-white",
  telegram: "",
};

export function AuthForm({
  mode,
  providers,
  telegramBot,
}: {
  mode: Mode;
  /** Serverda olinadi — tugmalar HTML da keladi va JS ga bog'liq emas. */
  providers: string[];
  telegramBot: string;
}) {
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
  // Yozayotgandagi tekshiruv faqat ro'yxatdan o'tishda kerak: kirishda
  // nom band ekanini aytish mavjud hisoblarni sanab chiqish yo'li bo'lardi.
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [pass2, setPass2] = useState("");
  // Natija QAYSI nom uchun kelgani bilan saqlanadi: «tekshirilmoqda»
  // holati shundan hosil qilinadi va uni alohida yozib qo'yish shart
  // emas — effekt ichida holat o'rnatish qayta-qayta render chaqiradi.
  const [nameCheck, setNameCheck] = useState<{ for: string; status: FieldStatus }>();

  // Har bosilgan tugmaga so'rov yuborilmaydi: odam yozishdan
  // to'xtaganda bittasi ketadi va oldingisi bekor qilinadi — aks holda
  // «ali» yozgan odam uchun to'rtta javob qaytardi va ular tartibsiz
  // kelib, oxirgisi eskisi bo'lib qolishi mumkin edi.
  useEffect(() => {
    if (mode !== "register" || username.length < 3) return;
    const stop = new AbortController();
    const timer = setTimeout(() => {
      getJson<{ available: boolean; reason: string }>(
        `/auth/username-check/?u=${encodeURIComponent(username)}`,
        { signal: stop.signal },
      )
        .then((data) =>
          setNameCheck({
            for: username,
            status: data.available
              ? { kind: "ok", text: t(locale, "auth.usernameFree") }
              : { kind: "bad", text: data.reason },
          }),
        )
        // Tarmoq yiqilsa jim qolamiz: server baribir tekshiradi va
        // yolg'on «band» yozuvi odamni bekorga qaytarardi.
        .catch(() => undefined);
    }, 400);
    return () => {
      clearTimeout(timer);
      stop.abort();
    };
  }, [mode, username, locale]);

  const nameStatus: FieldStatus | undefined =
    mode !== "register" || username.length < 3
      ? undefined
      : nameCheck?.for === username
        ? nameCheck.status
        : { kind: "busy", text: t(locale, "auth.checking") };

  const emailStatus: FieldStatus | undefined =
    mode === "register" && email.length > 3 && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)
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
      // Yangi hisob uchun `?welcome=1` — bir martalik xabar va kod
      // kiritish maydoni shu belgi bo'yicha chiziladi.
      router.push(mode === "register" ? "/?welcome=1" : "/");
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
          // Sahifaning yagona vazifasi shu forma — kursor darhol shu
          // yerda bo'lsin.
          autoFocus
          autoComplete="username"
          minLength={mode === "register" ? 3 : undefined}
          maxLength={mode === "register" ? 30 : undefined}
          value={mode === "register" ? username : undefined}
          onChange={
            mode === "register" ? (e) => setUsername(e.target.value) : undefined
          }
          status={nameStatus}
          hint={mode === "register" ? t(locale, "auth.usernameHint") : undefined}
        />
        {mode === "register" && (
          <Field
            label={t(locale, "auth.email")}
            name="email"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            status={emailStatus}
          />
        )}
        {mode === "register" && (
          <Field
            label={t(locale, "auth.displayName")}
            name="display_name"
            autoComplete="name"
            maxLength={100}
            hint={t(locale, "auth.displayNameHint")}
          />
        )}
        <Field
          label={t(locale, "auth.password")}
          name="password"
          type={visible ? "text" : "password"}
          required
          minLength={mode === "register" ? 8 : undefined}
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          value={mode === "register" ? pass : undefined}
          onChange={mode === "register" ? (e) => setPass(e.target.value) : undefined}
          // Qoida BO'SH maydonda turadi; birinchi harfdan keyin uning
          // o'rnini kuch chizig'i egallaydi — bir vaqtda bitta satr.
          hint={mode === "register" && !pass ? t(locale, "auth.passwordHint") : undefined}
          trailing={eye}
        />
        {mode === "register" && <Strength value={pass} />}
        {mode === "register" && (
          <Field
            label={t(locale, "auth.passwordConfirm")}
            name="password2"
            type={visible ? "text" : "password"}
            required
            autoComplete="new-password"
            value={pass2}
            onChange={(e) => setPass2(e.target.value)}
            status={matchStatus}
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

        <Button
          type="submit"
          busy={busy}
          busyLabel={t(locale, mode === "login" ? "auth.loggingIn" : "auth.registering")}
        >
          {t(locale, mode === "login" ? "auth.login" : "auth.register")}
        </Button>
        {mode === "register" && <Legal />}
      </form>

      {/* Parol formasi asosiy yo'l bo'lib qoladi, ijtimoiy kirish esa
          uning ostida: ajratkich tugmalardan OLDIN turadi, aks holda u
          formadan keyin osilib qolardi. */}
      {providers.length > 0 && (
        <>
          <div className="flex items-center gap-3">
            <span className="h-px flex-1 border-t rw-line" />
            <span className="text-theme-xs rw-dim">
              {t(locale, "auth.orWith")}
            </span>
            <span className="h-px flex-1 border-t rw-line" />
          </div>
          {/* Ustma-ust uchta to'liq kenglikdagi tugma ~150px vertikal joy
              olardi va forma ekrandan pastga tushib ketardi. Ikkitasi
              yonma-yon, Telegram esa ostida: uning vidjeti Telegram niki
              va eng kichik o'lchamida ham ~110px, uchdan bir katak esa
              mobilda ~85px bo'lardi — ya'ni vidjet qirqilardi.
              Brend nomi tarjima qilinmaydi, shuning uchun matn shu yerda;
              to'liq nomi (`Google orqali davom etish`) `aria-label` da. */}
          <div className="grid grid-cols-2 gap-2">
            {providers
              .filter((p): p is Provider => p !== "telegram" && p in PROVIDER_LABEL)
              .map((p) => (
                <a
                  key={p}
                  href={`/api/v1/auth/${p}/start/`}
                  aria-label={t(locale, PROVIDER_LABEL[p])}
                  className={`flex h-11 items-center justify-center gap-2 rw-radius-sm text-theme-sm font-medium transition rw-focus-ring hover:brightness-95 ${BRAND[p]}`}
                >
                  {p === "google" ? <GoogleMark /> : <GithubMark />}
                  <span className="truncate">{p === "google" ? "Google" : "GitHub"}</span>
                </a>
              ))}
          </div>
          {providers.includes("telegram") && telegramBot && (
            <TelegramButton bot={telegramBot} />
          )}
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

/** Parol kuchi — to'rt bo'lakli chiziq va so'z.
 *
 * Rang YOLG'IZ tashuvchi emas (WCAG 1.4.1): daraja so'z bilan ham
 * yoziladi va bo'lakchalar soni ham o'zgaradi. Bu ko'rsatkich hech
 * narsani to'smaydi — qabul qilish qoidasi faqat serverda. */
function Strength({ value }: { value: string }) {
  const locale = useLocale();
  const level = strength(value);
  if (!level) return null;
  const tone = level <= 1 ? "rw-bad-ink" : level === 4 ? "rw-ok-ink" : "rw-warn-ink";
  return (
    <p className="-mt-2 flex items-center gap-2" role="status" aria-live="polite">
      <span className="flex flex-1 gap-1" aria-hidden>
        {[1, 2, 3, 4].map((step) => (
          <span
            key={step}
            className={`h-1 flex-1 rw-radius-sm ${
              step <= level ? tone.replace("-ink", "-soft") : "rw-hover-bg"
            }`}
            style={{
              background:
                step <= level
                  ? `var(--rw-${level <= 1 ? "bad" : level === 4 ? "ok" : "warn"}-ink)`
                  : "var(--rw-line)",
            }}
          />
        ))}
      </span>
      <span className={`text-theme-xs ${tone}`}>
        {t(locale, `auth.strength${level}`)}
      </span>
    </p>
  );
}

/** Shartlar va maxfiylik — matn tarjimada `{terms}` va `{privacy}`
 *  o'rinlari bilan keladi, ya'ni har bir til so'z tartibini O'ZI
 *  belgilaydi. Jumlani bo'laklab yig'ish shu sababdan. */
function Legal() {
  const locale = useLocale();
  const parts = t(locale, "auth.legal").split(/(\{terms\}|\{privacy\})/);
  return (
    <p className="text-center text-theme-xs rw-dim">
      {parts.map((part, i) =>
        part === "{terms}" ? (
          <Link key={i} href="/shartlar" className="rw-accent-ink hover:underline">
            {t(locale, "footer.terms")}
          </Link>
        ) : part === "{privacy}" ? (
          <Link key={i} href="/maxfiylik" className="rw-accent-ink hover:underline">
            {t(locale, "footer.privacy")}
          </Link>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
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

/** Telegram OAuth EMAS: u o'z widgetini chizadi va imzolangan ma'lumotni
 *  to'g'ridan-to'g'ri callback'ga yuboradi. Shu sababli bu yerda havola
 *  emas, provayderning o'z skripti turadi. */
function TelegramButton({ bot }: { bot: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const host = ref.current;
    if (!host || host.childElementCount > 0) return;
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.setAttribute("data-telegram-login", bot);
    script.setAttribute("data-size", "medium");
    script.setAttribute("data-radius", "8");
    script.setAttribute(
      "data-auth-url",
      `${window.location.origin}/api/v1/auth/telegram/callback/`,
    );
    host.appendChild(script);
  }, [bot]);

  // Vidjet Telegram niki: kengligini biz belgilay olmaymiz, shuning
  // uchun katak qolgan ikkitasi bilan bir balandlikda va markazda
  // turadi, ichidagisi esa sig'masa qisqaradi.
  return (
    <div
      ref={ref}
      className="flex h-11 items-center justify-center overflow-hidden rw-radius-sm"
    />
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
