"use client";

import type { Route } from "next";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

const LEVELS = [
  ["beginner", "Boshlang'ich"],
  ["intermediate", "O'rta"],
  ["hard", "Qiyin"],
  ["expert", "Ekspert"],
  ["master", "Master"],
] as const;

const ORDERINGS = [
  ["difficulty", "Oson → qiyin"],
  ["-difficulty", "Qiyin → oson"],
  ["-solved_count", "Ko'p yechilgan"],
  ["-created_at", "Yangi qo'shilgan"],
] as const;

const field =
  "h-9 rw-radius-sm border rw-line rw-field-bg px-2.5 text-theme-sm rw-strong rw-focus-line";

/** Filtrlar URL da yashaydi — sahifa SSR bo'lib qoladi, holat ulashsa
 * bo'ladigan havolaga aylanadi va orqaga tugmasi kutilganday ishlaydi. */
export function ProblemFilters({
  topics,
  signedIn,
}: {
  topics: { slug: string; label: string }[];
  signedIn: boolean;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  function set(name: string, value: string) {
    const next = new URLSearchParams(params);
    if (value) next.set(name, value);
    else next.delete(name);
    router.push(`${pathname}${next.size ? `?${next}` : ""}` as Route);
  }

  const active = ["level", "topics", "solved", "ordering"].some((name) =>
    params.get(name),
  );

  return (
    <div className="flex flex-wrap items-center gap-2">
      <select
        aria-label="Daraja"
        value={params.get("level") ?? ""}
        onChange={(e) => set("level", e.target.value)}
        className={field}
      >
        <option value="">Har qanday daraja</option>
        {LEVELS.map(([code, label]) => (
          <option key={code} value={code}>
            {label}
          </option>
        ))}
      </select>

      <select
        aria-label="Mavzu"
        value={params.get("topics") ?? ""}
        onChange={(e) => set("topics", e.target.value)}
        className={field}
      >
        <option value="">Har qanday mavzu</option>
        {topics.map((topic) => (
          <option key={topic.slug} value={topic.slug}>
            {topic.label}
          </option>
        ))}
      </select>

      {signedIn && (
        <select
          aria-label="Holat"
          value={params.get("solved") ?? ""}
          onChange={(e) => set("solved", e.target.value)}
          className={field}
        >
          <option value="">Hammasi</option>
          <option value="false">Yechilmagan</option>
          <option value="true">Yechilgan</option>
        </select>
      )}

      <select
        aria-label="Tartib"
        value={params.get("ordering") ?? "difficulty"}
        onChange={(e) => set("ordering", e.target.value)}
        className={field}
      >
        {ORDERINGS.map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>

      {active && (
        <button
          type="button"
          onClick={() => router.push(pathname as Route)}
          className="rw-radius-sm px-2.5 py-1 text-theme-sm rw-dim transition rw-hover-bg"
        >
          Tozalash
        </button>
      )}
    </div>
  );
}
