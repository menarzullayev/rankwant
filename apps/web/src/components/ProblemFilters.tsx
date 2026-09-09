"use client";

import type { Route } from "next";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { CloseIcon, SearchIcon } from "@/icons";
import { useHideTags } from "@/lib/hideTags";

export type FilterTopic = { slug: string; label: string };

const SORTS = [
  ["difficulty", "Eng oson"],
  ["-difficulty", "Eng qiyin"],
  ["-solved_count", "Ko'p yechilgan"],
  ["-created_at", "Yangi"],
] as const;

const LEVELS = [
  ["beginner", "Boshlang'ich"],
  ["basic", "Asosiy"],
  ["intermediate", "O'rta"],
  ["upper", "Yaxshi"],
  ["hard", "Qiyin"],
  ["expert", "Ekspert"],
  ["master", "Master"],
] as const;

const STATUSES = [
  ["solved=false", "Yechilmagan"],
  ["solved=true", "Yechilgan"],
  ["favourite=true", "Sevimlilarim"],
  ["recommended=true", "Menga tavsiya"],
] as const;

/** Panelda boshqariladigan kalitlar — saralash va qidiruv panelda emas,
 * shuning uchun rozetkada ular hisoblanmaydi. */
const PANEL_KEYS = [
  "level",
  "topics",
  "solved",
  "favourite",
  "recommended",
  "statement_locale",
] as const;

const LOCALE_LABELS: Record<string, string> = {
  uz: "O'zbekcha",
  ru: "Ruscha",
  en: "Inglizcha",
};

