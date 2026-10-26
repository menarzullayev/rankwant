"use client";

import type { Route } from "next";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { TabBar } from "@/components/kit/TabBar";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { CountrySelect } from "@/components/ui/CountrySelect";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText, type MessageKey } from "@/i18n/messages";
import { api, ApiError, patchJson, type Me, type School } from "@/lib/api";
import { track } from "@/lib/analytics";
import {
  EDUCATION_LEVELS,
  gradeCodesFor,
  gradeLabel,
  hasSpecialty,
} from "@rankwant/shared/grades";
import { REGION_CODES, districtOptions, regionName } from "@rankwant/shared/regions";
import { safeNext } from "@/lib/site";
import { useUsernameCheck } from "../useUsernameCheck";

/** Is this the TEMPORARY handle the server gave (`u` + 12 lowercase letters or
 *  digits)? The sign-up may leave the handle blank; showing the temporary one
 *  as if it were the person's own would only raise "is this mine?". The field
 *  stays blank and they type their own.
 *
 *  The format must equal `core/usernames.py: is_temp_username`. */
function isTempUsername(name: string): boolean {
  return /^u[a-z0-9]{12}$/.test(name);
}

/** Which catalogue `kind` goes with an education level. Only these levels
 *  have a catalogue; "working" and "other" are free text or nothing. */
const CATALOGUE_KIND: Record<string, string> = {
  school: "school",
  lyceum: "lyceum",
  college: "college",
  bachelor: "university",
  master: "university",
  phd: "university",
  aspirantura: "university",
};

// Event names and reasons are named here: `check_hardcoded` reads a string on
// a ternary branch as screen text.
const EVENT_SAVED = "auth.step2_saved";
const EVENT_SKIPPED = "auth.step2_skipped";
const REASON_SERVER = "server";

const STEPS = ["address", "education", "extra"] as const;
type Step = (typeof STEPS)[number];

const TITLE: Record<Step, MessageKey> = {
  address: "onboarding.addressTitle",
  education: "onboarding.educationTitle",
  extra: "onboarding.extraTitle",
};
const STEP_LABEL: Record<Step, MessageKey> = {
  address: "onboarding.stepAddress",
  education: "onboarding.stepEducation",
  extra: "onboarding.stepExtra",
};
const BODY: Record<Step, MessageKey> = {
  address: "onboarding.addressBody",
  education: "onboarding.educationBody",
  extra: "onboarding.extraBody",
};

/** The second half of sign-up: three short steps, each one optional
 *  (2026-10-26). Everything required is already on the sign-up form, so this
 *  is only what makes the profile useful: where the person lives, where they
 *  study, and a couple of extras.
 *
 *  Each step saves on its own ("Next" writes it), so a person who leaves after
 *  step two keeps what they gave. "Later" moves on without writing the step.
 *
 *  The temporary handle is the one exception to "optional": if the sign-up left
 *  it blank, the first step asks for a real one — a profile address, rating and
 *  teams hang on it. */
