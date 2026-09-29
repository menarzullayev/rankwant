"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { Route } from "next";

import { useSession } from "@/context/SessionContext";
import { useCan } from "@/components/kit/Can";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { useOverlay } from "@/components/overlay/OverlayHost";

type Cmd = { id: string; label: string; run: () => void };

export function CommandPalette() {
  const locale = useLocale();
  const router = useRouter();
  const overlay = useOverlay();
  const { user } = useSession();
  const canStaff = useCan("staff");
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [sel, setSel] = useState(0);

  // H2: Ctrl+K qidiruvniki (`SearchBox`). Bu panel mahsulot shellida
  // mount qilinmaydi; ochilish eshigi yo'q. Escape — agar kit sinovida
  // ochiq qolsa yopish uchun.
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const cmds = useMemo<Cmd[]>(() => {
    const go = (path: Route) => () => {
      setOpen(false);
      router.push(path);
    };
    const items: Cmd[] = [
      {
        id: "problems",
        label: t(locale, "nav.problems"),
        run: go("/problems"),
      },
      {
        id: "contests",
        label: t(locale, "nav.contests"),
        run: go("/contests"),
      },
      {
        id: "settings",
        label: t(locale, "settings.title"),
        run: go("/settings/profil" as Route),
      },
      {
        id: "copy",
        label: t(locale, "kit.paletteCopyUrl"),
        run: () => {
          setOpen(false);
          void navigator.clipboard
            .writeText(window.location.href)
            .then(() => overlay.toast(t(locale, "problem.copied")))
            .catch(() => overlay.toast(t(locale, "problem.copyFailed")));
        },
      },
    ];
    if (canStaff) {
      items.push({
        id: "admin",
        label: t(locale, "admin.title"),
        run: go("/admin"),
      });
    }
    return items;
  }, [locale, overlay, router, canStaff]);

  const needle = q.trim().toLocaleLowerCase();
  const shown = cmds.filter((c) =>
    needle ? c.label.toLocaleLowerCase().includes(needle) : true,
  );
  const current = shown[Math.min(sel, Math.max(0, shown.length - 1))];

  if (!open) return null;

  return (
    <div
      className="rw-ov-scrim"
      style={{ pointerEvents: "auto" }}
      onClick={() => setOpen(false)}
    >
      <div
        className="rw-ov-panel"
        data-kit-confirm="cmdk"
        role="dialog"
        aria-modal="true"
        aria-label={t(locale, "kit.palette")}
        // `onClick` — faqat hodisani to'xtatish (parda yopilmasin).
        // `role="presentation"` shart emas: `role="dialog"` allaqachon
        // to'g'ri, `aria-modal` esa fokusni dialog ichida ushlab
        // turishini e'lon qiladi.
        onClick={(event) => event.stopPropagation()}
      >
        <input
          autoFocus
          className="rw-kit-cmdk-in"
          value={q}
          placeholder={t(locale, "kit.cmdkPlaceholder")}
          onChange={(event) => {
            setQ(event.target.value);
            setSel(0);
          }}
          onKeyDown={(event) => {
            if (event.key === "ArrowDown") {
              event.preventDefault();
              setSel((i) => Math.min(shown.length - 1, i + 1));
            } else if (event.key === "ArrowUp") {
              event.preventDefault();
              setSel((i) => Math.max(0, i - 1));
            } else if (event.key === "Enter" && current) {
              event.preventDefault();
              current.run();
            }
          }}
        />
        <div className="rw-kit-cmdk-list" role="listbox">
          {shown.length === 0 ? (
            <p className="px-2 py-2 text-theme-sm rw-faint">
              {t(locale, "kit.paletteEmpty")}
            </p>
          ) : (
            shown.map((c, i) => (
              <button
                key={c.id}
                type="button"
                role="option"
                aria-selected={c === current}
                onMouseEnter={() => setSel(i)}
                onClick={c.run}
              >
                {c.label}
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
