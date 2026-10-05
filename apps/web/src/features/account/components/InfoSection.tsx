"use client";

import type { Route } from "next";
import Link from "next/link";
import { useState } from "react";

import { FormBox } from "@/components/form/FormKit";

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
import { GRADE_GROUPS, gradeLabel, isGradeCode } from "@rankwant/shared/grades";
import { REGION_CODES, districtOptions, regionName } from "@rankwant/shared/regions";
import { SavedForm, useSaveSlot } from "./SaveBar";
import { Check, Hint, Select, Status, useAction } from "./section-kit";
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

/** What a visitor can be shown, in the order the profile shows it. Each key
 *  is one entry of `hidden_fields`; the label says what switching it ON does. */
const PRIVACY_ROWS: { field: PrivacyField; label: MessageKey }[] = [
  { field: "country", label: "settings.country" },
  { field: "school", label: "settings.school" },
  { field: "grade", label: "settings.grade" },
  { field: "birth_date", label: "settings.birthDate" },
  { field: "gender", label: "settings.gender" },
  { field: "website", label: "settings.website" },
  { field: "email", label: "settings.email" },
  { field: "coach", label: "settings.privacy.coach" },
  { field: "social", label: "settings.privacy.social" },
  { field: "online", label: "settings.privacy.online" },
  { field: "activity", label: "settings.privacy.activity" },
  { field: "heatmap", label: "settings.privacy.heatmap" },
  { field: "recent_ac", label: "settings.privacy.recentAc" },
  { field: "title_photo", label: "settings.privacy.titlePhoto" },
];

/** Who sees what — one table instead of a checkbox under each field
 *  (decision of 2026-10-05). Scattered through a 34-field form, the
 *  fourteen switches gave no picture of the profile as a visitor gets it. */
export function PrivacyCard() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  const [hidden, setHidden] = useState<PrivacyField[] | null>(null);
  const current = hidden ?? user?.hidden_fields ?? [];

  const save = async () => {
    const ok = await action.run(async () => {
      await patchJson("/me/", { hidden_fields: current });
      await reload();
    });
    if (ok) setHidden(null);
    return ok;
  };
  useSaveSlot(hidden !== null, save, () => setHidden(null));
  if (!user) return null;

  return (
    <Card
      title={t(locale, "settings.privacy.title")}
      action={
        <Link
          href={`/users/${user.username}` as Route}
          className="text-theme-sm rw-accent-ink hover:underline"
        >
          {t(locale, "settings.privacy.preview")}
        </Link>
      }
    >
      <Hint>{t(locale, "settings.privacy.hint")}</Hint>
      <ul className="mt-4 divide-y rw-divide">
        {PRIVACY_ROWS.filter((row) => row.field !== "email" || user.email).map((row) => {
          const shown = !current.includes(row.field);
          const label = t(locale, row.label);
          return (
            <li key={row.field} className="flex items-center justify-between gap-4 py-3">
              <span className="min-w-0">
                <span className="block text-theme-sm font-medium rw-strong">{label}</span>
                <span className="block text-theme-xs rw-dim">
                  {t(locale, shown ? "settings.privacy.shown" : "settings.privacy.hidden")}
                </span>
              </span>
              <FormBox
                shape="switch"
                checked={shown}
                aria-label={label}
                onChange={(event) =>
                  setHidden(
                    event.target.checked
                      ? current.filter((item) => item !== row.field)
                      : [...current, row.field],
                  )
                }
              />
            </li>
          );
        })}
      </ul>
      <div className="mt-3">
        <Status error={action.error} done={action.done} />
      </div>
    </Card>
  );
}

export function DetailsCard() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  const [country, setCountry] = useState<string | null>(null);
  const [region, setRegion] = useState<string | null>(null);
  const [sites, setSites] = useState<string[] | null>(null);
  if (!user) return null;

  const currentCountry = country ?? user.country;
  const today = new Date().toISOString().slice(0, 10);
  const urls =
    sites ??
    (user.websites?.length ? user.websites : user.website ? [user.website] : [""]);

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
      });
      await reload();
    });
    if (ok) clear();
    return ok;
  }

  function clear() {
    setCountry(null);
    setRegion(null);
    setSites(null);
  }

  const regionDefault = currentCountry === user.country ? user.region : "";
  const currentRegion = region ?? regionDefault;
  const districtDefault = currentRegion === user.region ? user.district : "";
  const districts =
    currentCountry === "UZ" && currentRegion ? districtOptions(currentRegion, locale) : [];

  return (
    <Card title={t(locale, "settings.info")}>
      <Hint>{t(locale, "settings.infoHint")}</Hint>
      <SavedForm
        onSubmit={save}
        onReset={clear}
        dirty={country !== null || sites !== null}
        className="mt-5 flex flex-col gap-6"
      >
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


        <Status error={action.error} done={action.done} />
      </SavedForm>
    </Card>
  );
}

export function DeliveryCard() {
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
    return action.run(async () => {
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
      <SavedForm
        key={formKey}
        onSubmit={save}
        onReset={() => setCountry(null)}
        dirty={country !== null}
        className="mt-5 flex flex-col gap-6"
      >
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
        <Button
          type="button"
          variant="outline"
          busy={erase.busy}
          onClick={clear}
          className="self-start"
        >
          {t(locale, "settings.deliveryErase")}
        </Button>
      </SavedForm>
    </Card>
  );
}
