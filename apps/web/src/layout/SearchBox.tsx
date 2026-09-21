"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { t } from "@/i18n/messages";
import { useLocale } from "@/i18n/LocaleProvider";
import { Icon } from "@/components/ui/Icon";
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
  const [focused, setFocused] = useState(false);
  // H3: tor ekranda maydon yashirin — lupa ochadi. `md+` da maydon
  // doim ko'rinadi, `expanded` faqat panel holatini bildiradi.
  const [expanded, setExpanded] = useState(false);
  const box = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLInputElement>(null);

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
      if (box.current && !box.current.contains(e.target as Node)) {
        setOpen(false);
        setExpanded(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  // `Ctrl+K` / `Cmd+K` — qidiruvga sakrash (D61 ⑦, H2 yagona egasi).
  // H3: tor ekranda avval panel ochiladi, keyin fokus — aks holda
  // `display:none` maydon fokus olmaydi.
  //
  // ⚠️ `preventDefault()` SHART: usiz brauzer o'z manzil qatoridagi
  // qidiruvni ochadi va bizning maydon fokus olmay qoladi.
  // Faqat oddiy tugmalar: `Ctrl+Shift+K` kabi birikmalar tegmaydi.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() !== "k" || e.shiftKey || e.altKey) return;
      if (!(e.metaKey || e.ctrlKey)) return;
      e.preventDefault();
      setExpanded(true);
      requestAnimationFrame(() => {
        input.current?.focus();
        input.current?.select();
      });
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const shown = active ? result : EMPTY;
  const total =
    shown.problems.length +
    shown.users.length +
    shown.articles.length +
    shown.contests.length;

  // Yorliq ko'rinishi: qiymat bor bo'lsa tozalash, aks holda klaviatura
  // yorlig'i. Ikkalasi bir vaqtda turmaydi — o'ng tomon tor.
  const showClear = q.length > 0;
  const showKbd = !showClear && !focused;

  function closeHit() {
    setOpen(false);
    setExpanded(false);
  }

  function toggleExpanded() {
    setExpanded((was) => {
      const next = !was;
      if (next) {
        requestAnimationFrame(() => input.current?.focus());
      }
      return next;
    });
  }

  return (
    <div ref={box} className="relative min-w-0 md:w-36 md:shrink lg:w-52 xl:w-80">
      <button
        type="button"
        onClick={toggleExpanded}
        aria-expanded={expanded}
        aria-controls="rw-header-search"
        aria-label={t(locale, "header.search")}
        data-tip={t(locale, "header.search")}
        data-tip-kind="flip"
        className="flex size-10 shrink-0 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg md:hidden"
      >
        <Icon name="action.search" className="pointer-events-none" />
      </button>
      <div
        id="rw-header-search"
        className={`${
          expanded
            ? "fixed inset-x-3 top-16 z-40 rounded-lg border rw-line rw-surface rw-shadow p-2 md:static md:inset-auto md:z-auto md:rounded-none md:border-0 md:bg-transparent md:p-0 md:shadow-none"
            : "hidden"
        } md:block`}
      >
      <label className="relative block">
        {/* Yorliqda MATN bo'lishi shart: ikonka va placeholder skrinriderga
            nom bermaydi, placeholder esa yozish boshlangach yo'qoladi. */}
        <span className="sr-only">{t(locale, "header.search")}</span>
        <Icon name="action.search" className="pointer-events-none absolute top-2.5 left-3 size-5 rw-faint" />
        <input
          ref={input}
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setOpen(true);
          }}
          onFocus={() => {
            setOpen(true);
            setFocused(true);
          }}
          onBlur={() => setFocused(false)}
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              if (q) setQ("");
              else {
                setExpanded(false);
                e.currentTarget.blur();
              }
            }
          }}
          placeholder={t(locale, "header.search")}
          aria-keyshortcuts="Control+K Meta+K"
          className="rw-fm-inp is-search h-10 w-full max-w-full border rw-line bg-transparent pr-16 pl-10 text-theme-sm outline-none rw-focus-line rw-focus-ring"
        />
        {showKbd && (
          <kbd
            aria-hidden="true"
            className="pointer-events-none absolute top-2.5 right-3 hidden rw-radius-sm border rw-line px-1.5 py-0.5 text-theme-xs rw-faint lg:inline-block"
          >
            Ctrl K
          </kbd>
        )}
        {showClear && (
          <button
            type="button"
            onClick={() => {
              setQ("");
              setResult(EMPTY);
              input.current?.focus();
            }}
            // Yorliq kerak: ichida faqat ikonka, ya'ni nom bermaydi.
            aria-label={t(locale, "common.clear")}
            title={t(locale, "common.clear")}
            className="absolute top-2 right-2 flex size-6 items-center justify-center rw-radius-sm rw-faint rw-hover-bg rw-focus-ring"
          >
            <Icon name="nav.close" className="size-4" />
          </button>
        )}
      </label>
      {open && total > 0 && (
        <div className="absolute top-12 left-0 z-40 w-full overflow-hidden rw-radius border rw-line rw-surface rw-shadow">
          {shown.problems.map((p) => (
            <Link
              key={`p-${p.slug}`}
              href={`/problems/${p.slug}`}
              onClick={closeHit}
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
              onClick={closeHit}
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
              onClick={closeHit}
              className="block px-4 py-2 text-theme-sm rw-hover-bg"
            >
              {a.title}
            </Link>
          ))}
          {shown.contests.map((c) => (
            <Link
              key={`c-${c.slug}`}
              href={`/contests/${c.slug}`}
              onClick={closeHit}
              className="block px-4 py-2 text-theme-sm rw-hover-bg"
            >
              {c.title}
            </Link>
          ))}
        </div>
      )}
      </div>
    </div>
  );
}
