"use client";

import type { Route } from "next";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Field, type FieldStatus } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { CountrySelect } from "@/components/ui/CountrySelect";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { api, getJson, patchJson, type Me, type School } from "@/lib/api";
import { track } from "@/lib/analytics";
import { REGION_CODES, regionName } from "@/lib/regions";
import { safeNext } from "@/lib/site";

/** Server bergan VAQTINCHALIK nommi (`u` + 12 ta kichik harf/raqam)?
 *
 * 1-qadamda nom so'ralmaydi (3-qaror), ya'ni hisob vaqtinchalik nom
 * bilan ochiladi. Uni odamga ko'rsatish ma'nosiz va zararli: u
 * «mening nomim shumi?» degan savol tug'diradi. Maydon bo'sh
 * ko'rsatiladi va odam o'z nomini yozadi.
 *
 * Format `core/usernames.py: is_temp_username` bilan AYNAN bir xil
 * bo'lishi shart — ikki tomon bir formatni bilmasa maydon vaqtinchalik
 * nomni haqiqiy deb ko'rsatib qo'yardi. */
function isTempUsername(name: string): boolean {
  return /^u[a-z0-9]{12}$/.test(name);
}

/** Ro'yxatdan o'tishning 2-qadami — asosan ixtiyoriy (3-qaror).
 *
 * Nega shu yerda: 1-qadamda faqat hisob ochish uchun SHART bo'lgani
 * qoldi (email, parol, tasdiq, rozilik) — ya'ni to'rtta maydon.
 * Foydalanuvchi nomi, ism va joy shu yerga ko'chdi va o'sha paytda
 * odam allaqachon hisob egasi, ya'ni oqim uzilmaydi.
 *
 * `username` — ISTISNO: u bu yerda MAJBURIY. Hisobsiz nom bo'lmaydi
 * (profil manzili, reyting va jamoalar unga bog'langan), ya'ni server
 * vaqtinchalik nom beradi va u 2-qadamda haqiqiysiga almashtiriladi.
 * Qolgan maydonlar ixtiyoriy: ularni talab qilish odamni butunlay
 * yo'qotardi va ular keyin sozlamalarda ham to'ldiriladi.
 *
 * Maktab katalogdan (ADR-0017) yoki erkin matndan olinadi: katalogda
 * yo'q maktab ham yozilishi kerak, aks holda odam ro'yxatda qolib
 * ketardi. Erkin matn `school`, katalog tanlovi esa `school_ref` ga
 * yoziladi — maktab reytingi faqat katalog bo'yicha quriladi.
 */
