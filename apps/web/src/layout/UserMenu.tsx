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
        className="flex h-10 items-center gap-2 rounded-lg bg-brand-500 px-4 text-theme-sm
          font-medium text-white transition hover:bg-brand-600"
      >
        <UserIcon className="size-4" />
        {t(locale, "auth.login")}
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Link
        href={`/users/${user.username}`}
        className="flex h-10 items-center gap-2 rounded-lg border border-gray-200 px-3
          text-theme-sm font-medium text-gray-700 transition hover:bg-gray-50
          dark:border-[#232936] dark:text-gray-200 dark:hover:bg-white/5"
      >
        <UserIcon className="size-4" />
        <span className="hidden sm:inline">{user.display_name || user.username}</span>
      </Link>
      <button
        type="button"
        onClick={logout}
        className="h-10 rounded-lg px-3 text-theme-sm text-gray-500 transition
          hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
      >
        {t(locale, "auth.logout")}
      </button>
    </div>
  );
}
