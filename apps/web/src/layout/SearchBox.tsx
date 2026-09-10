"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { t } from "@/i18n/messages";
import { useLocale } from "@/i18n/LocaleProvider";
import { SearchIcon } from "@/icons";
import { API_BASE, type SearchResult } from "@/lib/api";

const EMPTY: SearchResult = {
  q: "",
  problems: [],
  users: [],
  articles: [],
  contests: [],
};

export default function SearchBox() {
  const locale = useLocale();
  const [q, setQ] = useState("");
  const [result, setResult] = useState<SearchResult>(EMPTY);
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);

  // Har tugmada emas, 250 ms tinganda so'raymiz — server va ko'z uchun ham.
  const active = q.trim().length >= 2;

  useEffect(() => {
    if (!active) return;
    const handle = setTimeout(() => {
      fetch(`${API_BASE}/search/?q=${encodeURIComponent(q.trim())}`)
        .then((r) => (r.ok ? r.json() : EMPTY))
        .then((data: SearchResult) => setResult(data))
        .catch(() => setResult(EMPTY));
    }, 250);
    return () => clearTimeout(handle);
  }, [q, active]);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (box.current && !box.current.contains(e.target as Node))
        setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const shown = active ? result : EMPTY;
  const total =
    shown.problems.length +
    shown.users.length +
    shown.articles.length +
    shown.contests.length;

  return (
    <div ref={box} className="relative hidden min-w-0 shrink md:block">
      <label className="relative block">
        {/* Yorliqda MATN bo'lishi shart: ikonka va placeholder skrinriderga
            nom bermaydi, placeholder esa yozish boshlangach yo'qoladi. */}
        <span className="sr-only">{t(locale, "header.search")}</span>
        <SearchIcon className="pointer-events-none absolute top-2.5 left-3 size-5 rw-faint" />
        <input
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder={t(locale, "header.search")}
          className="h-10 w-64 rw-radius-sm border rw-line bg-transparent pr-3 pl-10 text-theme-sm outline-none rw-focus-line rw-focus-ring xl:w-80"
        />
      </label>
      {open && total > 0 && (
        <div className="absolute top-12 left-0 z-40 w-full overflow-hidden rw-radius border rw-line rw-surface rw-shadow">
          {shown.problems.map((p) => (
            <Link
              key={`p-${p.slug}`}
              href={`/problems/${p.slug}`}
              onClick={() => setOpen(false)}
              className="flex items-center justify-between px-4 py-2 text-theme-sm rw-hover-bg"
            >
              <span>{p.title}</span>
              <span className="text-theme-xs rw-faint">{p.difficulty}</span>
            </Link>
          ))}
          {shown.users.map((u) => (
            <Link
              key={`u-${u.username}`}
              href={`/users/${u.username}`}
              onClick={() => setOpen(false)}
              className="flex items-center justify-between px-4 py-2 text-theme-sm rw-hover-bg"
            >
              <span>@{u.username}</span>
              <span className="text-theme-xs rw-faint">{u.rating_skills}</span>
            </Link>
          ))}
          {shown.articles.map((a) => (
            <Link
              key={`a-${a.slug}`}
              href={`/learn/${a.slug}`}
              onClick={() => setOpen(false)}
              className="block px-4 py-2 text-theme-sm rw-hover-bg"
            >
              {a.title}
            </Link>
          ))}
          {shown.contests.map((c) => (
            <Link
              key={`c-${c.slug}`}
              href={`/contests/${c.slug}`}
              onClick={() => setOpen(false)}
              className="block px-4 py-2 text-theme-sm rw-hover-bg"
            >
              {c.title}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