export function OnboardingForm({ me }: { me: Me }) {
  const locale = useLocale();
  const router = useRouter();
  const params = useSearchParams();

  //: `AuthForm` ro'yxatdan keyin `?welcome=1` bilan yuboradi. Belgini
  //: bosh sahifaga O'TKAZAMIZ — aks holda yangi hisob egasi bir
  //: martalik xabarni (va kod kiritish maydonini) ko'rmasdi.
  const welcome = params.get("welcome");
  //: 2-qadam tugagach `1` ni `2` ga almashtiramiz (16-qaror): AtCoder/
  //: Codeforces taklifi AYNI shu belgini kutadi. Ilgari `1` o'zgarishsiz
  //: qolardi va `WelcomeNotice` (pochta tasdiqlash) bosh sahifada
  //: qayta chiqib, tasdiqlangan odamga ham «kodni kiriting» derdi.
  const done = welcome === "1" ? "2" : welcome;
  //: Qaytish manzili (qaror 1): ro'yxatdan o'tish odamni shu oraliq
  //: qadamga olib kirdi, lekin uning maqsadi boshqa sahifa edi. Belgilangan
  //: manzil bo'lsa — o'shanga qaytamiz, bir martalik xabar esa o'sha
  //: yerda ma'nosiz bo'lgani uchun tashlanadi.
  const back = safeNext(params.get("next"));
  const home = (back ?? (done ? `/?welcome=${done}` : "/")) as Route;

  //: Nom server bergan VAQTINCHALIK nom bo'lishi mumkin (`u` + 12
  //: belgi, 1-qadamda so'ralmaganligi uchun). Uni odamga ko'rsatish
  //: ma'nosiz — maydon bo'sh turadi va u o'z nomini yozadi.
  const [username, setUsername] = useState(
    isTempUsername(me.username) ? "" : me.username,
  );
  const [displayName, setDisplayName] = useState(me.display_name || "");
  const [nameCheck, setNameCheck] = useState<{ for: string; status: FieldStatus }>();
  const [country, setCountry] = useState(me.country || "UZ");
  const [region, setRegion] = useState(me.region || "");
  const [city, setCity] = useState(me.city || "");
  const [school, setSchool] = useState(me.school_name || me.school || "");
  const [schoolRef, setSchoolRef] = useState<number | null>(me.school_ref);
  //: Telefon — IXTIYORIY (qaror 6) va ommaviy profilga chiqmaydi.
  const [phone, setPhone] = useState(me.phone || "");

  const [found, setFound] = useState<{ for: string; items: School[] }>({
    for: "",
    items: [],
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  //: Nom bandligi — 1-qadamdan ko'chgan tekshiruv, xatti-harakati bir
  //: xil: odam yozishdan to'xtaganda bitta so'rov ketadi va oldingisi
  //: bekor qilinadi. Aks holda «ali» uchun to'rtta javob qaytardi va
  //: ular tartibsiz kelib, oxirgisi eskisi bo'lib qolishi mumkin edi.
  useEffect(() => {
    if (username.length < 3) return;
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
  }, [username, locale]);

  const nameStatus: FieldStatus | undefined =
    username.length < 3
      ? undefined
      : nameCheck?.for === username
        ? nameCheck.status
        : { kind: "busy", text: t(locale, "auth.checking") };

  const isUz = country === "UZ";
  const query = school.trim();
  // Natija QAYSI so'rov uchun kelgani bilan saqlanadi: eskirgan ro'yxat
  // yangi so'rov javobidan oldin ko'rinib qolmasin. Effekt ichida
  // `setState` chaqirmaslik uchun tozalash shu yerda — hisoblab.
  const results = found.for === query ? found.items : [];

  // Katalog qidiruvi — viloyat bo'yicha filtrlanadi, chunki bir xil
  // nomli maktablar har viloyatda bor. 300 ms kutamiz: har tugmada
  // so'rov yuborilsa ro'yxat miltillab qolardi.
  useEffect(() => {
    if (!isUz || query.length < 2 || query === me.school_name) return;
    const timer = setTimeout(() => {
      api
        .schools({ q: query, region: region || undefined })
        .then((page) =>
          setFound({ for: query, items: page.results.slice(0, 8) }),
        )
        .catch(() => setFound({ for: query, items: [] }));
    }, 300);
    return () => clearTimeout(timer);
  }, [query, region, isUz, me.school_name]);

  async function save(next: "home" | "skip") {
    setError("");
    if (next === "skip") {
      //: «O'tkazib yuborish» endi FAQAT IXTIYORIY maydonlarga tegishli:
      //: nom majburiy, ya'ni u bo'sh bo'lsa o'tkazib bo'lmaydi.
      //: Serverda ham vaqtinchalik nom qolib ketardi va odam profil
      //: manzilini bilmasdi.
      if (!username) {
        setError(t(locale, "auth.usernameRequired"));
        return;
      }
      // «O'tkazib yuborish» — eng muhim ko'rsatkich (qaror 17): bu raqam
      // qancha odam 2-qadamni to'ldirmasligini ko'rsatadi.
      track("auth.step2_skipped");
      await claimName();
      router.push(home);
      return;
    }
    if (!username) {
      setError(t(locale, "auth.usernameRequired"));
      return;
    }
    setBusy(true);
    try {
      await claimName();
      await patchJson<Me>("/me/", {
        display_name: displayName.trim(),
        country,
        // O'zbekistonda viloyat — kod, boshqa joyda shahar erkin matn.
        // Ikkalasi birga yuborilsa ham, model faqat mos kelganini
        // saqlaydi (ADR-0017: viloyat almashsa eski tuman tozalanadi).
        region: isUz ? region : "",
        city: isUz ? "" : city.trim(),
        school: school.trim(),
        school_ref: schoolRef,
        phone: phone.trim(),
      });
      track("auth.step2_saved", {
        country,
        // Maktab katalogdan tanlanganmi yoki erkin matnmi — katalog
        // qanchalik to'liq ekanini shu ko'rsatadi.
        from_catalog: schoolRef !== null,
        has_school: school.trim().length > 0,
      });
      router.push(home);
    } catch (err) {
      track("auth.form_error", { mode: "step2", reason: "server" });
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  /** Vaqtinchalik nomni haqiqiysiga almashtiradi.
   *
   *  Nom allaqachon o'zgargan bo'lsa (odam 2-qadamni ikkinchi marta
   *  ochgan) — hech narsa qilinmaydi. Sabab: `MeView` nom
   *  o'zgarishini `usernames.change` orqali o'tkazadi va u bepul
   *  imkoniyatni sarflaydi; aynan bir xil nomni qayta yuborish esa
   *  «Bu sizning hozirgi taxallusingiz» xatosi berardi.
   *
   *  Xato YUTILMAYDI: nom band bo'lsa `patchJson` 400 beradi va
   *  foydalanuvchi sababini ko'rishi kerak — jim o'tkazish uni
   *  vaqtinchalik nom bilan qoldirardi. */
  async function claimName() {
    if (username === me.username) return;
    await patchJson<Me>("/me/", { username });
  }

  return (
    <div className="flex flex-col gap-5">
      <p className="text-theme-sm rw-dim">{t(locale, "auth.step2Body")}</p>

      {/* NOM — bu qadamning yagona MAJBURIY maydoni (3-qaror).
          Ilgari u 1-qadamda edi; endi u shu yerda, ya'ni odam
          ro'yxatdan o'tib bo'lgach tanlaydi. Sabab: 1-qadamda nom
          tanlash qo'shimcha qaror edi va u ro'yxatdan o'tishning eng
          nozik joyini og'irlashtirardi.
          Tekshiruv serverda ham, shu yerda ham: `username-check`
          yozayotganda javob beradi, `PATCH /me/` esa yozishda. */}
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
        value={displayName}
        onChange={(e) => setDisplayName(e.target.value)}
        hint={t(locale, "auth.displayNameHint")}
      />

      <CountrySelect
        label={t(locale, "settings.country")}
        value={country}
        onChange={(code) => {
          setCountry(code);
          // Mamlakat almashsa joy ma'lumoti mos kelmay qoladi —
          // yangi mamlakatda viloyat kodi ham, shahar ham boshqa.
          setRegion("");
          setCity("");
        }}
      />

      {isUz ? (
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
      ) : (
        <Field
          label={t(locale, "settings.city")}
          name="city"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          maxLength={100}
        />
      )}

      <div>
        <Field
          label={t(locale, "settings.school")}
          name="school"
          value={school}
          onChange={(e) => {
            setSchool(e.target.value);
            // Erkin matn yozilgach eski katalog havolasi ma'nosini
            // yo'qotadi — aks holda reyting eski maktabda qolardi.
            setSchoolRef(null);
          }}
          maxLength={150}
          hint={t(locale, "settings.schoolFreeText")}
        />
        {results.length > 0 && (
          <ul className="mt-2 overflow-hidden rw-radius-sm border rw-line rw-surface">
            {results.map((s) => (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => {
                    setSchool(s.name);
                    setSchoolRef(s.id);
                    // Tanlangach ro'yxat yopiladi: `for` yangi nomga
                    // tenglashtiriladi, ya'ni natija bo'sh hisoblanadi.
                    setFound({ for: s.name, items: [] });
                  }}
                  className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-theme-sm transition rw-hover-bg"
                >
                  <span className="min-w-0 truncate rw-strong">{s.name}</span>
                  <span className="shrink-0 text-theme-xs rw-faint">
                    {s.members}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
        {schoolRef !== null && (
          <p className="mt-1.5 text-theme-xs rw-ok-ink">
            {t(locale, "settings.schoolFromCatalog")}
          </p>
        )}
      </div>

      {/* Telefon — IXTIYORIY (qaror 6). SMS tasdiqlash yo'q, ya'ni raqam
          tekshirilmaydi; maqsad hisobni tiklash va musobaqa
          bildirishnomalari uchun asos bo'lish. Ommaviy profilga
          chiqmaydi, shuning uchun bu yerda uning ko'rinishi haqida
          hech narsa va'da qilinmaydi. */}
      <Field
        label={t(locale, "settings.phone")}
        name="phone"
        type="tel"
        autoComplete="tel"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        maxLength={20}
        hint={t(locale, "settings.phoneHint")}
      />

      {error && (
        <Status status="bad" variant="alert" alert label={error} />
      )}

      <div className="flex flex-wrap gap-3">
        <Button onClick={() => save("home")} busy={busy}>
          {t(locale, "settings.save")}
        </Button>
        <Button variant="outline" onClick={() => save("skip")} disabled={busy}>
          {t(locale, "auth.skip")}
        </Button>
      </div>
    </div>
  );
}
