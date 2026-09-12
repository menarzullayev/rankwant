"use client";

import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
  Label,
} from "@headlessui/react";
import { useMemo, useState } from "react";

import { CountryFlag } from "@/components/ui/CountryFlag";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { countryName, countryOptions } from "@/lib/countries";

/** Mamlakat tanlagichi — qidiruv, klaviatura va bayroqlar bilan.
 *
 * Nega kutubxona (Headless UI): 249 variant uchun qidiruv va klaviatura
 * navigatsiyasi kerak, `listbox`/`option` ARIA naqshini va fokus
 * tuzog'ini qo'lda yozish esa oson xato qilinadigan joy. Headless UI
 * faqat XULQNI beradi — ko'rinish butunlay bizniki, ya'ni 12 uslub
 * tizimiga mos keladi va `rw-*` tokenlaridan foydalanadi.
 *
 * Qiymat — KOD (satr), obyekt emas: forma `FormData` bilan yig'iladi,
 * ya'ni yashirin `<input>` ga aynan kod tushishi kerak. Aks holda u
 * yerga `[object Object]` yozilardi.
 */
export function CountrySelect({
  value,
  onChange,
  label,
  hint,
  name,
  /** Sozlamalarda «tanlanmagan» holati bor — ro'yxat boshiga bo'sh
   *  variant qo'shiladi. */
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
  const [query, setQuery] = useState("");
  // `countryOptions` har renderda qayta qurilardi — endi til bo'yicha
  // keshlanadi, qidiruv jadvali ham shunga bog'lanadi.
  const options = useMemo(() => countryOptions(locale), [locale]);
  const selected = options.find((c) => c.code === value);

  // Qidiruv IKKI TILDA: nom (o'zbekcha/ruscha) + inglizcha nom + kod.
  // Sabab: odam "qoz" ham, "kazakhstan" ham yozishi mumkin, kod esa
  // har doim ishlaydi. Inglizcha nom alohida qo'shiladi, chunki
  // jadvaldagi nom boshqa tilda.
  const haystack = useMemo(
    () =>
      new Map(
        options.map((c) => [
          c.code,
          `${c.name} ${countryName(c.code, "en")} ${c.code}`.toLowerCase(),
        ]),
      ),
    [options],
  );

  const needle = query.trim().toLowerCase();
  const filtered = needle
    ? options.filter((c) => haystack.get(c.code)?.includes(needle))
    : options;

  return (
    <Combobox
      value={value}
      onChange={(code: string | null) => onChange(code ?? "")}
      name={name}
      // `as="div"` SHART: usiz Headless UI Fragment render qiladi va
      // o'z propslarini (`data-headlessui-state`) uzatib bo'lmaydi —
      // natijada SSR yiqiladi va butun sahifa ochilmaydi.
      as="div"
    >
      {/* `Label` — Headless UI input bilan yorliqni O'ZI bog'laydi
          (`htmlFor`/`id`), ya'ni `aria-label` yozish shart emas. */}
      <Label className="mb-1.5 block text-theme-sm font-medium rw-strong">
        {label}
      </Label>
      <div className="relative">
        {/* Bayroq trigger ICHIDA — chapda, ya'ni yopiq holatda ham
            tanlangan davlat ko'rinadi (native `<select>` da buning
            iloji yo'q edi). */}
        {selected && (
          <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center">
            <CountryFlag code={selected.code} />
          </span>
        )}
        <ComboboxInput
          autoComplete="off"
          className={`h-11 w-full rw-radius-sm border rw-line ${
            selected ? "pl-10" : "pl-4"
          } pr-10 text-theme-sm rw-strong outline-none transition rw-placeholder rw-focus-line rw-focus-ring rw-field-bg`}
          displayValue={(code: string) =>
            options.find((c) => c.code === code)?.name ?? ""
          }
          onChange={(event) => setQuery(event.target.value)}
          placeholder={t(locale, "geo.searchPlaceholder")}
        />
        <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center rw-faint">
          <ChevronDown />
        </span>

        <ComboboxOptions className="absolute z-60 mt-1 max-h-72 w-full overflow-y-auto rw-radius border rw-line rw-surface p-1.5 rw-shadow">
          {allowEmpty && (
            <ComboboxOption
              value=""
              className="flex cursor-pointer items-center gap-2 rw-radius-sm px-3 py-2 text-theme-sm rw-dim transition rw-hover-bg data-[focus]:rw-accent-soft"
            >
              {t(locale, "settings.notChosen")}
            </ComboboxOption>
          )}
          {filtered.length === 0 && (
            <p className="px-3 py-2 text-theme-sm rw-faint">
              {t(locale, "geo.noResults")}
            </p>
          )}
          {filtered.map((c) => (
            <ComboboxOption
              key={c.code}
              value={c.code}
              className="flex cursor-pointer items-center gap-2 rw-radius-sm px-3 py-2 text-theme-sm transition rw-hover-bg data-[focus]:rw-accent-soft"
            >
              <CountryFlag code={c.code} />
              <span className="min-w-0 truncate rw-strong">{c.name}</span>
            </ComboboxOption>
          ))}
        </ComboboxOptions>
      </div>
      {hint && <span className="mt-1.5 block text-theme-xs rw-dim">{hint}</span>}
    </Combobox>
  );
}

/** Ochilish belgisi — `@/icons` dagi to'plamga bog'lanmaslik uchun shu
 *  yerda: tanlagich o'zi bilan birga ko'chiriladigan bo'lsin. */
function ChevronDown() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="m6 9 6 6 6-6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
