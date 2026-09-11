import type { Route } from "next";
import Link from "next/link";

import { Avatar } from "@/components/Avatar";
import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { fill, t, type Locale } from "@/i18n/messages";
import type { PublicProfile } from "@/lib/api";
import { badgeLabel, coverClass, frameClass } from "@/lib/cosmetics";
import { countryName } from "@/lib/countries";
import { formatDate } from "@/lib/format";
import { regionName } from "@/lib/regions";
import { FollowButton } from "./FollowButton";
import { ShareButton } from "./ShareButton";

/** Chap ustun: kim bu odam — rasm, ism, joy, maktab, havolalar. */
export function ProfileCard({
  profile,
  locale,
}: {
  profile: PublicProfile;
  locale: Locale;
}) {
  const name = profile.display_name || profile.username;
  const badge = badgeLabel(profile.cosmetics.badge);
  const base = `/users/${profile.username}`;
  const { info } = profile;
  const region =
    info.region && (info.country === "UZ" ? regionName(info.region, locale) : info.region);
  const place = info.country
    ? [countryName(info.country, locale), region].filter(Boolean).join(", ")
    : "";
  const rows: [string, React.ReactNode][] = [];
  if (place) rows.push([t(locale, "settings.country"), place]);
  if (info.school) rows.push([t(locale, "settings.school"), info.school]);
  if (info.grade) rows.push([t(locale, "settings.grade"), info.grade]);
  if (info.website)
    rows.push([
      t(locale, "settings.website"),
      <a
        key="site"
        href={info.website}
        target="_blank"
        rel="nofollow ugc noopener noreferrer"
        className="break-all rw-accent-ink hover:underline"
      >
        {info.website.replace(/^https?:\/\//, "").replace(/\/$/, "")}
      </a>,
    ]);

  return (
    <section className="overflow-hidden rw-panel">
      <div aria-hidden="true" className={`h-20 ${coverClass(profile.cosmetics.cover)}`} />
      <div className="px-5 pb-5">
        <Avatar
          url={profile.avatar_url}
          name={name}
          className={`-mt-12 size-24 border-4 border-[var(--rw-surface)] text-title-sm ${frameClass(profile.cosmetics.frame)}`}
        />
        <h1 className="mt-3 flex flex-wrap items-center gap-2 text-theme-xl font-bold rw-strong">
          <span className="min-w-0 break-words">{name}</span>
          {badge && <Badge color="brand">{badge}</Badge>}
        </h1>
        <p className="text-theme-sm rw-dim">@{profile.username}</p>
        {profile.bio && <p className="mt-3 text-theme-sm rw-dim-2">{profile.bio}</p>}

        <div className="mt-4 flex flex-wrap gap-2">
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
          <ShareButton username={profile.username} name={name} />
        </div>

        <p className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-theme-sm">
          <Link href={`${base}/obunachilar` as Route} className="rw-link-hover">
            <strong className="tabular-nums rw-strong">{profile.followers}</strong>{" "}
            <span className="rw-dim">{t(locale, "profile.followers")}</span>
          </Link>
          <Link href={`${base}/obunalar` as Route} className="rw-link-hover">
            <strong className="tabular-nums rw-strong">{profile.following}</strong>{" "}
            <span className="rw-dim">{t(locale, "profile.followingTab")}</span>
          </Link>
        </p>

        <dl className="mt-4 space-y-2.5 border-t rw-line pt-4 text-theme-sm">
          {rows.map(([label, value]) => (
            <div key={label}>
              <dt className="text-theme-xs rw-faint">{label}</dt>
              <dd className="rw-strong">{value}</dd>
            </div>
          ))}
          <div>
            <dt className="sr-only">{t(locale, "profile.memberSince")}</dt>
            <dd className="text-theme-xs rw-dim">
              {fill(t(locale, "profile.joined"), {
                date: formatDate(profile.date_joined, locale, {
                  year: "numeric",
                  month: "long",
                }),
              })}
            </dd>
          </div>
        </dl>
      </div>
    </section>
  );
}
