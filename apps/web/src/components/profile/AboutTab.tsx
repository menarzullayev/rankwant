import { Card } from "@/components/ui/Card";
import { CountryFlag } from "@/components/ui/CountryFlag";
import { UzFallbackBadge } from "@/components/ui/UzFallbackBadge";
import { localName, localNameInfo, t, type Locale } from "@/i18n/messages";
import type { PrivacyField, PublicProfile } from "@/lib/api";
import { countryName } from "@/lib/countries";
import { districtName, regionName } from "@/lib/regions";
import { BrandIcon, EXTERNAL_ICONS, TECH_ICONS } from "@/lib/tech-icons";
import { EXTERNAL_LABEL, externalUrl, hostOf } from "@/lib/external-links";
import { formatDate } from "@/lib/format";

const years = (start: number | null, end: number | null, locale: Locale) =>
  start || end
    ? `${start ?? "…"} – ${end ?? t(locale, "profile.present")}`
    : "";

export function AboutTab({
  profile,
  locale,
}: {
  profile: PublicProfile;
  locale: Locale;
}) {
  const { info } = profile;
  const hidden = new Set(profile.hidden_fields);
  // Egasi yashirgan maydonini ham ko'radi — belgi bilan, begonaga
  // qanday ko'rinishini adashtirmasligi uchun.
  const mark = (field: PrivacyField) =>
    hidden.has(field) ? (
      <span className="ml-2 rw-radius-sm rw-chip px-1.5 py-0.5 text-theme-xs">
        {t(locale, "profile.hiddenChip")}
      </span>
    ) : null;

  const rows: { label: string; value: React.ReactNode; field: PrivacyField }[] = [];
  if (info.country) {
    const region =
      info.region && (info.country === "UZ" ? regionName(info.region, locale) : info.region);
    rows.push({
      label: t(locale, "settings.country"),
      // Bayroq nomning YONIDA: u bezak (`aria-hidden`), chunki davlat
      // nomi allaqachon matn bo'lib turibdi — skrinrider uni ikki marta
      // o'qimasligi kerak.
      value: (
        <span className="inline-flex items-center gap-1.5">
          <CountryFlag code={info.country} />
          {[
            countryName(info.country, locale),
            region,
            info.district ? districtName(info.district, locale) : info.city,
          ]
            .filter(Boolean)
            .join(", ")}
        </span>
      ),
      field: "country",
    });
  }
  if (info.school)
    rows.push({ label: t(locale, "settings.school"), value: info.school, field: "school" });
  if (info.grade)
    rows.push({ label: t(locale, "settings.grade"), value: info.grade, field: "grade" });
  if (info.birth_date)
    rows.push({
      label: t(locale, "settings.birthDate"),
      // Kalendar sanasi — UTC yarim tunda o'qiladi, zona siljitmasin.
      value: formatDate(info.birth_date, locale, { dateStyle: "long", timeZone: "UTC" }),
      field: "birth_date",
    });
  if (info.email)
    rows.push({
      label: t(locale, "auth.email"),
      value: (
        <a href={`mailto:${info.email}`} className="rw-accent-ink hover:underline">
          {info.email}
        </a>
      ),
      field: "email",
    });
  if (info.website)
    rows.push({
      label: t(locale, "settings.website"),
      value: (
        <a
          href={info.website}
          target="_blank"
          rel="nofollow ugc noopener noreferrer"
          className="break-all rw-accent-ink hover:underline"
        >
          {info.website.replace(/^https?:\/\//, "").replace(/\/$/, "")}
        </a>
      ),
      field: "website",
    });

  const empty =
    rows.length === 0 &&
    profile.skills.length === 0 &&
    profile.technologies.length === 0 &&
    profile.educations.length === 0 &&
    profile.work.length === 0 &&
    profile.external.length === 0;

  if (empty) {
    return (
      <Card>
        <p className="text-theme-sm rw-faint">{t(locale, "profile.aboutEmpty")}</p>
      </Card>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {rows.length > 0 && (
        <Card title={t(locale, "settings.info")}>
          <dl className="divide-y rw-divide">
            {rows.map((row) => (
              <div key={row.field} className="grid gap-1 py-2.5 sm:grid-cols-[10rem_1fr]">
                <dt className="text-theme-sm rw-dim">{row.label}</dt>
                <dd className="text-theme-sm rw-strong">
                  {row.value}
                  {mark(row.field)}
                </dd>
              </div>
            ))}
          </dl>
        </Card>
      )}

      {profile.external.length > 0 && (
        <Card title={t(locale, "settings.external")}>
          <ul className="divide-y rw-divide">
            {profile.external.map((row) => (
              <li key={row.kind} className="flex items-center gap-3 py-2.5">
                <span className="flex size-8 shrink-0 items-center justify-center rw-radius-sm rw-chip">
                  {EXTERNAL_ICONS[row.kind] ? (
                    <BrandIcon icon={EXTERNAL_ICONS[row.kind]} />
                  ) : (
                    <span className="text-theme-xs font-bold">
                      {EXTERNAL_LABEL[row.kind].slice(0, 2)}
                    </span>
                  )}
                </span>
                <a
                  href={externalUrl(row)}
                  target="_blank"
                  rel="nofollow ugc noopener noreferrer"
                  className="min-w-0 flex-1 truncate text-theme-sm rw-strong hover:underline"
                >
                  {EXTERNAL_LABEL[row.kind]}
                  {row.kind !== "linkedin" && (
                    <span className="ml-1.5 rw-dim">
                      {row.kind === "blog" ? hostOf(row.handle) : row.handle}
                    </span>
                  )}
                </a>
                {row.rating !== null && (
                  <span className="text-right text-theme-sm tabular-nums rw-strong">
                    {row.rating}
                    {row.rank && (
                      <span className="block text-theme-xs font-normal rw-faint">{row.rank}</span>
                    )}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {profile.skills.length > 0 && (
        <Card title={t(locale, "settings.skills")}>
          <ul className="space-y-3">
            {profile.skills.map((skill) => (
              <li key={skill.slug}>
                <div className="flex items-baseline justify-between gap-2 text-theme-sm">
                  <span className="rw-strong">
                    {localName(skill, locale)}
                    {localNameInfo(skill, locale).locale === null && (
                      <UzFallbackBadge locale={locale} />
                    )}
                  </span>
                  <span className="tabular-nums rw-faint">{skill.level}</span>
                </div>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${skill.level}%`, background: "var(--rw-accent)" }}
                  />
                </div>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {profile.technologies.length > 0 && (
        <Card title={t(locale, "settings.technologies")}>
          <ul className="flex flex-wrap gap-2">
            {profile.technologies.map((tech) => (
              <li
                key={tech.slug}
                className="flex h-8 items-center gap-2 rw-radius-sm rw-chip px-3 text-theme-sm"
              >
                <BrandIcon icon={TECH_ICONS[tech.slug]} />
                {tech.name}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {(profile.educations.length > 0 || profile.work.length > 0) && (
        <Card title={t(locale, "settings.nav.career")} className="lg:col-span-2">
          <div className="grid gap-6 md:grid-cols-2">
            {profile.educations.length > 0 && (
              <section>
                <h3 className="mb-2 text-theme-sm font-semibold rw-dim">
                  {t(locale, "settings.education")}
                </h3>
                <ul className="space-y-3">
                  {profile.educations.map((row, i) => (
                    <li key={i} className="border-l-2 rw-accent-line pl-3">
                      <p className="text-theme-sm font-medium rw-strong">{row.organization}</p>
                      <p className="text-theme-xs rw-dim">
                        {[row.degree, years(row.start_year, row.end_year, locale)]
                          .filter(Boolean)
                          .join(" · ")}
                      </p>
                    </li>
                  ))}
                </ul>
              </section>
            )}
            {profile.work.length > 0 && (
              <section>
                <h3 className="mb-2 text-theme-sm font-semibold rw-dim">
                  {t(locale, "settings.work")}
                </h3>
                <ul className="space-y-3">
                  {profile.work.map((row, i) => (
                    <li key={i} className="border-l-2 rw-accent-line pl-3">
                      <p className="text-theme-sm font-medium rw-strong">{row.company}</p>
                      <p className="text-theme-xs rw-dim">
                        {[row.title, years(row.start_year, row.end_year, locale)]
                          .filter(Boolean)
                          .join(" · ")}
                      </p>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
