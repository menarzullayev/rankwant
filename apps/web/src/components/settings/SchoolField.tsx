"use client";

import { useEffect, useState } from "react";

import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { getJson, type Paginated, type School } from "@/lib/api";
import { regionName } from "@/lib/regions";

/** Maktab — katalogdan tanlash yoki erkin matn (ADR-0017). Katalogdagi maktab
 *  `school_ref` bo'lib saqlanadi: maktab reytingi va sinfdoshlar shunga tayanadi. */
export function SchoolField({
  label,
  initialName,
  initialId,
}: {
  label: string;
  initialName: string;
  initialId: number | null;
}) {
  const locale = useLocale();
  const [text, setText] = useState(initialName);
  const [id, setId] = useState<number | null>(initialId);
  const [options, setOptions] = useState<School[]>([]);

  // Katalogdan tanlangan yoki juda qisqa matnda ro'yxat ko'rsatilmaydi —
  // bu holat hisoblanadi, effektda tozalanmaydi.
  const searching = id === null && text.trim().length >= 2;

  useEffect(() => {
    if (!searching) return;
    const q = text.trim();
    const timer = setTimeout(() => {
      getJson<Paginated<School>>(`/schools/?q=${encodeURIComponent(q)}&page_size=8`)
        .then((page) => setOptions(page.results))
        .catch(() => setOptions([]));
    }, 250);
    return () => clearTimeout(timer);
  }, [text, searching]);
  const visible = searching ? options : [];

  return (
    <div className="relative">
      <Field
        label={label}
        name="school"
        value={text}
        onChange={(event) => {
          setText(event.target.value);
          setId(null);
        }}
        maxLength={150}
        autoComplete="off"
        hint={t(locale, id === null ? "settings.schoolFreeText" : "settings.schoolFromCatalog")}
      />
      <input type="hidden" name="school_ref" value={id ?? ""} />
      {visible.length > 0 && (
        <ul className="absolute inset-x-0 z-20 mt-1 max-h-64 overflow-y-auto rw-radius-sm border rw-line rw-surface rw-shadow">
          {visible.map((school) => (
            <li key={school.id}>
              <button
                type="button"
                onClick={() => {
                  setText(school.name);
                  setId(school.id);
                }}
                className="block w-full px-3 py-2 text-left text-theme-sm rw-strong rw-hover-bg rw-focus-ring"
              >
                {school.name}
                {school.region && (
                  <span className="ml-1.5 rw-faint">· {regionName(school.region, locale)}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
