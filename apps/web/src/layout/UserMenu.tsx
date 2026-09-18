"use client";

import type { Route } from "next";
import { IntentLink } from "@/components/ui/IntentLink";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
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

  return (
    <div className="flex items-center gap-2">
      {user.is_staff && (
        <IntentLink
          href="/admin"
          className="hidden h-10 items-center rw-radius-sm border rw-line px-3 text-theme-sm font-medium rw-accent-ink transition rw-hover-accent sm:flex"
        >
          {t(locale, "admin.title.page")}
        </IntentLink>
      )}
      <IntentLink
        href={`/users/${user.username}`}
        className="flex h-10 items-center gap-2 rw-radius-sm border rw-line px-3 text-theme-sm font-medium rw-strong transition rw-hover-bg"
      >
        <Icon name="user.profile" className="size-4" />
        <span className="hidden sm:inline">
          {user.display_name || user.username}
        </span>
      </IntentLink>
      <IntentLink
        href="/settings/profil"
        aria-label={t(locale, "settings.title")}
        title={t(locale, "settings.title")}
        className="flex size-10 items-center justify-center rw-radius-sm border rw-line rw-dim transition rw-hover-strong"
      >
        <Icon name="system.settings" className="size-4" />
      </IntentLink>
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
        <Icon name="user.logout" className="size-4 sm:hidden" />
        <span className="hidden sm:inline">{t(locale, "auth.logout")}</span>
      </button>
    </div>
  );
}
