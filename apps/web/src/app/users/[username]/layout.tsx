import type { Metadata, Route } from "next";
import { notFound, redirect } from "next/navigation";

import { ProfileCard } from "@/components/profile/ProfileCard";
import { ProfileNav } from "@/components/profile/ProfileNav";
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

/** Ikki ustun: chapda profil kartasi, o'ngda raqamlar va tablar. */
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
    <div className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
      <aside className="lg:sticky lg:top-20 lg:self-start">
        <ProfileCard profile={profile} locale={locale} />
      </aside>
      <div className="min-w-0 space-y-6">
        <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
          <StatCard
            label="Skills"
            value={user.rating_skills}
            hint={ratingHint(user, "skills", locale)}
            about={t(locale, "profile.hintSkills")}
          />
          <StatCard
            label="Contests"
            value={user.rating_contest}
            hint={ratingHint(user, "contest", locale)}
            about={t(locale, "profile.hintContests")}
          />
          <StatCard
            label={t(locale, "leaderboard.activity")}
            value={user.rating_activity}
            hint={ratingHint(user, "activity", locale)}
            about={t(locale, "profile.hintActivity")}
          />
          <StatCard
            label={t(locale, "leaderboard.streak")}
            value={user.streak_count}
            about={t(locale, "profile.hintStreak")}
          />
        </section>
        <ProfileNav username={user.username} />
        {children}
      </div>
    </div>
  );
}
