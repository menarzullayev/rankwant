"use client";

import Link from "next/link";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { LogoutIcon, SettingsIcon, UserIcon } from "@/icons";
import { postJson } from "@/lib/api";

export default function UserMenu() {
  const locale = useLocale();
  const { user, ready, clear } = useSession();

  async function logout() {
    await postJson("/auth/logout/", {}).catch(() => {});
    clear();
  }

  // Aniqlanmaguncha joy band qilib turamiz — "Kirish" chaqnab keyin
  // foydalanuvchi nomiga almashishi chalg'itadi.
  if (!ready) return <div className="h-10 w-24" />;

  if (!user) {
    return (
      <Link
        href="/login"
        className="flex h-10 items-center gap-2 rw-radius-sm rw-accent-bg px-4 text-theme-sm font-medium text-white transition"
      >
        <UserIcon className="size-4" />
        {t(locale, "auth.login")}
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {user.is_staff && (
        <Link
          href="/admin"
          className="hidden h-10 items-center rw-radius-sm border rw-line px-3 text-theme-sm font-medium rw-accent-ink transition rw-hover-accent sm:flex"
        >
          Admin
        </Link>
      )}
      <Link
        href={`/users/${user.username}`}
        className="flex h-10 items-center gap-2 rw-radius-sm border rw-line px-3 text-theme-sm font-medium rw-strong transition rw-hover-bg"
      >
        <UserIcon className="size-4" />
        <span className="hidden sm:inline">
          {user.display_name || user.username}
        </span>
      </Link>
      <Link
        href="/settings"
        aria-label={t(locale, "settings.title")}
        title={t(locale, "settings.title")}
        className="flex size-10 items-center justify-center rw-radius-sm border rw-line rw-dim transition rw-hover-strong"
      >
        <SettingsIcon className="size-4" />
      </Link>
      {/* Tor ekranda faqat ikonka: matnli tugma ~70px olardi va
          sarlavha 390px da sig'masdan siljib ketardi. Nomi `aria-label`
          da qoladi, ya'ni ekran o'quvchi uchun hech narsa yo'qolmaydi. */}
      <button
        type="button"
        onClick={logout}
        aria-label={t(locale, "auth.logout")}
        title={t(locale, "auth.logout")}
        className="flex size-10 items-center justify-center rw-radius-sm text-theme-sm rw-dim transition rw-hover-strong sm:size-auto sm:px-3"
      >
        <LogoutIcon className="size-4 sm:hidden" />
        <span className="hidden sm:inline">{t(locale, "auth.logout")}</span>
      </button>
    </div>
  );
}
