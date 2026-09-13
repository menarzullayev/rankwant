"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Field, type FieldStatus } from "@/components/ui/Field";
import { Checkbox, SelectField } from "@/components/ui/SelectField";
import { CountrySelect } from "@/components/ui/CountrySelect";
import { GithubMark, GoogleMark, TelegramMark } from "@/components/ProviderMark";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText, type Locale } from "@/i18n/messages";
import { ApiError, getJson, postJson } from "@/lib/api";
import { track } from "@/lib/analytics";
import { strength } from "@/lib/password";
import { type Variant } from "@/lib/experiments";
import { REGION_CODES, regionName } from "@/lib/regions";
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

/** Til -> odatiy mamlakat. Mamlakat maydonining standart qiymati shu yerdan
 *  olinadi, qattiq `UZ` dan emas. Ro'yxatda yo'q til uchun `UZ`. */
const DEFAULT_COUNTRY: Partial<Record<Locale, string>> = {
  uz: "UZ",
  kaa: "UZ",
  ru: "UZ",
  kk: "KZ",
  ky: "KG",
  tg: "TJ",
  tr: "TR",
};

export function AuthForm({
  mode,
  providers,
  geoVariant = "a",
}: {
  mode: Mode;
  /** Serverda olinadi — tugmalar HTML da keladi va JS ga bog'liq emas. */
  providers: string[];
  /** A/B guruhi (8-qaror), SERVERDA cookie'dan o'qiladi.
   *
   *  `b` — viloyat ro'yxatdan o'tishning o'zida so'raladi. Server
   *  komponentida o'qiladi, mijozda emas: aks holda server `a`, mijoz
   *  `b` chizib hidratsiya mos kelmasligi mumkin edi.
   *
   *  Standart `a` — guruh bo'lmasa xatti-harakat o'zgarmaydi. */
  geoVariant?: Variant;
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
  const [busy, setBusy] = useState(false);
  const [visible, setVisible] = useState(false);
  // Yozayotgandagi tekshiruv faqat ro'yxatdan o'tishda kerak: kirishda
  // nom band ekanini aytish mavjud hisoblarni sanab chiqish yo'li bo'lardi.
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [pass2, setPass2] = useState("");
  //: Mamlakat — ro'yxatning 1-bosqichida so'raladi (qaror 2). Standart
  //: qiymat TILDAN kelib chiqadi: qattiq `UZ` qo'yilsa qozoq yoki qirg'iz
  //: foydalanuvchisi o'z mamlakatini emas, O'zbekistonni ko'rib qolardi.
  //: Til mamlakatni aniqlamasa (masalan `en`, `zh`, `es`) `UZ` qoladi —
  //: auditoriyaning asosiy qismi shu yerdan.
  const [country, setCountry] = useState(() => DEFAULT_COUNTRY[locale] ?? "UZ");
  //: A/B `b` variantida viloyat shu formada so'raladi (8-qaror).
  //: `a` variantida bo'sh qoladi va 2-qadamda to'ldiriladi.
  const [region, setRegion] = useState("");
  //: Shartlar va maxfiylik — MAJBURIY (qaror 13). Ataylab `false` dan
  //: boshlanadi: oldindan belgilangan katak rozilik hisoblanmaydi.
  const [terms, setTerms] = useState(false);
  //: Marketing — IXTIYORIY va alohida (GDPR 7-modda).
  const [marketing, setMarketing] = useState(false);
  //: «Meni eslab qol» — kirishda (qaror 7). Standart `false`: umumiy
  //: kompyuterda hisob ochiq qolmasligi kerak.
  const [remember, setRemember] = useState(false);
  //: «Forma boshlandi» hodisasi BIR MARTA yuboriladi (qaror 17). Har
  //: fokusda yuborilsa funnel shishib ketardi va raqam ma'nosini
  //: yo'qotardi.
  const started = useRef(false);
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
        await postJson("/auth/register/", {
          ...payload,
          country,
          // `b` variantida viloyat shu yerda keladi, `a` da bo'sh —
          // maydon ixtiyoriy, ya'ni ikkalasi ham to'g'ri.
          region,
          terms_accepted: terms,
          marketing_opt_in: marketing,
        });
        // Register sessiya ochmaydi (ADR-0008) — darhol login qilamiz.
        await postJson("/auth/login/", {
          username: payload.username,
          password: payload.password,
        });
      } else {
        await postJson("/auth/login/", { ...payload, remember });
      }
      // Sessiyani darhol yangilaymiz: header client komponenti bo'lgani
      // uchun `router.push` uni qayta mount qilmaydi va kirgandan keyin
      // ham «Kirish» tugmasi qolib ketardi.
      await reload();
      // Muvaffaqiyat hodisasi `router.push` dan OLDIN yuboriladi:
      // `keepalive` tufayli sahifa almashgach ham yetib boradi.
      track(mode === "register" ? "auth.register_done" : "auth.login_done", {
        mode,
        country: mode === "register" ? country : undefined,
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
          ? `/qoshimcha-malumot?welcome=1${
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
            naqsh: odam tanish maydonlardan boshlaydi (email + parol), keyin
            profil. Ilgari foydalanuvchi nomi birinchi edi, ya'ni odam
            tanish qismga yetishdan oldin qo'shimcha qaror qabul qilardi.
            Kirishda esa identifikator — foydalanuvchi nomi, shuning uchun
            u yerda tartib o'zgarmaydi. */}
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
            label={t(locale, "auth.username")}
            name="username"
            required
            autoFocus
            autoComplete="username"
            value={undefined}
            status={nameStatus}
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

        {mode === "register" && (
          <>
            {/* Guruh chegarasi — hisob va profil ajralib tursin. */}
            <hr className="border-t rw-divider" />
            {/* PROFIL. Foydalanuvchi nomi majburiy, qolgani ixtiyoriy. */}
            <Field
              label={t(locale, "auth.username")}
              name="username"
              required
              autoComplete="username"
              minLength={3}
              maxLength={30}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              status={nameStatus}
              hint={t(locale, "auth.usernameHint")}
            />
            <Field
              label={t(locale, "auth.displayName")}
              name="display_name"
              autoComplete="name"
              maxLength={100}
              hint={t(locale, "auth.displayNameHint")}
            />
            {/* Mamlakat — bosqichli yig'ishning birinchi qadami (qaror 2):
                bitta tanlov, lekin butun statistika shu bo'yicha bo'linadi.
                Qidiruvli: 249 variantni qo'lda aylantirish noqulay. */}
            <CountrySelect
              label={t(locale, "auth.country")}
              value={country}
              onChange={(code) => {
                setCountry(code);
                // Viloyat KODI faqat O'zbekiston uchun ma'noli: boshqa
                // mamlakatlarda joy erkin matn bo'ladi (ADR-0017).
                if (code !== "UZ") setRegion("");
              }}
            />
            {geoVariant === "b" && country === "UZ" && (
              /* A/B `b` varianti (8-qaror): viloyat DARHOL so'raladi.
                 Nazorat guruhida esa bu 2-qadamda so'raladi — farq shunda,
                 ya'ni «erta so'rash odamni qaytarib yuborayaptimi» degan
                 savolga javob shu ikki guruhni taqqoslab topiladi. */
              <SelectField
                label={t(locale, "settings.region")}
                name="region"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              >
                <option value="">—</option>
                {REGION_CODES.map((code) => (
                  <option key={code} value={code}>
                    {regionName(code, locale)}
                  </option>
                ))}
              </SelectField>
            )}
          </>
        )}

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
              href="/parolni-tiklash"
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
          {/* Ustma-ust uchta to'liq kenglikdagi tugma ~150px vertikal joy
              olardi va forma ekrandan pastga tushib ketardi. Ikkitasi
              yonma-yon, Telegram esa ostida — shunda ~96px bo'ladi.
              Brend nomi tarjima qilinmaydi, shuning uchun matn shu yerda;
              to'liq nomi (`Google orqali davom etish`) `aria-label` da.

              Telegram ham endi shu naqshda: ilgari u Telegram'ning o'z
              iframe vidjetini chizardi (o'lchamini o'zi belgilardi), endi
              qolganlar kabi oddiy havola — oqim OIDC ga o'tdi. */}
          <div className="grid grid-cols-2 gap-2">
            {providers
              .filter((p): p is Provider => p !== "telegram" && p in PROVIDER_LABEL)
              .map((p) => (
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
                  {p === "google" ? <GoogleMark /> : <GithubMark />}
                  <span className="truncate">{p === "google" ? "Google" : "GitHub"}</span>
                </a>
              ))}
          </div>
          {providers.includes("telegram") && (
            <a
              href={`/api/v1/auth/telegram/start/${
                next ? `?next=${encodeURIComponent(next)}` : ""
              }`}
              aria-label={t(locale, PROVIDER_LABEL.telegram)}
              className={`flex h-11 items-center justify-center gap-2 rw-radius-sm text-theme-sm font-medium transition rw-focus-ring hover:brightness-95 ${BRAND.telegram}`}
            >
              <TelegramMark />
              <span className="truncate">Telegram</span>
            </a>
          )}
          {/* Rozilik matni: OAuth orqali hisob ochilganda `terms_accepted_at`
              shu matnga asoslanib yoziladi (`record_social_consent`).
              Matnsiz yozish huquqiy jihatdan asossiz bo'lardi. */}
          <Legal />
        </>
      )}

      <p className="text-center text-theme-sm rw-dim">
        {t(locale, mode === "login" ? "auth.noAccount" : "auth.hasAccount")}{" "}
        <Link
          href={mode === "login" ? "/register" : "/login"}
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
