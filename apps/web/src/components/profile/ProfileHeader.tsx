import type { Route } from "next";
import Link from "next/link";

import { Avatar } from "@/components/Avatar";
import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { fill, t, type Locale } from "@/i18n/messages";
import type { PublicProfile } from "@/lib/api";
import { badgeLabel, coverClass, frameClass } from "@/lib/cosmetics";
import { FollowButton } from "./FollowButton";

export function ProfileHeader({
  profile,
  locale,
}: {
  profile: PublicProfile;
  locale: Locale;
}) {
  const name = profile.display_name || profile.username;
  const badge = badgeLabel(profile.cosmetics.badge);
  const base = `/users/${profile.username}`;
  const joined = new Date(profile.date_joined).toLocaleDateString(locale, {
    year: "numeric",
    month: "long",
  });

  return (
    <header className="overflow-hidden rw-panel">
      <div
        aria-hidden="true"
        className={`h-24 sm:h-32 ${coverClass(profile.cosmetics.cover)}`}
      />
      <div className="flex flex-wrap items-end gap-4 px-5 sm:px-6">
        <Avatar
          url={profile.avatar_url}
          name={name}
          className={`-mt-10 size-20 border-4 border-[var(--rw-surface)] text-title-sm ${frameClass(profile.cosmetics.frame)}`}
        />
        <div className="min-w-0 flex-1 pt-3">
          <h1 className="flex flex-wrap items-center gap-2 text-title-sm font-bold rw-strong">
            <span className="min-w-0 break-words">{name}</span>
            {badge && <Badge color="brand">{badge}</Badge>}
          </h1>
          <p className="text-theme-sm rw-dim">
            @{profile.username} · {fill(t(locale, "profile.joined"), { date: joined })}
          </p>
        </div>
        <div className="pt-3">
          {profile.is_owner ? (
            <ButtonLink href={"/settings/profil" as Route} variant="outline">
              {t(locale, "profile.edit")}
            </ButtonLink>
          ) : (
            <FollowButton
              username={profile.username}
              following={profile.is_following === true}
            />
          )}
        </div>
      </div>
      {profile.bio && (
        <p className="mt-3 max-w-3xl px-5 text-theme-sm rw-dim-2 sm:px-6">
          {profile.bio}
        </p>
      )}
      <div className="mt-4 flex flex-wrap gap-x-5 gap-y-1 border-t rw-line px-5 py-3 text-theme-sm sm:px-6">
        <Link href={`${base}?tab=followers` as Route} className="rw-link-hover">
          <strong className="tabular-nums rw-strong">{profile.followers}</strong>{" "}
          <span className="rw-dim">{t(locale, "profile.followers")}</span>
        </Link>
        <Link href={`${base}?tab=following` as Route} className="rw-link-hover">
          <strong className="tabular-nums rw-strong">{profile.following}</strong>{" "}
          <span className="rw-dim">{t(locale, "profile.followingTab")}</span>
        </Link>
      </div>
    </header>
  );
}
