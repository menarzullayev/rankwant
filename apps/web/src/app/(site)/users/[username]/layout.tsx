import type { Metadata, Route } from "next";
import { notFound, redirect } from "next/navigation";

import { ProfileCard } from "@/features/profile";
import { ProfileNav } from "@/features/profile";
import { StatCard } from "@/components/ui/Card";
import { fill, t, type Locale } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { ApiError, type RatingKind, type UserPublic } from "@/lib/api";
import { loadProfile, loadUser } from "@/lib/profile.server";

type Props = {
  children: React.ReactNode;
  params: Promise<{ username: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  // Mavjud bo'lmagan nom sarlavhaga qo'yilmaydi — 404 sahifasi begona
  // satrni ko'rsatib turmasin.
  try {
    const user = await loadUser(decodeURIComponent((await params).username));
    return { title: { default: user.display_name || user.username, template: "%s · RankWant" } };
  } catch {
    return { title: "404" };
  }
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

/** `xl` gacha bir ustun (karta tepada), 1280 dan ikki ustun: chapda profil
 * kartasi, o'ngda raqamlar va tablar. */
export default async function ProfileLayout({ children, params }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();

  let user: UserPublic;
  try {
    user = await loadUser(username);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  // Eski taxallus: API yangi egasini qaytaradi — manzil ham yangisiga
  // o'tadi, ya'ni eski havolalar va standings'dagi nomlar ishlab turadi.
  if (user.username !== username) redirect(`/users/${user.username}` as Route);
  const profile = await loadProfile(user.username);

  return (
    <div className="grid gap-6 xl:grid-cols-[300px_minmax(0,1fr)]">
      <aside className="xl:sticky xl:top-20 xl:self-start">
        <ProfileCard profile={profile} locale={locale} />
      </aside>
      <div className="min-w-0 space-y-6">
        {/* 2026-09-19 HITL qarori: panel endi faqat `xl` dan qaytadi, shuning
            uchun KPI to'ri `lg` dan 4 ustun — bu bosh sahifa (#96) geometriyasi
            bilan bir xil: 1024 px da kontent 701 px, karta ~163 px, ichki
            ~121 px, 8 xonali raqam 24 px da sig'adi. 1280 da ikki ustun
            qaytgach kontent 633 px, ichki 104 px — 6 xonali sanoq aynan
            sig'adi, shuning uchun raqam `2xl` gacha 24 px qoladi. Panelni
            `lg` da saqlash (kontent 377 px) majburan 4 ustun raqamlarni
            27 px ga qirqardi — o'lchangan (2026-09-18). */}
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Skills"
            value={user.rating_skills}
            hint={ratingHint(user, "skills", locale)}
            about={t(locale, "profile.hintSkills")}
            valueClassName="lg:text-2xl 2xl:text-title-sm"
          />
          <StatCard
            label="Contests"
            value={user.rating_contest}
            hint={ratingHint(user, "contest", locale)}
            about={t(locale, "profile.hintContests")}
            valueClassName="lg:text-2xl 2xl:text-title-sm"
          />
          <StatCard
            label={t(locale, "leaderboard.activity")}
            value={user.rating_activity}
            hint={ratingHint(user, "activity", locale)}
            about={t(locale, "profile.hintActivity")}
            valueClassName="lg:text-2xl 2xl:text-title-sm"
          />
          <StatCard
            label={t(locale, "leaderboard.streak")}
            value={user.streak_count}
            about={t(locale, "profile.hintStreak")}
            valueClassName="lg:text-2xl 2xl:text-title-sm"
          />
        </section>
        <ProfileNav username={user.username} />
        {children}
      </div>
    </div>
  );
}
