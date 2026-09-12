"use client";

import type { Route } from "next";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { api, patchJson, type Me, type School } from "@/lib/api";
import { track } from "@/lib/analytics";
import { countryOptions } from "@/lib/countries";
import { REGION_CODES, regionName } from "@/lib/regions";

/** Ro'yxatdan o'tishning 2-qadami — ixtiyoriy (qaror 3, 4).
 *
 * Nega ixtiyoriy: ro'yxatdan o'tishni to'sish odamni butunlay yo'qotadi,
 * maktab ma'lumoti esa keyin ham qo'shiladi (sozlamalarda ham bor).
 * Shu sababli bu yerda MAJBURIY maydon yo'q va "O'tkazib yuborish"
 * tugmasi bir xil darajada ko'rinadi.
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
  const home = (welcome ? `/?welcome=${welcome}` : "/") as Route;

  const [country, setCountry] = useState(me.country || "UZ");
  const [region, setRegion] = useState(me.region || "");
  const [city, setCity] = useState(me.city || "");
  const [school, setSchool] = useState(me.school_name || me.school || "");
  const [schoolRef, setSchoolRef] = useState<number | null>(me.school_ref);

  const [found, setFound] = useState<{ for: string; items: School[] }>({
    for: "",
    items: [],
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

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
      // «O'tkazib yuborish» — eng muhim ko'rsatkich (qaror 17): bu raqam
      // qancha odam 2-qadamni to'ldirmasligini ko'rsatadi.
      track("auth.step2_skipped");
      router.push(home);
      return;
    }
    setBusy(true);
    try {
      await patchJson<Me>("/me/", {
        country,
        // O'zbekistonda viloyat — kod, boshqa joyda shahar erkin matn.
        // Ikkalasi birga yuborilsa ham, model faqat mos kelganini
        // saqlaydi (ADR-0017: viloyat almashsa eski tuman tozalanadi).
        region: isUz ? region : "",
        city: isUz ? "" : city.trim(),
        school: school.trim(),
        school_ref: schoolRef,
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

  return (
    <div className="flex flex-col gap-5">
      <p className="text-theme-sm rw-dim">{t(locale, "auth.step2Body")}</p>

      <SelectField
        label={t(locale, "settings.country")}
        name="country"
        value={country}
        onChange={(e) => {
          setCountry(e.target.value);
          // Mamlakat almashsa joy ma'lumoti mos kelmay qoladi —
          // yangi mamlakatda viloyat kodi ham, shahar ham boshqa.
          setRegion("");
          setCity("");
        }}
      >
        {countryOptions(locale).map((c) => (
          <option key={c.code} value={c.code}>
            {c.name}
          </option>
        ))}
      </SelectField>

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

      {error && (
        <p
          role="alert"
          className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink"
        >
          {error}
        </p>
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
