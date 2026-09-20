"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { CountrySelect } from "@/components/ui/CountrySelect";
import { Field } from "@/components/ui/Field";
import { Icon } from "@/components/ui/Icon";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import {
  patchJson,
  type Gender,
  type PrivacyField,
  type ShirtSize,
  type ShirtSizeEu,
} from "@/lib/api";
import { GRADE_GROUPS, gradeLabel, isGradeCode } from "@/lib/grades";
import { REGION_CODES, districtOptions, regionName } from "@/lib/regions";
import { Check, Hint, Select, Status, useAction } from "./kit";
import { SchoolField } from "./SchoolField";

const SHIRT_SIZES: ShirtSize[] = ["XS", "S", "M", "L", "XL", "XXL", "3XL"];
const SHIRT_EU: ShirtSizeEu[] = [
  "40",
  "42",
  "44",
  "46",
  "48",
  "50",
  "52",
  "54",
  "56",
  "58",
  "60",
];
const GENDERS: Gender[] = ["male", "female", "non_binary", "prefer_not"];
const MAX_SITES = 5;

export function InfoSection() {
  return (
    <>
      <DetailsCard />
      <DeliveryCard />
    </>
  );
}

function DetailsCard() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  const [country, setCountry] = useState<string | null>(null);
  const [hidden, setHidden] = useState<PrivacyField[] | null>(null);
  const [region, setRegion] = useState<string | null>(null);
  const [sites, setSites] = useState<string[] | null>(null);
  if (!user) return null;

  const currentCountry = country ?? user.country;
  const currentHidden = hidden ?? user.hidden_fields;
  const today = new Date().toISOString().slice(0, 10);
  const urls =
    sites ??
    (user.websites?.length ? user.websites : user.website ? [user.website] : [""]);

  function visibility(field: PrivacyField, label?: string) {
    return (
      <Check
        label={label ?? t(locale, "settings.showOnProfile")}
        checked={!currentHidden.includes(field)}
        onChange={(event) => {
          const next = event.target.checked
            ? currentHidden.filter((item) => item !== field)
            : [...currentHidden, field];
          setHidden(next);
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
        gender: text("gender"),
        websites: urls.map((url) => url.trim()).filter(Boolean),
        birth_date: text("birth_date") || null,
        phone: text("phone"),
        shirt_size: text("shirt_size"),
        shirt_size_eu: text("shirt_size_eu"),
        hidden_fields: currentHidden,
      });
      await reload();
    });
    if (ok) {
      setCountry(null);
      setHidden(null);
      setRegion(null);
      setSites(null);
    }
  }

  const regionDefault = currentCountry === user.country ? user.region : "";
  const currentRegion = region ?? regionDefault;
  const districtDefault = currentRegion === user.region ? user.district : "";
  const districts =
    currentCountry === "UZ" && currentRegion ? districtOptions(currentRegion, locale) : [];

  return (
    <Card title={t(locale, "settings.info")}>
      <Hint>{t(locale, "settings.infoHint")}</Hint>
      <form onSubmit={save} className="mt-5 flex flex-col gap-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <CountrySelect
              label={t(locale, "settings.country")}
              value={currentCountry}
              allowEmpty
              onChange={(code) => {
                setCountry(code);
                setRegion(null);
              }}
            />
            {visibility("country")}
          </div>
          {currentCountry === "UZ" ? (
            <Select
              key="uz"
              label={t(locale, "settings.region")}
              name="region"
              defaultValue={regionDefault}
              onChange={setRegion}
              options={[
                { value: "", label: t(locale, "settings.notChosen") },
                ...REGION_CODES.map((code) => ({
                  value: code,
                  label: regionName(code, locale),
                })),
              ]}
            />
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
                  options={[
                    { value: "", label: t(locale, "settings.notChosen") },
                    ...[
                      { key: "settings.districts" as const, rows: districts.filter((row) => !row.city) },
                      { key: "settings.cities" as const, rows: districts.filter((row) => row.city) },
                    ].flatMap((group) =>
                      group.rows.map((row) => ({
                        value: row.code,
                        label: row.name,
                        group: t(locale, group.key),
                      })),
                    ),
                  ]}
                />
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
            <Select
              label={t(locale, "settings.grade")}
              name="grade"
              defaultValue={user.grade}
              options={[
                { value: "", label: t(locale, "settings.notChosen") },
                ...(user.grade && !isGradeCode(user.grade)
                  ? [{ value: user.grade, label: user.grade }]
                  : []),
                ...GRADE_GROUPS.flatMap((group) =>
                  group.codes.map((code) => ({
                    value: code,
                    label: gradeLabel(code, locale),
                    group: group.key ? t(locale, group.key) : undefined,
                  })),
                ),
              ]}
            />
            {visibility("grade")}
          </div>
          <div className="space-y-2">
            <Select
              label={t(locale, "settings.gender")}
              name="gender"
              defaultValue={user.gender}
              hint={t(locale, "settings.genderHint")}
              options={[
                { value: "", label: t(locale, "settings.notChosen") },
                ...GENDERS.map((value) => ({
                  value,
                  label: t(locale, `settings.gender.${value}` as MessageKey),
                })),
              ]}
            />
            {visibility("gender", t(locale, "settings.showGender"))}
          </div>
          <div className="space-y-2 sm:col-span-2">
            <p className="text-theme-sm font-medium rw-strong">{t(locale, "settings.websites")}</p>
            <Hint>{t(locale, "settings.websitesHint")}</Hint>
            <ul className="space-y-2">
              {urls.map((url, i) => (
                <li key={i} className="flex items-end gap-2">
                  <div className="min-w-0 flex-1">
                    <Field
                      label={i === 0 ? t(locale, "settings.website") : `${i + 1}`}
                      name={`website_${i}`}
                      type="url"
                      value={url}
                      onChange={(event) =>
                        setSites(urls.map((item, j) => (j === i ? event.target.value : item)))
                      }
                      hint={i === 0 ? "https://…" : undefined}
                      autoComplete="url"
                    />
                  </div>
                  {urls.length > 1 && (
                    <button
                      type="button"
                      onClick={() => setSites(urls.filter((_, j) => j !== i))}
                      aria-label={t(locale, "settings.remove")}
                      className="mb-0.5 flex size-11 shrink-0 items-center justify-center rw-radius-sm rw-dim transition rw-hover-bg rw-focus-ring"
                    >
                      <Icon name="nav.close" className="size-4" />
                    </button>
                  )}
                </li>
              ))}
            </ul>
            {urls.length < MAX_SITES && (
              <Button variant="outline" type="button" onClick={() => setSites([...urls, ""])}>
                {t(locale, "settings.addWebsite")}
              </Button>
            )}
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
          <div className="space-y-2">
            <Field
              label={t(locale, "settings.phone")}
              name="phone"
              type="tel"
              defaultValue={user.phone}
              hint={t(locale, "settings.phoneHint")}
              autoComplete="tel"
            />
          </div>
          <Select
            label={t(locale, "settings.shirtSize")}
            name="shirt_size"
            defaultValue={user.shirt_size}
            hint={t(locale, "settings.shirtSizeHint")}
            options={[
              { value: "", label: t(locale, "settings.notChosen") },
              ...SHIRT_SIZES.map((size) => ({ value: size, label: size })),
            ]}
          />
          <Select
            label={t(locale, "settings.shirtSizeEu")}
            name="shirt_size_eu"
            defaultValue={user.shirt_size_eu}
            options={[
              { value: "", label: t(locale, "settings.notChosen") },
              ...SHIRT_EU.map((size) => ({ value: size, label: size })),
            ]}
          />
        </div>

        {user.email && visibility("email", t(locale, "settings.showEmail"))}
        {visibility("online", t(locale, "settings.showOnline"))}
        {visibility("coach", t(locale, "settings.showCoach"))}
        {visibility("social", t(locale, "settings.showSocial"))}
        {visibility("activity", t(locale, "settings.showActivity"))}
        {visibility("heatmap", t(locale, "settings.showHeatmap"))}
        {visibility("recent_ac", t(locale, "settings.showRecentAc"))}

        <Status error={action.error} done={action.done} />
        <Button type="submit" busy={action.busy} className="self-start">
          {t(locale, "settings.save")}
        </Button>
      </form>
    </Card>
  );
}

function DeliveryCard() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  const erase = useAction();
  const [country, setCountry] = useState<string | null>(null);
  const [formKey, setFormKey] = useState(0);
  if (!user) return null;
  const currentCountry = country ?? user.postal_country;

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const text = (name: string) => String(form.get(name) ?? "").trim();
    await action.run(async () => {
      await patchJson("/me/", {
        postal_recipient: text("postal_recipient"),
        postal_country: currentCountry,
        postal_region: text("postal_region"),
        postal_city: text("postal_city"),
        postal_address: text("postal_address"),
        postal_code: text("postal_code"),
        postal_recipient_native: text("postal_recipient_native"),
        postal_region_native: text("postal_region_native"),
        postal_city_native: text("postal_city_native"),
        postal_address_native: text("postal_address_native"),
        postal_consent: form.get("postal_consent") === "on",
      });
      await reload();
      setCountry(null);
      setFormKey((n) => n + 1);
    });
  }

  async function clear() {
    const empty = {
      postal_recipient: "",
      postal_country: "",
      postal_region: "",
      postal_city: "",
      postal_address: "",
      postal_code: "",
      postal_recipient_native: "",
      postal_region_native: "",
      postal_city_native: "",
      postal_address_native: "",
      postal_consent: false,
    };
    const ok = await erase.run(async () => {
      await patchJson("/me/", empty);
      await reload();
    });
    if (ok) {
      setCountry("");
      setFormKey((n) => n + 1);
    }
  }

  return (
    <Card title={t(locale, "settings.delivery")}>
      <Hint>{t(locale, "settings.deliveryHint")}</Hint>
      <form key={formKey} onSubmit={save} className="mt-5 flex flex-col gap-6">
        <div className="grid gap-4 lg:grid-cols-2">
          <fieldset className="space-y-3">
            <legend className="text-theme-sm font-medium rw-strong">
              {t(locale, "settings.langEn")}
            </legend>
            <Field
              label={t(locale, "settings.postalRecipient")}
              name="postal_recipient"
              defaultValue={user.postal_recipient}
              maxLength={150}
              autoComplete="name"
            />
            <CountrySelect
              label={t(locale, "settings.country")}
              name="postal_country"
              value={currentCountry}
              allowEmpty
              onChange={setCountry}
            />
            <Field
              label={t(locale, "settings.postalRegion")}
              name="postal_region"
              defaultValue={user.postal_region}
              maxLength={80}
            />
            <Field
              label={t(locale, "settings.postalCity")}
              name="postal_city"
              defaultValue={user.postal_city}
              maxLength={100}
            />
            <Field
              label={t(locale, "settings.postalAddress")}
              name="postal_address"
              defaultValue={user.postal_address}
              maxLength={255}
            />
            <Field
              label={t(locale, "settings.postalCode")}
              name="postal_code"
              defaultValue={user.postal_code}
              maxLength={16}
              autoComplete="postal-code"
            />
          </fieldset>
          <fieldset className="space-y-3">
            <legend className="text-theme-sm font-medium rw-strong">
              {t(locale, "settings.langNative")}
            </legend>
            <Field
              label={t(locale, "settings.postalRecipientNative")}
              name="postal_recipient_native"
              defaultValue={user.postal_recipient_native}
              maxLength={150}
            />
            <Field
              label={t(locale, "settings.postalRegionNative")}
              name="postal_region_native"
              defaultValue={user.postal_region_native}
              maxLength={80}
            />
            <Field
              label={t(locale, "settings.postalCityNative")}
              name="postal_city_native"
              defaultValue={user.postal_city_native}
              maxLength={100}
            />
            <Field
              label={t(locale, "settings.postalAddressNative")}
              name="postal_address_native"
              defaultValue={user.postal_address_native}
              maxLength={255}
            />
          </fieldset>
        </div>
        <Check
          label={t(locale, "settings.postalConsent")}
          name="postal_consent"
          defaultChecked={user.postal_consent}
        />
        <Status
          error={action.error || erase.error}
          done={action.done || erase.done}
          text={erase.done ? t(locale, "settings.deliveryErased") : undefined}
        />
        <div className="flex flex-wrap gap-3">
          <Button type="submit" busy={action.busy} className="self-start">
            {t(locale, "settings.save")}
          </Button>
          <Button
            type="button"
            variant="outline"
            busy={erase.busy}
            onClick={clear}
          >
            {t(locale, "settings.deliveryErase")}
          </Button>
        </div>
      </form>
    </Card>
  );
}