export function OnboardingForm({ me }: { me: Me }) {
  const locale = useLocale();
  const router = useRouter();
  const params = useSearchParams();

  // `?welcome=1` is carried to the home page and turned into `2` after the last
  // step: the "enter the code" notice there waits for exactly that.
  const welcome = params.get("welcome");
  const done = welcome === "1" ? "2" : welcome;
  // The sign-up led here on the way to another page: return to it, and drop the
  // one-time notice, which would mean nothing there.
  const back = safeNext(params.get("next"));
  const home = (back ?? (done ? `/?welcome=${done}` : "/")) as Route;

  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  // Step 1 — where
  const needsHandle = isTempUsername(me.username);
  const [username, setUsername] = useState(needsHandle ? "" : me.username);
  const [country, setCountry] = useState(me.country || "UZ");
  const [region, setRegion] = useState(me.region || "");
  const [district, setDistrict] = useState(me.district || "");
  const [city, setCity] = useState(me.city || "");
  // Step 2 — study
  const [level, setLevel] = useState(me.education_level || "");
  const [school, setSchool] = useState(me.school_name || me.school || "");
  const [schoolRef, setSchoolRef] = useState<number | null>(me.school_ref);
  const [grade, setGrade] = useState(me.grade || "");
  const [specialty, setSpecialty] = useState(me.specialty || "");
  // Step 3 — extras
  const [phone, setPhone] = useState(me.phone || "");
  const [birthDate, setBirthDate] = useState(me.birth_date || "");

  const [found, setFound] = useState<{ for: string; items: School[] }>({ for: "", items: [] });
  const nameStatus = useUsernameCheck(username, needsHandle && step === 0);

  const isUz = country === "UZ";
  const query = school.trim();
  const kind = CATALOGUE_KIND[level];
  // The result remembers which query it answers, so a stale list never shows
  // before the new answer arrives.
  const results = found.for === query ? found.items : [];
  const districts = isUz && region ? districtOptions(region, locale) : [];
  const grades = gradeCodesFor(level);

  // Catalogue search, filtered by the level's kind and (for UZ) the region.
  // 300 ms of quiet first: a request per keystroke made the list flicker.
  useEffect(() => {
    if (!isUz || !kind || query.length < 2 || query === me.school_name) return;
    const timer = setTimeout(() => {
      api
        .schools({ q: query, region: region || undefined, kind })
        .then((page) => setFound({ for: query, items: page.results.slice(0, 8) }))
        .catch(() => setFound({ for: query, items: [] }));
    }, 300);
    return () => clearTimeout(timer);
  }, [query, region, isUz, kind, me.school_name]);

  const current = STEPS[step];
  const last = step === STEPS.length - 1;

  /** Writes this step. The handle is claimed first when it is still temporary:
   *  a taken name must stop the step so the person sees why. */
  async function save(): Promise<void> {
    if (current === "address") {
      if (needsHandle && username.trim() && username !== me.username) {
        await patchJson<Me>("/me/", { username: username.trim() });
      }
      await patchJson<Me>("/me/", {
        country,
        // In Uzbekistan the region and district are catalogue codes, elsewhere a
        // free-text city. The model keeps only what matches (ADR-0017).
        region: isUz ? region : "",
        district: isUz ? district : "",
        city: isUz ? "" : city.trim(),
      });
    } else if (current === "education") {
      await patchJson<Me>("/me/", {
        education_level: level,
        school: school.trim(),
        school_ref: schoolRef,
        grade,
        specialty: hasSpecialty(level) ? specialty.trim() : "",
      });
    } else {
      await patchJson<Me>("/me/", {
        phone: phone.trim(),
        birth_date: birthDate || null,
      });
    }
  }

  async function advance(write: boolean) {
    setError("");
    if (write) {
      setBusy(true);
      try {
        await save();
      } catch (err) {
        track("auth.form_error", {
          mode: "step2",
          reason: err instanceof ApiError ? err.code : REASON_SERVER,
        });
        setError(err instanceof ApiError ? errorText(locale, err.code, err.text) : String(err));
        setBusy(false);
        return;
      }
      setBusy(false);
    }
    track(write ? EVENT_SAVED : EVENT_SKIPPED, { step: current });
    if (last) {
      router.push(home);
      return;
    }
    setStep(step + 1);
  }

  return (
    <form
      method="post"
      noValidate
      onSubmit={(event) => {
        event.preventDefault();
        void advance(true);
      }}
      className="flex flex-col gap-4"
    >
      <TabBar
        tone="step"
        label={t(locale, "onboarding.step")
          .replace("{n}", String(step + 1))
          .replace("{total}", String(STEPS.length))}
        value={current}
        options={STEPS.map((name) => ({ id: name, label: t(locale, STEP_LABEL[name]) }))}
      />
      <h1 className="text-2xl font-bold rw-strong">{t(locale, TITLE[current])}</h1>
      <p className="-mt-2 text-theme-sm rw-dim">{t(locale, BODY[current])}</p>

      {current === "address" && (
        <>
          {needsHandle && (
            <Field
              label={t(locale, "auth.username")}
              name="username"
              required
              autoComplete="username"
              autoCapitalize="none"
              spellCheck={false}
              minLength={3}
              maxLength={30}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              status={nameStatus}
              hint={t(locale, "auth.usernameHint")}
            />
          )}
          <CountrySelect
            label={t(locale, "settings.country")}
            value={country}
            onChange={(code) => {
              setCountry(code);
              // A new country makes the place no longer match.
              setRegion("");
              setDistrict("");
              setCity("");
            }}
          />
          {isUz ? (
            <>
              <SelectField
                label={t(locale, "settings.region")}
                name="region"
                value={region}
                onChange={(code) => {
                  setRegion(code);
                  setDistrict("");
                }}
                options={[
                  { value: "", label: t(locale, "settings.notChosen") },
                  ...REGION_CODES.map((code) => ({
                    value: code,
                    label: regionName(code, locale),
                  })),
                ]}
              />
              {districts.length > 0 && (
                <SelectField
                  key={`district:${region}`}
                  label={t(locale, "settings.district")}
                  name="district"
                  value={district}
                  onChange={setDistrict}
                  options={[
                    { value: "", label: t(locale, "settings.notChosen") },
                    ...districts.map((d) => ({ value: d.code, label: d.name })),
                  ]}
                />
              )}
            </>
          ) : (
            <Field
              label={t(locale, "settings.city")}
              name="city"
              autoComplete="address-level2"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              maxLength={100}
            />
          )}
        </>
      )}

      {current === "education" && (
        <>
          <SelectField
            label={t(locale, "onboarding.level")}
            name="education_level"
            value={level}
            onChange={(code) => {
              setLevel(code);
              // A year from another level would be nonsense (5th year of school).
              setGrade("");
              setSchoolRef(null);
            }}
            options={[
              { value: "", label: t(locale, "settings.notChosen") },
              ...EDUCATION_LEVELS.map((code) => ({
                value: code,
                label: t(locale, `onboarding.level.${code}` as MessageKey),
              })),
            ]}
          />
          {level && level !== "working" && (
            <div>
              <Field
                label={t(locale, "onboarding.institution")}
                name="school"
                value={school}
                onChange={(e) => {
                  setSchool(e.target.value);
                  // Typed text no longer points at the catalogue row.
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
                          setFound({ for: s.name, items: [] });
                        }}
                        className="flex min-h-11 w-full items-center justify-between gap-3 px-3 py-2 text-left text-theme-sm transition rw-hover-bg"
                      >
                        <span className="min-w-0 truncate rw-strong">{s.name}</span>
                        <span className="shrink-0 text-theme-xs rw-faint">{s.members}</span>
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
          )}
          {grades.length > 0 && (
            <SelectField
              key={`grade:${level}`}
              label={t(locale, "settings.grade")}
              name="grade"
              value={grade}
              onChange={setGrade}
              options={[
                { value: "", label: t(locale, "settings.notChosen") },
                ...grades.map((code) => ({ value: code, label: gradeLabel(code, locale) })),
              ]}
            />
          )}
          {hasSpecialty(level) && (
            <Field
              label={t(locale, "onboarding.specialty")}
              name="specialty"
              value={specialty}
              onChange={(e) => setSpecialty(e.target.value)}
              maxLength={150}
            />
          )}
        </>
      )}

      {current === "extra" && (
        <>
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
          <Field
            label={t(locale, "settings.birthDate")}
            name="birth_date"
            type="date"
            autoComplete="bday"
            value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)}
          />
        </>
      )}

      {error && <Status status="bad" variant="alert" alert label={error} />}

      <div className="flex flex-wrap items-center gap-3">
        <Button type="submit" busy={busy}>
          {t(locale, last ? "onboarding.finish" : "onboarding.next")}
        </Button>
        {step > 0 && (
          <Button type="button" variant="outline" disabled={busy} onClick={() => setStep(step - 1)}>
            {t(locale, "onboarding.back")}
          </Button>
        )}
        <Button type="button" variant="outline" disabled={busy} onClick={() => void advance(false)}>
          {t(locale, "onboarding.later")}
        </Button>
      </div>
    </form>
  );
}
