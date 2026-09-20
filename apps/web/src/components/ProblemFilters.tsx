"use client";

import type { Route } from "next";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { LOCALE_NAMES, type Locale } from "@/i18n/messages";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { FormTreeItem } from "@/components/kit/FormExtras";
import { Icon } from "@/components/ui/Icon";
import { UzFallbackBadge } from "@/components/ui/UzFallbackBadge";
import { useSession } from "@/context/SessionContext";
import { useHideTags } from "@/lib/hideTags";
import { announcePrefs } from "@/lib/prefs";

/** `fallback` — `label` o'zbekchadan olingan (kontent nomlari faqat
 *  uz/ru/en ustunlarida). Ro'yxatda `uz` belgisi shu bayroqdan chiziladi,
 *  ya'ni qaysi til qaytish berayotganini filtr o'zi taxmin qilmaydi. */
export type FilterTopic = {
  slug: string;
  label: string;
  parent: string | null;
  fallback: boolean;
};

/** Matches `problems.models.DIFFICULTY_LEVELS` — chips set the CF range. */
const LEVEL_RANGES = [
  ["beginner", 800, 999],
  ["basic", 1000, 1199],
  ["intermediate", 1200, 1499],
  ["upper", 1500, 1799],
  ["hard", 1800, 2199],
  ["expert", 2200, 2699],
  ["master", 2700, 3500],
] as const;

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

/** Status filters; any of them in the URL overrides the "hide solved"
 * default that `app/problems/page.tsx` applies (ADR-0024). */
const STATUS_KEYS = ["solved", "attempted", "favourite", "recommended"] as const;

/** Panelda boshqariladigan kalitlar — saralash va qidiruv panelda emas,
 * shuning uchun rozetkada ular hisoblanmaydi. */
const PANEL_KEYS = [
  "level",
  "difficulty__gte",
  "difficulty__lte",
  "topics",
  "exclude_topics",
  "solved",
  "attempted",
  "favourite",
  "recommended",
  "statement_locale",
] as const;

/** The three URL shapes that all mean the same thing: "which difficulty".
 *  `PANEL_KEYS` counts one filter per param, but a preset chip writes BOTH
 *  range bounds, so the badge read "Filtrlar2" for a single "Qiyin" chip.
 *  `level` is the pre-#90 spelling, still honoured on read. */
const DIFFICULTY_KEYS: readonly string[] = [
  "level",
  "difficulty__gte",
  "difficulty__lte",
];

/** Mavzu query kalitlari — URL'ga ketadi, tarjima qilinmaydi.
 *  Konstantada saqlanadi: `check_hardcoded.py` ternary ichidagi
 *  literalni qattiq yozilgan matn deb o'qiydi. */
