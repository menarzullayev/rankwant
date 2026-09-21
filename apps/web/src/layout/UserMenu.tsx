"use client";

import type { Route } from "next";
import { useEffect, useRef, useState } from "react";

import { IntentLink } from "@/components/ui/IntentLink";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import { postJson } from "@/lib/api";

export default function UserMenu() {
  const locale = useLocale();
  const { user, ready, clear } = useSession();
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);

  async function logout() {
    setOpen(false);
    await postJson("/auth/logout/", {}).catch(() => {});
    clear();
  }

  useEffect(() => {
    if (!open) return;
    const onDown = (event: PointerEvent) => {
      if (!box.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      // Customizer ham Escape ni tinglaydi — menyu yopilishi panelni
      // yopmasin (AppTopNav dagi sabab bilan bir xil).
      event.stopPropagation();
      setOpen(false);
    };
    document.addEventListener("pointerdown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // Aniqlanmaguncha joy band qilib turamiz — "Kirish" chaqnab keyin
  // foydalanuvchi nomiga almashishi chalg'itadi.
  if (!ready) return <div className="h-10 w-24" />;

  if (!user) {
    // `whitespace-nowrap` SHART — usiz yorliq ikki qatorga bo'linardi.
    // O'lchandi (375px, `en`): 88x40px va **2 qator**; `nowrap` bilan
    // 100x40px va 1 qator. Sabab: header tor ekranda siqiladi va flex
    // element kontentidan pastga tushadi, matn esa o'raladi. Eng uzun
    // tarjima `tg` — «Ворид шудан» (11 belgi), ya'ni bir qatorli
    // yorliq uzunligi tilga bog'liq, shuning uchun o'rashni taqiqlash
    // yagona barqaror yechim.
    return (
      <IntentLink
        href={"/login?tab=login" as Route}
        className="flex h-10 items-center gap-2 whitespace-nowrap rw-radius-sm rw-accent-bg px-4 text-theme-sm font-medium text-white transition"
      >
        <Icon name="user.profile" className="size-4" />
        {t(locale, "auth.login")}
      </IntentLink>
    );
  }

  // H4: profil / sozlama / chiqish (va admin) bitta menyu — uchtasi
  // yonma-yon turib 390px ni yeb qo'masin.
  const name = user.display_name || user.username;
  const item =
    "flex w-full items-center gap-2 px-3 py-2 text-start text-theme-sm rw-strong transition rw-hover-bg";

  return (
    <div ref={box} className="relative">
      <button
        type="button"
        onClick={() => setOpen((was) => !was)}
        aria-expanded={open}
        aria-controls="rw-account-menu"
        aria-haspopup="true"
        aria-label={name}
        data-tip={open ? undefined : name}
        data-tip-kind="flip"
        className="flex h-10 items-center gap-2 rw-radius-sm border rw-line px-3 text-theme-sm font-medium rw-strong transition rw-hover-bg"
      >
        <Icon name="user.profile" className="size-4 shrink-0" />
        <span className="hidden max-w-[8rem] truncate sm:inline">{name}</span>
        <Icon
          name="nav.expandDown"
          className={`size-4 shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>
      {open && (
        <ul
          id="rw-account-menu"
          role="menu"
          className="absolute end-0 top-full z-50 mt-1 min-w-[12rem] overflow-hidden border p-1 rw-radius rw-surface rw-shadow rw-line"
        >
          <li role="none">
            <IntentLink
              href={`/users/${user.username}`}
              role="menuitem"
              onClick={() => setOpen(false)}
              className={item}
            >
              <Icon name="user.profile" className="size-4 shrink-0" />
              {t(locale, "settings.nav.profile")}
            </IntentLink>
          </li>
          <li role="none">
            <IntentLink
              href={"/settings/profil" as Route}
              role="menuitem"
              onClick={() => setOpen(false)}
              className={item}
            >
              <Icon name="system.settings" className="size-4 shrink-0" />
              {t(locale, "settings.title")}
            </IntentLink>
          </li>
          {user.is_staff && (
            <li role="none">
              <IntentLink
                href="/admin"
                role="menuitem"
                onClick={() => setOpen(false)}
                className={item}
              >
                {t(locale, "admin.title.page")}
              </IntentLink>
            </li>
          )}
          <li role="none">
            <button type="button" role="menuitem" onClick={logout} className={item}>
              <Icon name="user.logout" className="size-4 shrink-0" />
              {t(locale, "auth.logout")}
            </button>
          </li>
        </ul>
      )}
    </div>
  );
}