export function ProblemFilters({
  topics,
  locales,
  signedIn,
}: {
  topics: FilterTopic[];
  locales: string[];
  signedIn: boolean;
}) {
  const [hideTags, setHideTags] = useHideTags();
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const [open, setOpen] = useState(false);
  const [term, setTerm] = useState(params.get("search") ?? "");
  const typed = useRef(false);

  const push = (next: URLSearchParams) => {
    // Filtr o'zgarsa 5-sahifada qolib ketib bo'lmaydi — natija boshqa.
    next.delete("page");
    router.push(`${pathname}${next.size ? `?${next}` : ""}` as Route);
  };

  const set = (name: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(name, value);
    else next.delete(name);
    push(next);
  };

  const setStatus = (value: string) => {
    const next = new URLSearchParams(params);
    next.delete("solved");
    next.delete("favourite");
    next.delete("recommended");
    if (value) {
      const [key, raw] = value.split("=");
      next.set(key, raw);
    }
    push(next);
  };

  const selectedTopics = (params.get("topics") ?? "")
    .split(",")
    .filter(Boolean);

  const toggleTopic = (slug: string) => {
    const next = selectedTopics.includes(slug)
      ? selectedTopics.filter((s) => s !== slug)
      : [...selectedTopics, slug];
    set("topics", next.join(","));
  };

  // Qidiruv har harfda so'rov yubormaydi — yozib bo'lgach. Manzil
  // o'zgarmasa push ham qilinmaydi: aks holda `params` yangilanishi
  // effektni qayta ishga tushirib, cheksiz navigatsiya hosil qilardi.
  useEffect(() => {
    if (!typed.current) return;
    const handle = setTimeout(() => {
      const next = new URLSearchParams(params);
      const value = term.trim();
      if (value) next.set("search", value);
      else next.delete("search");
      next.delete("page");
      const target = `${pathname}${next.size ? `?${next}` : ""}`;
      const current = `${pathname}${params.size ? `?${params}` : ""}`;
      if (target !== current) router.push(target as Route);
    }, 400);
    return () => clearTimeout(handle);
  }, [term, params, pathname, router]);

  const activeStatus = params.get("recommended")
    ? "recommended=true"
    : params.get("favourite")
      ? "favourite=true"
      : params.get("solved")
        ? `solved=${params.get("solved")}`
        : "";

  const activeCount = PANEL_KEYS.filter((key) => params.get(key)).length;
  const sort = params.get("ordering") ?? "difficulty";

  const chip =
    "flex h-9 items-center rw-radius-sm px-3 text-theme-sm font-medium transition";

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <div
          className="flex flex-wrap items-center gap-1 rw-radius-sm rw-chip p-1"
          role="tablist"
          aria-label="Saralash"
        >
          {SORTS.map(([value, label]) => (
            <button
              key={value}
              type="button"
              role="tab"
              aria-selected={sort === value}
              onClick={() => set("ordering", value)}
              className={`${chip} ${
                sort === value
                  ? "rw-surface rw-strong rw-shadow"
                  : "rw-dim rw-hover-bg"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <label className="relative ml-auto">
          <SearchIcon className="pointer-events-none absolute top-2.5 left-3 size-4 rw-faint" />
          <input
            type="search"
            value={term}
            onChange={(e) => {
              typed.current = true;
              setTerm(e.target.value);
            }}
            placeholder="Masala qidirish…"
            aria-label="Masala qidirish"
            className="h-9 w-52 rw-radius-sm border rw-line bg-transparent pr-3 pl-9 text-theme-sm rw-strong outline-none rw-placeholder rw-focus-line"
          />
        </label>

        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          className={`${chip} border rw-line ${activeCount ? "rw-accent-ink" : "rw-dim-2"} rw-hover-bg`}
        >
          Filtrlar
          {activeCount > 0 && (
            <span className="ml-2 flex size-5 items-center justify-center rounded-full rw-accent-bg text-theme-xs">
              {activeCount}
            </span>
          )}
        </button>
      </div>

      {open && (
        <div className="rw-panel space-y-4 p-4">
          <Group label="Daraja">
            <Option
              active={!params.get("level")}
              onClick={() => set("level", "")}
              label="Hammasi"
            />
            {LEVELS.map(([value, label]) => (
              <Option
                key={value}
                active={params.get("level") === value}
                onClick={() => set("level", value)}
                label={label}
              />
            ))}
          </Group>

          {signedIn && (
            <Group label="Holat">
              <Option
                active={!activeStatus}
                onClick={() => setStatus("")}
                label="Hammasi"
              />
              {STATUSES.map(([value, label]) => (
                <Option
                  key={value}
                  active={activeStatus === value}
                  onClick={() => setStatus(value)}
                  label={label}
                />
              ))}
            </Group>
          )}

          <Group
            // Ikkitadan ko'p tanlanganda semantikani aytib qo'yish kerak:
            // filtr HAMMASI bo'lgan masalalarni beradi, yig'indini emas.
            label={`Mavzular${
              selectedTopics.length > 1
                ? ` (${selectedTopics.length} — hammasi)`
                : selectedTopics.length
                  ? ` (${selectedTopics.length})`
                  : ""
            }`}
          >
            {topics.map((topic) => (
              <Option
                key={topic.slug}
                active={selectedTopics.includes(topic.slug)}
                onClick={() => toggleTopic(topic.slug)}
                label={topic.label}
              />
            ))}
          </Group>

          {locales.length > 1 && (
            <Group label="Matn tili">
              <Option
                active={!params.get("statement_locale")}
                onClick={() => set("statement_locale", "")}
                label="Hammasi"
              />
              {locales.map((code) => (
                <Option
                  key={code}
                  active={params.get("statement_locale") === code}
                  onClick={() => set("statement_locale", code)}
                  label={LOCALE_LABELS[code] ?? code}
                />
              ))}
            </Group>
          )}

          <Group label="Ko'rinish">
            <Option
              active={hideTags}
              onClick={() => setHideTags(!hideTags)}
              label="Yechilmaganlarda mavzuni yashirish"
            />
          </Group>

          {activeCount > 0 && (
            <button
              type="button"
              onClick={() => {
                const next = new URLSearchParams(params);
                PANEL_KEYS.forEach((key) => next.delete(key));
                push(next);
              }}
              className="flex items-center gap-1.5 text-theme-sm rw-dim transition rw-hover-strong"
            >
              <CloseIcon className="size-4" />
              Filtrlarni tozalash
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function Group({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <p className="mb-1.5 text-theme-xs font-medium tracking-wider rw-faint uppercase">
        {label}
      </p>
      <div className="flex flex-wrap gap-1.5">{children}</div>
    </div>
  );
}

function Option({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`rw-radius-sm border px-3 py-1.5 text-theme-sm transition ${
        active
          ? "rw-accent-soft rw-accent-ink rw-accent-line"
          : "rw-line rw-dim-2 rw-hover-bg"
      }`}
    >
      {label}
    </button>
  );
}
