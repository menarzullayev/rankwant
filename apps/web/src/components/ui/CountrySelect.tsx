"use client";

import { CountryFlag } from "@/components/ui/CountryFlag";
import { Dropdown } from "@/components/ui/Dropdown";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { countryName, countryOptions } from "@rankwant/shared/countries";

/** Mamlakat tanlagichi — yagona `Dropdown` qolipi, bayroqlar bilan.
 *
 * Qiymat — KOD (satr), obyekt emas: forma `FormData` bilan yig'iladi.
 */

export function CountrySelect({
  value,
  onChange,
  label,
  hint,
  name,
  allowEmpty = false,
}: {
  value: string;
  onChange: (code: string) => void;
  label: string;
  hint?: string;
  name?: string;
  allowEmpty?: boolean;
}) {
  const locale = useLocale();
  const catalog = countryOptions(locale);
  const options = [
    ...(allowEmpty
      ? [{ value: "", label: t(locale, "settings.notChosen") }]
      : []),
    ...catalog.map((country) => ({
      value: country.code,
      label: country.name,
      keywords: `${countryName(country.code, "en")} ${country.code}`,
      leading: <CountryFlag code={country.code} />,
    })),
  ];

  return (
    <Dropdown
      label={label}
      hint={hint}
      name={name}
      value={value}
      onChange={onChange}
      options={options}
      placeholder={t(locale, "geo.searchPlaceholder")}
    />
  );
}
