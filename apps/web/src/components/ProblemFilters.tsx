"use client";

import type { Route } from "next";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { LOCALE_NAMES, type Locale } from "@/i18n/messages";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { CloseIcon, SearchIcon } from "@/icons";
import { useHideTags } from "@/lib/hideTags";

export type FilterTopic = { slug: string; label: string };

// ⚠️ Ikkala element: qiymat (URL'ga ketadi) va tarjima KALITI.
// Ilgari ikkinchisi tayyor o'zbekcha matn edi — filtr panelining
// hamma yozuvi 9 tilda ham o'zbekcha qolardi. Kalitlarni o'zgartirsangiz
// `uz.ts` dagi `filter.*` kalitlarini ham yangilang.
const SORTS = [
  ["difficulty", "filter.sort.easiest"],
  ["-difficulty", "filter.sort.hardest"],
  ["-solved_count", "filter.sort.mostSolved"],
  ["-created_at", "filter.sort.newest"],
] as const;

const LEVELS = [
  ["beginner", "level.beginner"],
  ["basic", "level.basic"],
  ["intermediate", "level.intermediate"],
  ["upper", "level.upper"],
  ["hard", "level.hard"],
  ["expert", "level.expert"],
  ["master", "level.master"],
] as const;

const STATUSES = [
  ["solved=false", "filter.status.unsolved"],
  ["solved=true", "filter.status.solved"],
  // Urinilgan — `solved=false` bilan birga «taqalib qolganlar».
  ["attempted=true", "filter.status.attempted"],
  ["favourite=true", "filter.status.favourites"],
  ["recommended=true", "filter.status.recommended"],
] as const;

/** Panelda boshqariladigan kalitlar — saralash va qidiruv panelda emas,
 * shuning uchun rozetkada ular hisoblanmaydi. */
const PANEL_KEYS = [
  "level",
  "topics",
  "solved",
  "attempted",
  "favourite",
  "recommended",
  "statement_locale",
] as const;

