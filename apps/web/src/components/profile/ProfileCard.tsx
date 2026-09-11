import type { Route } from "next";
import Link from "next/link";

import { Avatar } from "@/components/Avatar";
import { UserName } from "@/components/UserName";
import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { fill, t, type Locale } from "@/i18n/messages";
import type { ProfileRole, PublicProfile } from "@/lib/api";
import { badgeLabel, coverClass, frameClass } from "@/lib/cosmetics";
import { countryName } from "@/lib/countries";
import { EXTERNAL_LABEL, externalShown, externalUrl } from "@/lib/external-links";
import { formatDate, formatRelative } from "@/lib/format";
import { districtName, regionName } from "@/lib/regions";
import { BrandIcon, EXTERNAL_ICONS } from "@/lib/tech-icons";
import { FollowButton } from "./FollowButton";
import { Medal, achievementLabel } from "./Medal";
import { ShareButton } from "./ShareButton";

const ROLE_COLOR: Record<ProfileRole["code"], BadgeColor> = {
  champion: "warning",
  staff: "brand",
  jury: "info",
  author: "success",
};

/** Chap ustun: kim bu odam — rasm, unvon, ism, rollar, joy, havolalar. */
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
  const rank = profile.title ? `rw-rank-${profile.title.level}` : "";
  const region =
    info.region && (info.country === "UZ" ? regionName(info.region, locale) : info.region);
  const locality = info.district ? districtName(info.district, locale) : info.city;
  const place = info.country
    ? [countryName(info.country, locale), region, locality].filter(Boolean).join(", ")
    : "";
  const rows: [string, React.ReactNode][] = [];
  if (place) rows.push([t(locale, "settings.country"), place]);
  if (info.school)
    rows.push([
      t(locale, "settings.school"),
      info.school_id ? (
        <Link
          key="school"
          href={`/leaderboard?school=${info.school_id}` as Route}
          title={t(locale, "profile.schoolRanking")}
          className="rw-accent-ink hover:underline"
        >
          {info.school}
        </Link>
      ) : (
        info.school
      ),
    ]);
  if (profile.coach.length > 0)
    rows.push([
      t(locale, "profile.coach"),
      <span key="coach" className="flex flex-wrap gap-x-2">
        {profile.coach.map((coach) => (
          <UserName
            key={coach.username}
            username={coach.username}
            name={coach.display_name}
            title={coach.title}
            locale={locale}
          />
        ))}
      </span>,
    ]);
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
          className={`-mt-12 size-24 border-4 border-[var(--rw-surface)] text-title-sm ${frameClass(profile.cosmetics.frame, profile.title)}`}
        />
        <h1 className="mt-3 flex flex-wrap items-center gap-2 text-theme-xl font-bold rw-strong">
          <span className={`min-w-0 break-words ${rank}`}>{name}</span>
          {badge && <Badge color="brand">{badge}</Badge>}
        </h1>
        <p className="text-theme-sm rw-dim">@{profile.username}</p>
        {(profile.title || profile.roles.length > 0) && (
          <div className="mt-3 flex flex-wrap items-center gap-1.5">
            {profile.title && (
              <span
                title={t(locale, "profile.titleHint")}
                className={`inline-flex items-center rounded-full border border-current px-2.5 py-0.5 text-theme-xs font-semibold ${rank}`}
              >
                {t(locale, `title.${profile.title.code}`)}
              </span>
            )}
            {profile.roles.map((role) => (
              <span
                key={role.code}
                title={
                  role.code === "champion"
                    ? fill(t(locale, "role.championOf"), { contest: role.contest_title })
                    : undefined
                }
              >
                <Badge color={ROLE_COLOR[role.code]}>{t(locale, `role.${role.code}`)}</Badge>
              </span>
            ))}
          </div>
        )}
        {profile.online ? (
          <p className="mt-2 flex items-center gap-1.5 text-theme-xs font-medium rw-ok-ink">
            <span aria-hidden="true" className="size-2 rounded-full bg-current" />
            {t(locale, "profile.online")}
          </p>
        ) : (
          profile.last_seen && (
            <p className="mt-2 text-theme-xs rw-faint">
              {fill(t(locale, "profile.lastSeen"), {
                time: formatRelative(profile.last_seen, locale),
              })}
            </p>
          )
        )}
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

        {profile.external.length > 0 && (
          <ul aria-label={t(locale, "settings.external")} className="mt-4 flex flex-wrap gap-2">
            {profile.external.map((row) => {
              const icon = EXTERNAL_ICONS[row.kind];
              const label = `${EXTERNAL_LABEL[row.kind] ?? row.kind}: ${externalShown(row)}`;
              return (
                <li key={row.kind}>
                  <a
                    href={externalUrl(row)}
                    target="_blank"
                    rel="nofollow ugc noopener noreferrer"
                    title={label}
                    aria-label={label}
                    className="flex size-9 items-center justify-center rw-radius-sm border rw-line rw-strong transition rw-hover-bg rw-focus-ring"
                  >
                    {icon ? (
                      <BrandIcon icon={icon} className="size-4" />
                    ) : (
                      <span className="text-theme-xs font-bold">
                        {(EXTERNAL_LABEL[row.kind] ?? row.kind).slice(0, 2)}
                      </span>
                    )}
                  </a>
                </li>
              );
            })}
          </ul>
        )}

        {profile.pinned.length > 0 && (
          <ul aria-label={t(locale, "profile.pinnedTitle")} className="mt-4 flex flex-wrap gap-2">
            {profile.pinned.map((row) => (
              <li key={row.code}>
                <Medal tier={row.tier} label={achievementLabel(row, locale)} locale={locale} />
              </li>
            ))}
          </ul>
        )}

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
