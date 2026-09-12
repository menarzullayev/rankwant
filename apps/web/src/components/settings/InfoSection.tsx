"use client";

import { useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { CountryFlag } from "@/components/ui/CountryFlag";
import { Field } from "@/components/ui/Field";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { patchJson, type PrivacyField } from "@/lib/api";
import { countryOptions } from "@/lib/countries";
import { REGION_CODES, districtOptions, regionName } from "@/lib/regions";
import { Check, Hint, Select, Status, useAction } from "./kit";
import { SchoolField } from "./SchoolField";

/** Shaxsiy ma'lumot. Hammasi ixtiyoriy va standart holatda profilda
 *  ko'rinadi — yashirish har maydon yonida, odam nimani ochiq qoldirganini
 *  ko'rib turadi. */
export function InfoSection() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  const [country, setCountry] = useState<string | null>(null);
  const [hidden, setHidden] = useState<PrivacyField[] | null>(null);
  const [region, setRegion] = useState<string | null>(null);
  const countries = useMemo(() => countryOptions(locale), [locale]);
  if (!user) return null;

  const currentCountry = country ?? user.country;
  const currentHidden = hidden ?? user.hidden_fields;
  const today = new Date().toISOString().slice(0, 10);

  function visibility(field: PrivacyField, label?: string) {
    return (
      <Check
        label={label ?? t(locale, "settings.showOnProfile")}
        checked={!currentHidden.includes(field)}
        onChange={(event) => {
          const rest = currentHidden.filter((f) => f !== field);
          setHidden(event.target.checked ? rest : [...rest, field]);
        }}
      />
    );
  }

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const text = (name: string) => String(form.get(name) ?? "").trim();
    const ok = await action.run(async () => {
      await patchJson("/me/", {
        country: currentCountry,
        region: text("region"),
        district: text("district"),
        city: text("city"),
        school_ref: text("school_ref") ? Number(text("school_ref")) : null,
        school: text("school"),
        grade: text("grade"),
        website: text("website"),
        birth_date: text("birth_date") || null,
        hidden_fields: currentHidden,
      });
      await reload();
    });
    if (ok) {
      setCountry(null);
      setHidden(null);
      setRegion(null);
    }
  }

  const regionDefault = currentCountry === user.country ? user.region : "";
  const currentRegion = region ?? regionDefault;
  const districtDefault = currentRegion === user.region ? user.district : "";
  const districts = currentCountry === "UZ" && currentRegion ? districtOptions(currentRegion, locale) : [];

  return (
    <Card title={t(locale, "settings.info")}>
      <Hint>{t(locale, "settings.infoHint")}</Hint>
      <form onSubmit={save} className="mt-5 flex flex-col gap-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Select
              label={t(locale, "settings.country")}
              value={currentCountry}
              leading={
                currentCountry ? <CountryFlag code={currentCountry} /> : undefined
              }
              onChange={(event) => {
                setCountry(event.target.value);
                setRegion(null);
              }}
            >
              <option value="">{t(locale, "settings.notChosen")}</option>
              {countries.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.name}
                </option>
              ))}
            </Select>
            {visibility("country")}
          </div>
          {currentCountry === "UZ" ? (
            <Select
              key="uz"
              label={t(locale, "settings.region")}
              name="region"
              defaultValue={regionDefault}
              onChange={(event) => setRegion(event.target.value)}
            >
              <option value="">{t(locale, "settings.notChosen")}</option>
              {REGION_CODES.map((code) => (
                <option key={code} value={code}>
                  {regionName(code, locale)}
                </option>
              ))}
            </Select>
          ) : (
            <Field
              key="other"
              label={t(locale, "settings.region")}
              name="region"
              defaultValue={regionDefault}
              maxLength={80}
              disabled={!currentCountry}
              autoComplete="address-level1"
            />
          )}
          {currentCountry === "UZ"
            ? districts.length > 0 && (
                <Select
                  key={`district:${currentRegion}`}
                  label={t(locale, "settings.district")}
                  name="district"
                  defaultValue={districtDefault}
                >
                  <option value="">{t(locale, "settings.notChosen")}</option>
                  {/* Toshkent shahrida viloyat shaharlari yo'q — bo'sh guruh chizilmaydi. */}
                  {[
                    { key: "settings.districts", rows: districts.filter((row) => !row.city) },
                    { key: "settings.cities", rows: districts.filter((row) => row.city) },
                  ]
                    .filter((group) => group.rows.length > 0)
                    .map((group) => (
                      <optgroup key={group.key} label={t(locale, group.key)}>
                        {group.rows.map((row) => (
                          <option key={row.code} value={row.code}>
                            {row.name}
                          </option>
                        ))}
                      </optgroup>
                    ))}
                </Select>
              )
            : currentCountry && (
                <Field
                  key="city"
                  label={t(locale, "settings.city")}
                  name="city"
                  defaultValue={user.city}
                  maxLength={100}
                  autoComplete="address-level2"
                />
              )}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <SchoolField
              label={t(locale, "settings.school")}
              initialName={user.school_ref ? user.school_name : user.school}
              initialId={user.school_ref}
            />
            {visibility("school")}
          </div>
          <div className="space-y-2">
            <Field
              label={t(locale, "settings.grade")}
              name="grade"
              defaultValue={user.grade}
              maxLength={40}
            />
            {visibility("grade")}
          </div>
          <div className="space-y-2">
            <Field
              label={t(locale, "settings.website")}
              name="website"
              type="url"
              defaultValue={user.website}
              hint="https://…"
              autoComplete="url"
            />
            {visibility("website")}
          </div>
          <div className="space-y-2">
            <Field
              label={t(locale, "settings.birthDate")}
              name="birth_date"
              type="date"
              defaultValue={user.birth_date ?? ""}
              min="1900-01-01"
              max={today}
              autoComplete="bday"
            />
            {visibility("birth_date")}
          </div>
        </div>

        {user.email && visibility("email", t(locale, "settings.showEmail"))}
        {visibility("online", t(locale, "settings.showOnline"))}
        {visibility("coach", t(locale, "settings.showCoach"))}
        {visibility("social", t(locale, "settings.showSocial"))}

        <Status error={action.error} done={action.done} />
        <Button type="submit" busy={action.busy} className="self-start">
          {t(locale, "settings.save")}
        </Button>
      </form>
    </Card>
  );
}
