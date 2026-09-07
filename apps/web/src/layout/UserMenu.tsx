"use client";

import Link from "next/link";

import { useSession } from "@/context/SessionContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { UserIcon } from "@/icons";
import { postJson } from "@/lib/api";

export default function UserMenu() {
  const locale = DEFAULT_LOCALE;
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
          className="flex h-10 items-center rw-radius-sm border rw-line px-3 text-theme-sm font-medium rw-accent-ink transition rw-hover-accent"
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
      <button
        type="button"
        onClick={logout}
        className="h-10 rw-radius-sm px-3 text-theme-sm rw-dim transition rw-hover-strong"
      >
        {t(locale, "auth.logout")}
      </button>
    </div>
  );
}
