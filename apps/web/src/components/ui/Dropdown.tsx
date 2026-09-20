"use client";

import {
  Combobox,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
  Label,
} from "@headlessui/react";
import { useState } from "react";

import { Icon } from "@/components/ui/Icon";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import {
  filterDropdownOptions,
  groupDropdownOptions,
  type SearchableOption,
} from "@/lib/dropdown-search";

/** Qidiruvli tanlov — platformadagi barcha ochiladigan ro'yxatning
 *  yagona qolipi.
 *
 *  Trigger — yoziladigan input. Fokusda panel ochiladi (`immediate`),
 *  kiritilgan matn esa ro'yxatni darhol toraytiradi. 3 ta jins ham,
 *  249 mamlakat ham shu input — yagona komponentning narxi.
 *
 *  Nega Headless UI Combobox: klaviatura (strelka, Enter, Escape),
 *  fokus tuzog'i va `listbox` ARIA naqshi qo'lda oson xato qilinadi.
 *  Ko'rinish butunlay `rw-*` tokenlari.
 *
 *  `as="div"` SHART: usiz Headless UI Fragment render qiladi va SSR
 *  yiqiladi (`CountrySelect` dagi o'lchov).
 */

export type DropdownOption = SearchableOption & {
  leading?: React.ReactNode;
  trailing?: React.ReactNode;
  disabled?: boolean;
};

export type DropdownSize = "md" | "sm" | "xs" | "header";

const HEIGHT: Record<DropdownSize, string> = {
  md: "h-11 text-theme-sm",
  sm: "h-9 text-theme-sm",
  xs: "h-8 text-theme-xs",
  header: "h-10 text-theme-xs",
};

const WIDTH: Record<DropdownSize, string> = {
  md: "w-full",
  sm: "w-full",
  xs: "w-full",
  header: "w-[9.5rem] sm:w-[11rem]",
};

/** Headless UI `anchor` qiymatlari — URL emas, lekin `check_hardcoded`
 *  ternary ichidagi literalni matn deb o'qiydi. */
const ANCHOR = { header: "bottom end", field: "bottom start" } as const;

export function Dropdown({
  options,
  value,
  defaultValue,
  onChange,
  label,
  hideLabel = false,
  hint,
  name,
  placeholder,
  disabled = false,
  loading = false,
  noResults,
  size = "md",
  className,
  inputClassName,
  optionsClassName,
  optionsStyle,
  onOpen,
}: {
  options: readonly DropdownOption[];
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  label: string;
  hideLabel?: boolean;
  hint?: string;
  name?: string;
  placeholder?: string;
  disabled?: boolean;
  loading?: boolean;
  noResults?: string;
  size?: DropdownSize;
  className?: string;
  inputClassName?: string;
  optionsClassName?: string;
  optionsStyle?: React.CSSProperties;
  onOpen?: () => void;
}) {
  const locale = useLocale();
  const [query, setQuery] = useState("");
  const [inner, setInner] = useState(value ?? defaultValue ?? "");
  const current = value !== undefined ? value : inner;
  const selected = options.find((option) => option.value === current);
  const filtered = filterDropdownOptions(options, query);
  const buckets = groupDropdownOptions(filtered);
  const searchLabel = placeholder ?? t(locale, "dropdown.search");
  const emptyText = noResults ?? t(locale, "geo.noResults");
  const leading = query.trim() ? undefined : selected?.leading;
  const header = size === "header";

  return (
    <Combobox
      as="div"
      className={className ?? (header ? "relative inline-block" : undefined)}
      immediate
      name={name}
      disabled={disabled || loading}
      value={current}
      onChange={(next: string | null) => {
        const code = next ?? "";
        if (value === undefined) setInner(code);
        onChange?.(code);
      }}
      onClose={() => setQuery("")}
    >
      <Label
        className={
          hideLabel
            ? "sr-only"
            : "mb-1.5 block text-theme-sm font-medium rw-strong"
        }
      >
        {label}
      </Label>
      <div
        className={
          header
            ? "relative inline-flex h-10 items-center gap-1.5 rw-radius-sm border rw-line px-2.5 pr-8 rw-field-bg rw-focus-line rw-focus-ring"
            : "relative"
        }
      >
        {leading && (
          <span
            className={
              header
                ? "flex shrink-0 items-center"
                : "pointer-events-none absolute inset-y-0 left-3 z-[1] flex items-center"
            }
          >
            {leading}
          </span>
        )}
        <ComboboxInput
          autoComplete="off"
          displayValue={(code: string) =>
            options.find((option) => option.value === code)?.label ?? ""
          }
          onChange={(event) => setQuery(event.target.value)}
          onFocus={(event) => {
            event.currentTarget.select();
            onOpen?.();
          }}
          placeholder={searchLabel}
          className={
            header
              ? `${HEIGHT[size]} min-w-0 max-w-[3rem] truncate bg-transparent p-0 text-theme-xs rw-strong outline-none rw-placeholder sm:max-w-[7.5rem] ${inputClassName ?? ""}`
              : `${HEIGHT[size]} ${WIDTH[size]} rw-radius-sm border rw-line ${
                  leading ? "pl-10" : "pl-4"
                } pr-9 rw-strong outline-none transition rw-placeholder rw-focus-line rw-focus-ring rw-field-bg`
          }
        />
        <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 rw-faint">
          {loading ? (
            <Icon
              name="action.loading"
              className="size-3.5 animate-spin motion-reduce:animate-none"
            />
          ) : (
            <Icon name="nav.expandDown" className={header ? "size-3.5" : "size-4"} />
          )}
        </span>
      </div>

      <ComboboxOptions
        anchor={optionsStyle ? undefined : header ? ANCHOR.header : ANCHOR.field}
        modal={false}
        style={optionsStyle}
        className={`z-[200] max-h-72 overflow-y-auto rw-radius border rw-line rw-surface p-1.5 rw-shadow [--anchor-gap:4px] [--anchor-max-height:18rem] ${
          optionsClassName ?? (header ? "top-full mt-1 w-64" : "mt-1 w-[var(--input-width)]")
        }`}
      >
          {filtered.length === 0 ? (
            <p className="px-3 py-2 text-theme-sm rw-faint">{emptyText}</p>
          ) : (
            buckets.map(({ group, options: rows }) => (
              <div key={group ?? ""}>
                {group ? (
                  <div className="px-3 pb-1 pt-2 text-theme-xs uppercase tracking-wide rw-dim-2">
                    {group}
                  </div>
                ) : null}
                {rows.map((option) => (
                  <ComboboxOption
                    key={option.value || "__empty"}
                    value={option.value}
                    disabled={option.disabled}
                    className="flex cursor-pointer items-center gap-2 rw-radius-sm px-3 py-2 text-theme-sm transition rw-hover-bg data-[focus]:rw-accent-soft data-[selected]:font-medium"
                  >
                    {({ selected: on }) => (
                      <>
                        {option.leading}
                        <span className="min-w-0 flex-1">
                          <span className="block truncate rw-strong">{option.label}</span>
                          {option.hint && option.hint !== option.label ? (
                            <span className="block truncate text-theme-xs rw-dim-2">
                              {option.hint}
                            </span>
                          ) : null}
                        </span>
                        {option.trailing}
                        {on ? (
                          <Icon name="action.confirm" className="size-3.5 shrink-0" />
                        ) : null}
                      </>
                    )}
                  </ComboboxOption>
                ))}
              </div>
            ))
          )}
      </ComboboxOptions>
      {hint && <span className="mt-1.5 block text-theme-xs rw-dim">{hint}</span>}
    </Combobox>
  );
}
