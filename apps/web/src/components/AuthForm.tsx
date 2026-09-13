"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Field, type FieldStatus } from "@/components/ui/Field";
import { Checkbox } from "@/components/ui/SelectField";
import { GithubMark, GoogleMark, TelegramMark } from "@/components/ProviderMark";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";
import { track } from "@/lib/analytics";
import { strength } from "@/lib/password";
import { Turnstile } from "@/components/auth/Turnstile";
import { safeNext } from "@/lib/site";

type Mode = "login" | "register";

/** Provayder kaliti sozlanmagan bo'lsa tugmasi umuman ko'rinmaydi —
 *  API `/auth/providers/` da faqat tayyorlarini qaytaradi (ADR-0016). */
const PROVIDER_LABEL = {
  google: "auth.withGoogle",
  github: "auth.withGithub",
  telegram: "auth.withTelegram",
} as const;

type Provider = keyof typeof PROVIDER_LABEL;

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
  google: "border rw-line bg-white text-[#1f1f1f]",
  github: "bg-[#1f2328] text-white",
  telegram: "bg-[#1a77a4] text-white",
};

export function AuthForm({
  mode,
  providers,
  turnstileSiteKey = "",
}: {
  mode: Mode;
  /** Serverda olinadi — tugmalar HTML da keladi va JS ga bog'liq emas. */
  providers: string[];
  /** Turnstile sayt kaliti (9-qaror). Bo'sh — tekshiruv sozlanmagan. */
  turnstileSiteKey?: string;
}) {
  const locale = useLocale();
  const router = useRouter();
  const params = useSearchParams();
  // Provayder bizni shu ikki holatda qaytaradi: bog'lash kerak
  // (`?link=`) yoki almashuv yiqildi (`?social=`) — ADR-0016.
  const linking = params.get("link");
  const socialFailed = params.get("social");
  // Himoyalangan sahifadan uchirilgan odam qayerga qaytishi kerak
  // (qaror 1). `safeNext` faqat ichki yo'lni o'tkazadi — aks holda bu
  // ochiq redirect bo'lardi.
  const next = safeNext(params.get("next"));
  const { reload } = useSession();
  const [error, setError] = useState("");
  //: Bloklanish qolgan soniyalar (`Retry-After`). Nolga tushgach qayta
  //: urinish mumkin (15-qaror) — server ham, tugma ham shuni kutadi.
  const [retryAfter, setRetryAfter] = useState(0);
  const [busy, setBusy] = useState(false);
  const [visible, setVisible] = useState(false);
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [pass2, setPass2] = useState("");
  //: Shartlar va maxfiylik — MAJBURIY (qaror 13). Ataylab `false` dan
  //: boshlanadi: oldindan belgilangan katak rozilik hisoblanmaydi.
  const [terms, setTerms] = useState(false);
  //: Marketing — IXTIYORIY va alohida (GDPR 7-modda).
  const [marketing, setMarketing] = useState(false);
  //: «Meni eslab qol» — kirishda (qaror 7). Standart `false`: umumiy
  //: kompyuterda hisob ochiq qolmasligi kerak.
  const [remember, setRemember] = useState(false);
  //: Turnstile tokeni (9-qaror). Bo'sh bo'lishi MUMKIN: tekshiruv
  //: sozlanmagan yoki skript yuklanmagan — qarorni server beradi.
  const [captcha, setCaptcha] = useState("");
  //: Server maydon xatosi (14-qaror). `email` — band pochta, ya'ni
  //: «kirish YOKI tiklash» yo'lini ko'rsatish kerak. Maydon nomi
  //: bo'yicha ajratiladi: DRF maydon xatosida `code` har doim
  //: `"invalid"` bo'ladi va uni sabab bilan chalkashtirib bo'lmaydi.
  const [blocked, setBlocked] = useState<{ kind: "email" } | null>(null);
  //: «Forma boshlandi» hodisasi BIR MARTA yuboriladi (qaror 17). Har
  //: fokusda yuborilsa funnel shishib ketardi va raqam ma'nosini
  //: yo'qotardi.
  const started = useRef(false);

  //: Bloklanish taymeri. Har soniyada bitta qayta render, lekin faqat
  //: bloklangan paytda — `retryAfter` nolga tushgach effekt to'xtaydi.
  useEffect(() => {
    if (retryAfter <= 0) return;
    const timer = setTimeout(() => setRetryAfter((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [retryAfter]);

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
      track("auth.form_error", { mode, reason: "password_mismatch" });
      return;
    }
    delete payload.password2;

    // Rozilik serverda ham tekshiriladi (`validate_terms_accepted`), lekin
    // bu yerda ham to'xtatamiz: aks holda odam butun formani to'ldirib,
    // oxirida xato ko'rardi — sababi esa boshidagi katak edi.
    if (mode === "register" && !terms) {
      setError(t(locale, "auth.termsRequired"));
      track("auth.form_error", { mode, reason: "terms" });
      return;
    }

    setBusy(true);
    try {
      if (mode === "register") {
        // 1-qadam faqat TO'RT maydon (3-qaror): email, parol, tasdiq,
        // rozilik. Foydalanuvchi nomi, ism va joy 2-qadamda
        // (`/onboarding`) so'raladi — server ularni ixtiyoriy
        // deb biladi va nom berilmasa vaqtinchalik nom qo'yadi.
        await postJson("/auth/register/", {
          email: payload.email,
          password: payload.password,
          terms_accepted: terms,
          marketing_opt_in: marketing,
          turnstile_token: captcha,
        });
        // Register sessiya ochmaydi (ADR-0008) — darhol login qilamiz.
        // Aynan SHU email bilan, ya'ni yangi `identifier` maydoni
        // orqali: nom hali tanlanmagan.
        await postJson("/auth/login/", {
          identifier: payload.email,
          password: payload.password,
        });
      } else {
        // `identifier` — foydalanuvchi nomi YOKI email (4-qaror).
        await postJson("/auth/login/", {
          identifier: payload.identifier,
          password: payload.password,
          remember,
        });
      }
      // Sessiyani darhol yangilaymiz: header client komponenti bo'lgani
      // uchun `router.push` uni qayta mount qilmaydi va kirgandan keyin
      // ham «Kirish» tugmasi qolib ketardi.
      await reload();
      // Muvaffaqiyat hodisasi `router.push` dan OLDIN yuboriladi:
      // `keepalive` tufayli sahifa almashgach ham yetib boradi.
      //
      // `country` ENDI YUBORILMAYDI: mamlakat 1-qadamda so'ralmaydi
      // (3-qaror), ya'ni hodisada u har doim `undefined` bo'lardi —
      // bo'sh o'lchov qatorini to'plashning ma'nosi yo'q.
      track(mode === "register" ? "auth.register_done" : "auth.login_done", {
        mode,
      });
      // Ro'yxatdan keyin 2-qadam (qaror 3): joy va maktab ixtiyoriy
      // so'raladi. `?welcome=1` o'sha yerga o'tadi va 2-qadamdan keyin
      // bosh sahifada bir martalik xabar bo'lib chiqadi — aks holda
      // yangi hisob egasi uni umuman ko'rmasdi.
      //
      // `next` 2-qadamga KO'TARILADI: ro'yxatdan o'tish odamni oraliq
      // qadamga olib kirdi, lekin maqsadi boshqa sahifa edi. Uni shu
      // yerda yo'qotib qo'ysak, qaytish manzili ma'nosiz qolardi.
      router.push(
        (mode === "register"
          ? `/onboarding?welcome=1${
              next ? `&next=${encodeURIComponent(next)}` : ""
            }`
          : (next ?? "/")) as Route,
      );
    } catch (err) {
      // Xato MATNI yuborilmaydi: u foydalanuvchi kiritgan ma'lumotni
      // (masalan emailni) o'z ichiga olishi mumkin. Faqat API kodi.
      track("auth.form_error", {
        mode,
        reason: err instanceof ApiError ? err.code : "network",
      });
      // Bloklanish (15-qaror): server qancha kutishni AYTADI
      // (`Retry-After`), ya'ni sahifa taxmin qilmaydi. Sarlavhani
      // o'qib bo'lmasa (`Retry-After` yo'q) matn umumiy qoladi —
      // «biroz kuting» — va taymer ko'rinmaydi.
      const wait = err instanceof ApiError ? err.retryAfter : 0;
      setRetryAfter(wait);
      // Band pochta — server matni o'rniga YO'NALTIRUVCHI xabar
      // (14-qaror). Matn tarjima qilinmagan bo'lishi ham mumkin, shuning
      // uchun tayyor kalitdan olamiz; yo'naltiruvchi satr esa pastda
      // alohida chiziladi va u `role="alert"` ni takrorlamaydi.
      const takenEmail =
        mode === "register" && err instanceof ApiError && err.field("email") !== null;
      setBlocked(takenEmail ? { kind: "email" } : null);
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
      <form
        onSubmit={onSubmit}
        // Fokus — «forma boshlandi» belgisi. `onSubmit` buni ushlamaydi:
        // odam formani ochib, maydonni bosib, keyin tashlab ketishi
        // mumkin — aynan shu holat eng qimmatli ma'lumot.
        onFocus={() => {
          if (started.current) return;
          started.current = true;
          track("auth.form_started", { mode });
        }}
        className="flex flex-col gap-4"
      >
        {/* HISOB — kirish uchun majburiy qism, eng avval keladi. Standart
            naqsh: odam tanish maydonlardan boshlaydi (identifikator +
            parol), keyin profil.

            Kirishda maydon BITTA (4-qaror): foydalanuvchi nomi ham,
            email ham qabul qilinadi. Ilgari faqat nom edi va emailini
            yoddan bilgan odam «Login yoki parol noto'g'ri» olardi —
            holbuki u to'g'ri ma'lumot kiritgan edi. Serverda ikkala
            ustun bo'yicha qidiriladi. */}
        {mode === "register" ? (
          <Field
            label={t(locale, "auth.email")}
            name="email"
            type="email"
            required
            // Sahifaning yagona vazifasi shu forma — kursor darhol shu
            // yerda bo'lsin.
            autoFocus
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            status={emailStatus}
          />
        ) : (
          <Field
            label={t(locale, "auth.usernameOrEmail")}
            name="identifier"
            required
            autoFocus
            // Parol menejeri ham nom, ham email saqlashi mumkin —
            // `username` ikkalasini qamrab oladi.
            autoComplete="username"
            hint={t(locale, "auth.identifierHint")}
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

        {/* PROFIL maydonlari (foydalanuvchi nomi, ism, mamlakat, viloyat)
            bu yerdan 2-QADAMGA ko'chirildi (3-qaror). Sabab o'lchovda:
            forma to'qqizta maydon edi, raqobatchilarda esa o'rtacha
            3–4 ta — ya'ni odam «ro'yxatdan o'tish» ni bosishdan oldin
            to'qqiz qaror qabul qilishi kerak edi.
            Endi 1-qadamda faqat hisob ochish uchun SHART bo'lgani bor:
            email, parol, tasdiq va rozilik. Qolgani OnboardingForm da.

            Bu yerda ilgari `geoVariant === "b"` shoxi ham bor edi —
            viloyatni erta so'rash tajribasi. U 2-qadamga ko'chgan
            maydonlar bilan birga ketdi: endi ikkala guruh ham viloyatni
            bir joyda, bir xil vaqtda so'raydi, ya'ni tajriba o'lchaydigan
            narsa qolmadi va u `OnboardingForm` da saqlanadi. */}

        {mode === "login" && (
          /* Bitta qatorda: chapda «eslab qol», o'ngda «parolni tiklash» —
             ikkalasi ham kirishga yordam beradi, ya'ni bir joyda turishi
             kerak (RoboContest va KEP'da ham shunday). */
          <div className="-mt-1 flex flex-wrap items-center justify-between gap-2">
            <Checkbox
              name="remember"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
            >
              {t(locale, "auth.remember")}
            </Checkbox>
            <Link
              href={"/login?tab=reset-password" as Route}
              className="text-theme-sm rw-accent-ink hover:underline"
            >
              {t(locale, "auth.forgot")}
            </Link>
          </div>
        )}

        {mode === "register" && (
          /* Rozilik: shartlar MAJBURIY, marketing IXTIYORIY (qaror 13).
             Ikkalasi alohida — GDPR shartlar roziligi bilan marketing
             roziligini birlashtirishga ruxsat bermaydi. */
          <div className="flex flex-col gap-2.5">
            <Checkbox
              name="terms_accepted"
              checked={terms}
              onChange={(e) => setTerms(e.target.checked)}
              required
            >
              {t(locale, "auth.termsAccept")}
            </Checkbox>
            <Checkbox
              name="marketing_opt_in"
              checked={marketing}
              onChange={(e) => setMarketing(e.target.checked)}
            >
              {t(locale, "auth.marketingOptIn")}
            </Checkbox>
          </div>
        )}

        {error && (
          // `aria-live` TAQDIM ETILMAYDI: `role="alert"` allaqachon
          // «assertive» rejimda e'lon qiladi va `aria-live` ni
          // takrorlash ekran o'quvchini ikki marta gapirtirardi.
          <p
            role="alert"
            className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink"
          >
            {error}
            {retryAfter > 0 && (
              // Kutish soniyasi (15-qaror). Matn serverdan kelgan
              // `Retry-After` dan hosil qilinadi, ya'ni taxmin emas.
              // Raqam taymer bilan yangilanadi va u `error` satrining
              // ICHIDA emas, alohida tugun — aks holda butun xato
              // qayta e'lon qilinar va ekran o'quvchi uni har soniyada
              // o'qib chiqardi.
              <>
                {" "}
                {t(locale, "auth.throttledWait").replace(
                  "{seconds}",
                  String(retryAfter),
                )}
              </>
            )}
          </p>
        )}

        {/* Yo'naltiruvchi xabar (14-qaror): «bu email band» — boshi berk
            ko'cha emas, IKKI yo'l. Matnni maydon nomi bo'yicha
            ajratamiz, chunki DRF maydon xatosida `code` har doim
            `"invalid"` bo'ladi (`ApiError.field` izohiga qarang).

            Ro'yxatdan o'tishda: «Kirish» + «Parolni tiklash».
            Tiklashda esa email topilmasa ham xuddi shu ikki yo'l —
            sabab bir xil, ya'ni matn bitta kalitdan keladi. */}
        {blocked?.kind === "email" && (
          <p className="-mt-2 text-theme-sm rw-dim">
            {t(locale, "auth.emailTaken")}{" "}
            <Link
              href={"/login?tab=login" as Route}
              className="rw-accent-ink underline rw-focus-ring"
            >
              {t(locale, "auth.tabLogin")}
            </Link>
            {" · "}
            <Link
              href={"/login?tab=reset-password" as Route}
              className="rw-accent-ink underline rw-focus-ring"
            >
              {t(locale, "auth.tabReset")}
            </Link>
          </p>
        )}

        {/* Turnstile FAQAT ro'yxatdan o'tishda (9-qaror): hisob ochish
            botlar uchun eng qulay nishon, kirish esa allaqachon parol
            va throttle bilan himoyalangan. Ko'rinmas rejim, ya'ni odam
            odatda hech narsa ko'rmaydi; tugma USTIDA turadi va o'lchami
            nolga tushsa ham joy egallamaydi. */}
        {mode === "register" && (
          <Turnstile siteKey={turnstileSiteKey} onToken={setCaptcha} />
        )}

        <Button
          type="submit"
          // Bloklangan paytda tugma O'CHIRILADI: server baribir rad
          // etadi, ya'ni bosish faqat ortiqcha 429 yasardi va odam
          // «ishlamayapti» degan taassurot olardi.
          disabled={retryAfter > 0}
          busy={busy}
          busyLabel={t(locale, mode === "login" ? "auth.loggingIn" : "auth.registering")}
        >
          {t(locale, mode === "login" ? "auth.login" : "auth.register")}
        </Button>
        {/* Bu yerda ilgari `auth.legal` («Ro'yxatdan o'tish orqali...»)
            ham chizilardi. U yuqoridagi MAJBURIY checkbox bilan bir xil
            narsani aytardi, ya'ni bir sahifada rozilik ikki marta
            takrorlanardi — o'lchandi. Checkbox aniqroq (faol rozilik) va
            uni chetlab o'tib bo'lmaydi, shuning uchun passiv takror
            olib tashlandi. Ijtimoiy yo'lda esa checkbox YO'Q, ya'ni u
            yerda passiv matn rozilikning yagona asosi bo'lib qoladi. */}
      </form>

      {/* Parol formasi asosiy yo'l bo'lib qoladi, ijtimoiy kirish esa
          uning ostida: ajratkich tugmalardan OLDIN turadi, aks holda u
          formadan keyin osilib qolardi. */}
      {providers.length > 0 && (
        <>
          <div className="flex items-center gap-3">
            <span className="h-px flex-1 border-t rw-divider" />
            <span className="text-theme-xs rw-dim">
              {t(locale, "auth.orWith")}
            </span>
            <span className="h-px flex-1 border-t rw-divider" />
          </div>
          {/* Tartib `PROVIDER_ORDER` dan (10-qaror): Telegram birinchi
              va TO'LIQ kenglikda, qolganlari ostida yonma-yon.
              Uchtasi ham ustma-ust ~150px vertikal joy olardi va forma
              ekrandan pastga tushib ketardi; ikkitasi yonma-yon esa
              ~96px — shuning uchun aynan shu taqsimot.

              Brend nomi tarjima qilinmaydi, shuning uchun matn shu
              yerda; to'liq nomi (`Google orqali davom etish`)
              `aria-label` da. */}
          <div className="flex flex-col gap-2">
            {PROVIDER_ORDER.filter((p) =>
              providers.includes(p),
            ).map((p) =>
              p === "telegram" ? (
                <a
                  key={p}
                  // `next` provayderga ham uzatiladi: server uni sessiyada
                  // saqlaydi va callback'da o'sha manzilga qaytaradi.
                  href={`/api/v1/auth/${p}/start/${
                    next ? `?next=${encodeURIComponent(next)}` : ""
                  }`}
                  aria-label={t(locale, PROVIDER_LABEL[p])}
                  className={`flex h-11 items-center justify-center gap-2 rw-radius-sm text-theme-sm font-medium transition rw-focus-ring hover:brightness-95 ${BRAND[p]}`}
                >
                  <TelegramMark />
                  <span className="truncate">{PROVIDER_NAME[p]}</span>
                </a>
              ) : null,
            )}
            <div className="grid grid-cols-2 gap-2">
              {PROVIDER_ORDER.filter(
                (p) => p !== "telegram" && providers.includes(p),
              ).map((p) => (
                <a
                  key={p}
                  href={`/api/v1/auth/${p}/start/${
                    next ? `?next=${encodeURIComponent(next)}` : ""
                  }`}
                  aria-label={t(locale, PROVIDER_LABEL[p])}
                  className={`flex h-11 items-center justify-center gap-2 rw-radius-sm text-theme-sm font-medium transition rw-focus-ring hover:brightness-95 ${BRAND[p]}`}
                >
                  {p === "google" ? <GoogleMark /> : <GithubMark />}
                  <span className="truncate">{PROVIDER_NAME[p]}</span>
                </a>
              ))}
            </div>
          </div>
          {/* Rozilik matni: OAuth orqali hisob ochilganda `terms_accepted_at`
              shu matnga asoslanib yoziladi (`record_social_consent`).
              Matnsiz yozish huquqiy jihatdan asossiz bo'lardi. */}
          <Legal />
        </>
      )}

      {/* Footer endi BO'LIM tugmasi bilan takrorlanmaydi: uchala forma
          bitta kartada va almashish yuqoridagi bo'limlarda (1-qaror).
          Ya'ni bu satr faqat SHU formasiz qolgan yo'lni ko'rsatadi —
          kirishda «hisobingiz yo'qmi?», ro'yxatda esa aksi. */}
      <p className="text-center text-theme-sm rw-dim">
        {t(locale, mode === "login" ? "auth.noAccount" : "auth.hasAccount")}{" "}
        <Link
          href={
            (mode === "login"
              ? "/login?tab=register"
              : "/login?tab=login") as Route
          }
          // Doimiy tagchiziq: havola MATN ICHIDA turadi, ya'ni faqat rang
          // bilan ajralishi WCAG 1.4.1 ni buzardi (yuqoridagi rozilik
          // havolalari bilan bir xil sabab).
          className="font-medium rw-accent-ink underline"
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
                  // Bo'sh bo'lakchalar `--rw-divider`: `--rw-line` shaffof
                  // bo'lgani uchun `clay` va `neu` da ular umuman
                  // ko'rinmasdi va chiziq «4 dan 1» emas, bitta qisqa
                  // chiziq bo'lib o'qilardi. Daraja so'z bilan ham
                  // yoziladi, lekin bo'lakchalar SONI ham ma'no tashiydi.
                  : "var(--rw-divider)",
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
 *  belgilaydi. Jumlani bo'laklab yig'ish shu sababdan.
 *
 *  Faqat ijtimoiy tugmalar ostida chiziladi (`auth.socialConsent`).
 *  Forma tomonida bunday passiv matn YO'Q: u yerda majburiy checkbox
 *  bor va u aniqroq — passiv takror bir sahifada rozilikni ikki marta
 *  ko'rsatardi.
 *
 *  Havolalar DOIMIY tagchiziq bilan chiziladi. Sabab WCAG 1.4.1: ular
 *  matn ICHIDA turadi va atrofdagi so'zdan faqat rang bilan ajralsa,
 *  farq 1.24:1 bo'ladi (talab 3:1) — ya'ni rang ko'rmaydigan odam uchun
 *  havola umuman bilinmaydi. Lighthouse buni `link-in-text-block` deb
 *  belgilaydi. `.rw-md a` ham xuddi shu sababdan tagchiziqli. */
function Legal() {
  const locale = useLocale();
  const parts = t(locale, "auth.socialConsent").split(/(\{terms\}|\{privacy\})/);
  return (
    <p className="text-center text-theme-xs rw-dim">
      {parts.map((part, i) =>
        part === "{terms}" ? (
          <Link key={i} href="/shartlar" className="rw-accent-ink underline">
            {t(locale, "footer.terms")}
          </Link>
        ) : part === "{privacy}" ? (
          <Link key={i} href="/maxfiylik" className="rw-accent-ink underline">
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
        <Link
          href={"/login?tab=reset-password" as Route}
          className="rw-accent-ink hover:underline"
        >
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
