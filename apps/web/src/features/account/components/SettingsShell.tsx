"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AccountSettings } from "@/features/account";
import { Dropdown } from "@/components/ui/Dropdown";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { AppearanceSection } from "./AppearanceSection";
import { CareerSection } from "./CareerSection";
import { InfoSection } from "./InfoSection";
import { Loading } from "./section-kit";
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
          <div className="mb-3 hidden lg:block">
            <div className="rw-kit-tabs" data-kit-tabs="crumb">
              <span className="rw-kit-tab" aria-current={undefined}>
                {t(locale, "settings.title")}
              </span>
              <span className="rw-kit-tab" aria-current="page">
                {t(locale, SECTIONS.find((s) => s.id === section)?.key ?? "settings.nav.profile")}
              </span>
            </div>
          </div>
          <div className="lg:hidden">
            <Dropdown
              hideLabel
              label={t(locale, "settings.section")}
              value={section}
              onChange={(next) => router.push(`/settings/${next}` as Route)}
              options={SECTIONS.map((s) => ({
                value: s.id,
                label: t(locale, s.key),
              }))}
            />
          </div>
          <ul className="rw-kit-tabs sticky top-20 hidden flex-col gap-1 lg:flex" data-kit-tabs="vertical">
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
