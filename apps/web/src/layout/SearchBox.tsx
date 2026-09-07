"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { SearchIcon } from "@/icons";
import { API_BASE, type SearchResult } from "@/lib/api";

const EMPTY: SearchResult = { q: "", problems: [], users: [], articles: [], contests: [] };

export default function SearchBox() {
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
      if (box.current && !box.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const shown = active ? result : EMPTY;
  const total =
    shown.problems.length + shown.users.length + shown.articles.length + shown.contests.length;

  return (
    <div ref={box} className="relative hidden md:block">
      <label className="relative block">
        <SearchIcon className="pointer-events-none absolute top-2.5 left-3 size-5 text-gray-400" />
        <input
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder={t(DEFAULT_LOCALE, "header.search")}
          className="h-10 w-64 rounded-lg border border-gray-200 bg-transparent pr-3 pl-10
            text-theme-sm outline-none focus:border-brand-400 focus:shadow-focus-ring
            dark:border-[#232936] dark:text-white/90 xl:w-80"
        />
      </label>
      {open && total > 0 && (
        <div
          className="absolute top-12 left-0 z-40 w-full overflow-hidden rounded-xl border
            border-gray-200 bg-white shadow-theme-lg dark:border-[#232936] dark:bg-[#141821]"
        >
          {shown.problems.map((p) => (
            <Link key={`p-${p.slug}`} href={`/problems/${p.slug}`} onClick={() => setOpen(false)}
              className="flex items-center justify-between px-4 py-2 text-theme-sm hover:bg-gray-50 dark:hover:bg-white/5">
              <span>{p.title}</span>
              <span className="text-theme-xs text-gray-400">{p.difficulty}</span>
            </Link>
          ))}
          {shown.users.map((u) => (
            <Link key={`u-${u.username}`} href={`/users/${u.username}`} onClick={() => setOpen(false)}
              className="flex items-center justify-between px-4 py-2 text-theme-sm hover:bg-gray-50 dark:hover:bg-white/5">
              <span>@{u.username}</span>
              <span className="text-theme-xs text-gray-400">{u.rating_skills}</span>
            </Link>
          ))}
          {shown.articles.map((a) => (
            <Link key={`a-${a.slug}`} href={`/learn/${a.slug}`} onClick={() => setOpen(false)}
              className="block px-4 py-2 text-theme-sm hover:bg-gray-50 dark:hover:bg-white/5">
              {a.title}
            </Link>
          ))}
          {shown.contests.map((c) => (
            <Link key={`c-${c.slug}`} href={`/contests/${c.slug}`} onClick={() => setOpen(false)}
              className="block px-4 py-2 text-theme-sm hover:bg-gray-50 dark:hover:bg-white/5">
              {c.title}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