// Til nomlari `LOCALE_NAMES` dan olinadi (messages.ts): ular ENDONIM —
// har bir til o'z nomi bilan yoziladi va tarjima qilinmaydi. Ilgari bu
// yerda alohida xarita bor edi va u faqat `uz`/`ru`/`en` ni bilardi,
// ya'ni qolgan 7 til kod bo'lib chiqardi.

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
  const locale = useLocale();
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
    next.delete("attempted");
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
      : params.get("attempted")
        ? "attempted=true"
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
          aria-label={t(locale, "filter.sortLabel")}
        >
          {SORTS.map(([value, labelKey]) => (
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
              {t(locale, labelKey)}
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
            placeholder={t(locale, "filter.searchPlaceholder")}
            aria-label={t(locale, "filter.searchLabel")}
            className="h-9 w-52 rw-radius-sm border rw-line bg-transparent pr-3 pl-9 text-theme-sm rw-strong outline-none rw-placeholder rw-focus-line"
          />
        </label>

        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          className={`${chip} border rw-line ${activeCount ? "rw-accent-ink" : "rw-dim-2"} rw-hover-bg`}
        >
          {t(locale, "filter.filters")}
          {activeCount > 0 && (
            <span className="ml-2 flex size-5 items-center justify-center rounded-full rw-accent-bg text-theme-xs">
              {activeCount}
            </span>
          )}
        </button>
      </div>

      {open && (
        <div className="rw-panel space-y-4 p-4">
          <Group label={t(locale, "filter.levelLabel")}>
            <Option
              active={!params.get("level")}
              onClick={() => set("level", "")}
              label={t(locale, "filter.all")}
            />
            {LEVELS.map(([value, labelKey]) => (
              <Option
                key={value}
                active={params.get("level") === value}
                onClick={() => set("level", value)}
                label={t(locale, labelKey)}
              />
            ))}
          </Group>

          {signedIn && (
            <Group label={t(locale, "filter.statusLabel")}>
              <Option
                active={!activeStatus}
                onClick={() => setStatus("")}
                label={t(locale, "filter.all")}
              />
              {STATUSES.map(([value, labelKey]) => (
                <Option
                  key={value}
                  active={activeStatus === value}
                  onClick={() => setStatus(value)}
                  label={t(locale, labelKey)}
                />
              ))}
            </Group>
          )}

          <Group
            // Ikkitadan ko'p tanlanganda semantikani aytib qo'yish kerak:
            // filtr HAMMASI bo'lgan masalalarni beradi, yig'indini emas.
            label={`${t(locale, "filter.topicsLabel")}${
              selectedTopics.length > 1
                ? ` (${selectedTopics.length} — ${t(locale, "filter.all").toLowerCase()})`
                : selectedTopics.length
                  ? ` (${selectedTopics.length})`
                  : ""
            }`}
          >
            <TopicOptions
              topics={topics}
              selected={selectedTopics}
              onToggle={toggleTopic}
            />
          </Group>

          {locales.length > 1 && (
            <Group label={t(locale, "filter.statementLocaleLabel")}>
              <Option
                active={!params.get("statement_locale")}
                onClick={() => set("statement_locale", "")}
                label={t(locale, "filter.all")}
              />
              {locales.map((code) => (
                <Option
                  key={code}
                  active={params.get("statement_locale") === code}
                  onClick={() => set("statement_locale", code)}
                  label={LOCALE_NAMES[code as Locale] ?? code}
                />
              ))}
            </Group>
          )}

          <Group label={t(locale, "filter.viewLabel")}>
            <Option
              active={hideTags}
              onClick={() => setHideTags(!hideTags)}
              label={t(locale, "filter.hideTagsUnsolved")}
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
              {t(locale, "filter.clear")}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

/** Mavzu tanlash.
 *
 * Arxiv 2000 masalaga yetganda mavzu ham 100 dan oshdi va tekis ro'yxat
 * ishlamay qoldi: kerakli yorliqni ko'z bilan izlash panelni ochishdan
 * ko'ra uzoqroq. Qidiruv maydoni ro'yxat uzun bo'lgandagina chiqadi —
 * beshta mavzu uchun u ortiqcha bo'lardi.
 *
 * Tanlanganlar qidiruvdan QAT'IY NAZAR yuqorida qoladi, aks holda
 * yozishni boshlash bilan ular ko'zdan yo'qolardi va foydalanuvchi
 * nimani tanlaganini unutardi. */
function TopicOptions({
  topics,
  selected,
  onToggle,
}: {
  topics: FilterTopic[];
  selected: string[];
  onToggle: (slug: string) => void;
}) {
  const [query, setQuery] = useState("");
  const locale = useLocale();
  const needle = query.trim().toLocaleLowerCase("uz");
  const shown = topics.filter(
    (topic) =>
      selected.includes(topic.slug) ||
      topic.label.toLocaleLowerCase("uz").includes(needle),
  );

  return (
    <>
      {topics.length > 15 && (
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={fill(t(locale, "filter.topicSearchPlaceholder"), {
            count: topics.length,
          })}
          aria-label={t(locale, "filter.topicSearchLabel")}
          className="mb-1.5 h-8 w-full rw-radius-sm border rw-line rw-field-bg px-2.5 text-theme-sm rw-strong rw-focus-line"
        />
      )}
      <div className="flex max-h-64 flex-wrap gap-1.5 overflow-y-auto">
        {shown.map((topic) => (
          <Option
            key={topic.slug}
            active={selected.includes(topic.slug)}
            onClick={() => onToggle(topic.slug)}
            label={topic.label}
          />
        ))}
        {shown.length === 0 && (
          <p className="text-theme-sm rw-faint">
            {t(locale, "filter.noTopicMatch")}
          </p>
        )}
      </div>
    </>
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
