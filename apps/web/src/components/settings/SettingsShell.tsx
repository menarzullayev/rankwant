"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AccountSettings } from "@/components/AccountSettings";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { AppearanceSection } from "./AppearanceSection";
import { CareerSection } from "./CareerSection";
import { InfoSection } from "./InfoSection";
import { Loading } from "./kit";
import { NotificationsSection } from "./NotificationsSection";
import { ProfileSection } from "./ProfileSection";
import { SECTIONS, type SectionId } from "./sections";
import { SecuritySection } from "./SecuritySection";
import { SkillsSection } from "./SkillsSection";
import { SocialSection } from "./SocialSection";
import { TeamsSection } from "./TeamsSection";

const VIEWS: Record<SectionId, () => React.ReactNode> = {
  profil: ProfileSection,
  xavfsizlik: SecuritySection,
  malumotlar: InfoSection,
  ijtimoiy: SocialSection,
  konikmalar: SkillsSection,
  karyera: CareerSection,
  jamoalar: TeamsSection,
  bildirishnomalar: NotificationsSection,
  korinish: AppearanceSection,
  hisob: AccountSettings,
};

/** Chapda bo'limlar ro'yxati (KEP kabi), tor ekranda esa uning o'rnida
 *  tanlash maydoni — o'nta havola telefonda butun ekranni egallardi. */
export function SettingsShell({ section }: { section: SectionId }) {
  const locale = useLocale();
  const router = useRouter();
  const { user } = useSession();
  const View = VIEWS[section];

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-title-sm font-bold rw-strong">
        {t(locale, "settings.title")}
      </h1>
      <div className="mt-6 grid gap-6 lg:grid-cols-[220px_minmax(0,1fr)]">
        <nav aria-label={t(locale, "settings.title")}>
          <label className="block lg:hidden">
            <span className="sr-only">{t(locale, "settings.section")}</span>
            <select
              value={section}
              onChange={(event) =>
                router.push(`/settings/${event.target.value}` as Route)
              }
              className="h-11 w-full rw-radius-sm border rw-line px-3 text-theme-sm rw-strong rw-field-bg rw-focus-ring"
            >
              {SECTIONS.map((s) => (
                <option key={s.id} value={s.id}>
                  {t(locale, s.key)}
                </option>
              ))}
            </select>
          </label>
          <ul className="sticky top-20 hidden flex-col gap-1 lg:flex">
            {SECTIONS.map((s) => (
              <li key={s.id}>
                <Link
                  href={`/settings/${s.id}` as Route}
                  aria-current={s.id === section ? "page" : undefined}
                  className={`menu-item ${
                    s.id === section ? "menu-item-active" : "menu-item-inactive"
                  }`}
                >
                  {t(locale, s.key)}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div className="min-w-0 space-y-6">{user ? <View /> : <Loading />}</div>
      </div>
    </div>
  );
}
