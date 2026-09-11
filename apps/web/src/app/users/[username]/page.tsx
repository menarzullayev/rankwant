import type { Metadata, Route } from "next";
import { notFound, redirect } from "next/navigation";

import { AboutTab } from "@/components/profile/AboutTab";
import {
  AchievementsTab,
  ActivityTab,
  PeopleTab,
  PurchasesTab,
} from "@/components/profile/ActivityTabs";
import { ProfileHeader } from "@/components/profile/ProfileHeader";
import { ProfileTabs, isTab, type Tab } from "@/components/profile/ProfileTabs";
import { RatingTab } from "@/components/profile/RatingTab";
import { StatCard } from "@/components/ui/Card";
import { fill, t, type Locale } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import {
  api,
  ApiError,
  type PublicProfile,
  type RatingKind,
  type UserPublic,
} from "@/lib/api";
import { getWithSession } from "@/lib/api.server";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<{ tab?: string; before?: string; page?: string }>;
};

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { username } = await params;
  // Mavjud bo'lmagan foydalanuvchi nomini sarlavhaga qo'ymaymiz —
  // 404 sahifasi begona satrni ko'rsatib turmasin. `api.user` fetch'i
  // sahifa render'i bilan bir xil, ya'ni ikkinchi so'rov ketmaydi.
  try {
    const user = await api.user(decodeURIComponent(username));
    return { title: user.display_name || user.username };
  } catch {
    return { title: "404" };
  }
}

export default async function ProfilePage({ params, searchParams }: Props) {
  const username = decodeURIComponent((await params).username);
  const query = await searchParams;
  const locale = await getLocale();

  let user: UserPublic;
  try {
    user = await api.user(username);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  // Eski taxallus: API yangi egasini qaytaradi — manzil ham yangisiga
  // o'tadi, ya'ni eski havolalar va standings'dagi nomlar ishlab turadi.
  if (user.username !== username) redirect(`/users/${user.username}` as Route);

  // Sessiya bilan: egasi yashirgan maydonlarini ham, «kuzatyapman» holatini ham ko'radi.
  const profile = await getWithSession<PublicProfile>(`/users/${user.username}/profile/`);
  const tab: Tab = isTab(query.tab) ? query.tab : "about";

  return (
    <div className="space-y-6">
      <ProfileHeader profile={profile} locale={locale} />

      {/* Reyting yonida O'RIN: raqamning o'zi «ko'p yoki oz» ekanini
          aytmaydi, u faqat boshqalar bilan solishtirganda ma'lum bo'ladi
          (KEP profilida ham shunday). Eng yuqori qiymat esa hozirgisi
          tushib ketgan bo'lsa ham mehnat yo'qolmaganini ko'rsatadi. */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Skills" value={user.rating_skills} hint={ratingHint(user, "skills", locale)} />
        <StatCard label="Contests" value={user.rating_contest} hint={ratingHint(user, "contest", locale)} />
        <StatCard
          label={t(locale, "leaderboard.activity")}
          value={user.rating_activity}
          hint={ratingHint(user, "activity", locale)}
        />
        <StatCard label={t(locale, "leaderboard.streak")} value={user.streak_count} />
      </section>

      <ProfileTabs username={user.username} active={tab} locale={locale} />

      {tab === "about" && <AboutTab profile={profile} locale={locale} />}
      {tab === "rating" && <RatingTab user={user} locale={locale} />}
      {tab === "activity" && (
        <ActivityTab username={user.username} before={query.before} locale={locale} />
      )}
      {tab === "achievements" && <AchievementsTab username={user.username} locale={locale} />}
      {tab === "purchases" && <PurchasesTab username={user.username} locale={locale} />}
      {(tab === "followers" || tab === "following") && (
        <PeopleTab
          username={user.username}
          direction={tab}
          page={Math.max(1, Number(query.page) || 1)}
          locale={locale}
        />
      )}
    </div>
  );
}

/** «#7 · eng yuqori 1500» — o'rin va erishilgan cho'qqi. */
function ratingHint(user: UserPublic, kind: RatingKind, locale: Locale): string | undefined {
  const parts: string[] = [];
  const rank = user.ranks[kind];
  const max = user.max_ratings[kind];
  if (rank) parts.push(`#${rank}`);
  if (max !== undefined && max > 0) parts.push(fill(t(locale, "profile.highest"), { max }));
  return parts.length ? parts.join(" · ") : undefined;
}