const TOPIC_LIST = { include: "topics", exclude: "exclude_topics" } as const;

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
  const accountHideSolved = Boolean(useSession().user?.ui_prefs?.problemset?.hideSolved);
  // Optimistic until the session reloads with the saved value.
  const [hideSolvedChoice, setHideSolvedChoice] = useState<boolean | null>(null);
  const hideSolved = hideSolvedChoice ?? accountHideSolved;
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
    // With "hide solved" on the server hides them by default, so "all" has
    // to be explicit.
    const target = value || (hideSolved ? "solved=any" : "");
    if (target) {
      const [key, raw] = target.split("=");
      next.set(key, raw);
    }
    push(next);
  };

  const toggleHideSolved = () => {
    const next = !hideSolved;
    setHideSolvedChoice(next);
    announcePrefs({ problemset: { hideSolved: next } });
    // The server uses the new default only once the PATCH lands; until then
    // an explicit status keeps the list in step. A status the person chose stays.
    if (!STATUS_KEYS.some((key) => params.get(key))) setStatus(next ? "solved=false" : "solved=any");
  };

  const selectedTopics = (params.get("topics") ?? "")
    .split(",")
    .filter(Boolean);

  const excludedTopics = (params.get("exclude_topics") ?? "")
    .split(",")
    .filter(Boolean);

  const range = (() => {
    const gte = params.get("difficulty__gte");
    const lte = params.get("difficulty__lte");
    if (gte || lte) return { gte: gte ?? "", lte: lte ?? "" };
    const preset = LEVEL_RANGES.find(([code]) => code === params.get("level"));
    return preset
      ? { gte: String(preset[1]), lte: String(preset[2]) }
      : { gte: "", lte: "" };
  })();

  const applyRange = (gte: string, lte: string) => {
    const next = new URLSearchParams(params);
    next.delete("level");
    if (gte) next.set("difficulty__gte", gte);
    else next.delete("difficulty__gte");
    if (lte) next.set("difficulty__lte", lte);
    else next.delete("difficulty__lte");
    push(next);
  };

  const toggleList = (name: (typeof TOPIC_LIST)[keyof typeof TOPIC_LIST], slug: string) => {
    const current = (params.get(name) ?? "").split(",").filter(Boolean);
    const nextSlugs = current.includes(slug)
      ? current.filter((s) => s !== slug)
      : [...current, slug];
    const next = new URLSearchParams(params);
    const other = name === TOPIC_LIST.include ? TOPIC_LIST.exclude : TOPIC_LIST.include;
    const otherSlugs = (params.get(other) ?? "")
      .split(",")
      .filter((s) => s && s !== slug);
    if (otherSlugs.length) next.set(other, otherSlugs.join(","));
    else next.delete(other);
    if (nextSlugs.length) next.set(name, nextSlugs.join(","));
    else next.delete(name);
    push(next);
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
        : params.get("solved") && params.get("solved") !== "any"
          ? `solved=${params.get("solved")}`
          : !STATUS_KEYS.some((key) => params.get(key)) && hideSolved
            ? "solved=false"
            : "";

  // Difficulty is ONE filter, not one per param: a preset chip writes both
  // bounds, manual entry may write only one, and an old `?level=` link carries
  // the same choice in a third shape. The rest still count one per key.
  const activeCount =
    PANEL_KEYS.filter(
      (key) => !DIFFICULTY_KEYS.includes(key) && params.get(key),
    ).length + (DIFFICULTY_KEYS.some((key) => params.get(key)) ? 1 : 0);
  const sort = params.get("ordering") ?? "difficulty";

  const chip =
    "flex h-9 items-center rw-radius-sm px-3 text-theme-sm font-medium transition";

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <div
          className="rw-kit-tabs flex flex-wrap items-center gap-1 rw-radius-sm rw-chip p-1"
          data-kit-tabs="chips"
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
          <Icon name="action.search" className="pointer-events-none absolute top-2.5 left-3 size-4 rw-faint" />
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
              active={!range.gte && !range.lte}
              onClick={() => applyRange("", "")}
              label={t(locale, "filter.all")}
            />
            {LEVELS.map(([value, labelKey], index) => {
              const [, lo, hi] = LEVEL_RANGES[index];
              const active = range.gte === String(lo) && range.lte === String(hi);
              return (
                <Option
                  key={value}
                  active={active}
                  onClick={() => applyRange(String(lo), String(hi))}
                  label={t(locale, labelKey)}
                />
              );
            })}
            <div className="flex w-full flex-wrap items-center gap-2 pt-1">
              <label className="flex items-center gap-1.5 text-theme-sm rw-dim">
                {t(locale, "filter.difficultyMin")}
                <input
                  type="number"
                  min={800}
                  max={3500}
                  step={100}
                  value={range.gte}
                  onChange={(event) => applyRange(event.target.value, range.lte)}
                  className="h-8 w-20 rw-radius-sm border rw-line rw-field-bg px-2 text-theme-sm rw-strong rw-focus-line rw-fm-inp"
                />
              </label>
              <label className="flex items-center gap-1.5 text-theme-sm rw-dim">
                {t(locale, "filter.difficultyMax")}
                <input
                  type="number"
                  min={800}
                  max={3500}
                  step={100}
                  value={range.lte}
                  onChange={(event) => applyRange(range.gte, event.target.value)}
                  className="h-8 w-20 rw-radius-sm border rw-line rw-field-bg px-2 text-theme-sm rw-strong rw-focus-line rw-fm-inp"
                />
              </label>
            </div>
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
            label={`${t(locale, "filter.topicsInclude")}${
              selectedTopics.length ? ` (${selectedTopics.length})` : ""
            }`}
          >
            <TopicOptions
              topics={topics}
              selected={selectedTopics}
              onToggle={(slug) => toggleList(TOPIC_LIST.include, slug)}
            />
          </Group>

          <Group
            label={`${t(locale, "filter.topicsExclude")}${
              excludedTopics.length ? ` (${excludedTopics.length})` : ""
            }`}
          >
            <TopicOptions
              topics={topics}
              selected={excludedTopics}
              onToggle={(slug) => toggleList(TOPIC_LIST.exclude, slug)}
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
            {signedIn && (
              <Option
                active={hideSolved}
                onClick={toggleHideSolved}
                label={t(locale, "filter.hideSolved")}
              />
            )}
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
              <Icon name="nav.close" className="size-4" />
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
  const known = new Set(topics.map((topic) => topic.slug));
  const match = (topic: FilterTopic) =>
    selected.includes(topic.slug) ||
    !needle ||
    topic.label.toLocaleLowerCase("uz").includes(needle);

  const roots = topics.filter(
    (topic) => !topic.parent || !known.has(topic.parent),
  );
  const childrenOf = (slug: string) =>
    topics.filter((topic) => topic.parent === slug);

  const visibleRoots = roots.filter(
    (root) =>
      match(root) ||
      childrenOf(root.slug).some(match) ||
      selected.includes(root.slug),
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
          className="mb-1.5 h-8 w-full rw-radius-sm border rw-line rw-field-bg px-2.5 text-theme-sm rw-strong rw-focus-line rw-fm-inp"
        />
      )}
      <div className="max-h-64 space-y-2 overflow-y-auto">
        {visibleRoots.map((root) => {
          const children = childrenOf(root.slug).filter(
            (child) => match(child) || selected.includes(child.slug),
          );
          const open = selected.includes(root.slug) || children.some((c) => selected.includes(c.slug)) || Boolean(needle);
          return (
            <div key={root.slug} className="rw-kit-tree">
              <FormTreeItem
                label={root.label}
                fallback={root.fallback}
                checked={selected.includes(root.slug)}
                indeterminate={
                  children.some((c) => selected.includes(c.slug)) &&
                  !selected.includes(root.slug)
                }
                extra={root.fallback ? <UzFallbackBadge locale={locale} /> : null}
                onChange={() => onToggle(root.slug)}
              />
              {open && children.length > 0 && (
                <div className="space-y-1">
                  {children.map((child) => (
                    <FormTreeItem
                      key={child.slug}
                      nested
                      label={child.label}
                      fallback={child.fallback}
                      checked={selected.includes(child.slug)}
                      extra={
                        child.fallback ? <UzFallbackBadge locale={locale} /> : null
                      }
                      onChange={() => onToggle(child.slug)}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}
        {visibleRoots.length === 0 && (
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
  fallback = false,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  /** Kontent nomi o'zbekchadan olingan bo'lsa `true` (mavzu chiplari).
   *  Daraja/holat/til chiplari interfeys satri — ular hech qachon
   *  qaytish emas, ya'ni standart `false`. */
  fallback?: boolean;
}) {
  const locale = useLocale();
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
      {fallback && <UzFallbackBadge locale={locale} />}
    </button>
  );
}
