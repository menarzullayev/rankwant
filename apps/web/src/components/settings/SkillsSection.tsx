"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { ContentName, contentNameText } from "@/components/ui/UzFallbackBadge";
import { fill, localName, t, type Locale } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import {
  putJson,
  type MySkill,
  type SkillBadge,
  type SkillName,
  type Technology,
} from "@/lib/api";
import { BrandIcon, TECH_ICONS } from "@/lib/tech-icons";
import { Hint, Loading, Select, Status, useAction, useLoad } from "./kit";

/** `profiles/views.py` dagi `MAX_ROWS` bilan bir xil. */
const MAX_ROWS = 20;

type Level = { skill: string; level: number };

/** Ko'nikma nomi + qaytish belgisi; katalogda topilmasa — slug.
 *
 *  Katalog nomlari faqat uz/ru/en ustunlarida saqlanadi, ya'ni qolgan
 *  yetti tilda o'zbekcha ko'rinadi va `uz` belgisini oladi (qaror 10).
 */
function SkillLabel({
  slug,
  names,
  locale,
}: {
  slug: string;
  names: Map<string, SkillName>;
  locale: Locale;
}) {
  const found = names.get(slug);
  return found ? <ContentName row={found} locale={locale} /> : <>{slug}</>;
}

function SkillsCard() {
  const locale = useLocale();
  const catalog = useLoad<SkillName[]>("/skills/catalog/");
  const mine = useLoad<MySkill[]>("/me/skills/");
  const action = useAction();
  const [edited, setEdited] = useState<Level[] | null>(null);
  const rows: Level[] =
    edited ?? (mine.data ?? []).map((r) => ({ skill: r.skill, level: r.level }));
  const names = new Map((catalog.data ?? []).map((s) => [s.slug, s]));
  const free = (catalog.data ?? []).filter(
    (s) => !rows.some((row) => row.skill === s.slug),
  );
  const label = (slug: string) => {
    const found = names.get(slug);
    return found ? localName(found, locale) : slug;
  };

  async function save() {
    await action.run(async () => {
      mine.setData(await putJson<MySkill[]>("/me/skills/", rows));
      setEdited(null);
    });
  }

  const loading = (!catalog.data || !mine.data) && !(catalog.error || mine.error);

  return (
    <Card title={t(locale, "settings.skills")}>
      <Hint>{t(locale, "settings.skillsHint")}</Hint>
      {loading ? (
        <div className="mt-3">
          <Loading />
        </div>
      ) : (
        <>
          <ul className="mt-4 space-y-3">
            {rows.map((row, i) => (
              <li key={row.skill} className="flex items-center gap-3">
                <label
                  htmlFor={`skill-${row.skill}`}
                  className="w-36 shrink-0 truncate text-theme-sm rw-strong sm:w-48"
                >
                  <SkillLabel slug={row.skill} names={names} locale={locale} />
                </label>
                <input
                  id={`skill-${row.skill}`}
                  type="range"
                  min={0}
                  max={100}
                  step={5}
                  value={row.level}
                  onChange={(event) =>
                    setEdited(
                      rows.map((r, j) =>
                        j === i ? { ...r, level: Number(event.target.value) } : r,
                      ),
                    )
                  }
                  className="rw-accent-control min-w-0 flex-1"
                />
                <span className="w-9 text-right text-theme-sm tabular-nums rw-dim">
                  {row.level}
                </span>
                <button
                  type="button"
                  onClick={() => setEdited(rows.filter((_, j) => j !== i))}
                  aria-label={`${t(locale, "settings.remove")}: ${label(row.skill)}`}
                  className="flex size-8 shrink-0 items-center justify-center rw-radius-sm rw-dim transition rw-hover-bg rw-focus-ring"
                >
                  <Icon name="nav.close" className="size-4" />
                </button>
              </li>
            ))}
          </ul>
          {free.length > 0 && rows.length < MAX_ROWS && (
            <label className="mt-4 block max-w-xs">
              <span className="sr-only">{t(locale, "settings.skillAdd")}</span>
              <select
                value=""
                onChange={(event) =>
                  event.target.value &&
                  setEdited([...rows, { skill: event.target.value, level: 50 }])
                }
                className="h-11 w-full rw-radius-sm border rw-line px-3 text-theme-sm rw-strong rw-field-bg rw-focus-ring"
              >
                <option value="">{t(locale, "settings.skillAdd")}</option>
                {free.map((s) => (
                  <option key={s.slug} value={s.slug}>
                    {/* Native `<option>` ichida JSX yo'q — belgi matn
                        qo'shimchasi sifatida qo'shiladi. */}
                    {contentNameText(s, locale)}
                  </option>
                ))}
              </select>
            </label>
          )}
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <Button busy={action.busy} disabled={edited === null} onClick={save}>
              {t(locale, "settings.save")}
            </Button>
            <Status
              error={action.error || catalog.error || mine.error}
              done={action.done}
            />
          </div>
        </>
      )}
    </Card>
  );
}

function TechCard() {
  const locale = useLocale();
  const catalog = useLoad<Technology[]>("/technologies/catalog/");
  const mine = useLoad<Technology[]>("/me/technologies/");
  const action = useAction();
  const [picked, setPicked] = useState<string[] | null>(null);
  const current = picked ?? (mine.data ?? []).map((row) => row.slug);
  const full = current.length >= MAX_ROWS;

  async function save() {
    await action.run(async () => {
      mine.setData(await putJson<Technology[]>("/me/technologies/", current));
      setPicked(null);
    });
  }

  return (
    <Card title={t(locale, "settings.technologies")}>
      <Hint>{t(locale, "settings.technologiesHint")}</Hint>
      {!catalog.data || !mine.data ? (
        <div className="mt-3">
          {catalog.error || mine.error ? (
            <Status error={catalog.error || mine.error} />
          ) : (
            <Loading />
          )}
        </div>
      ) : (
        <>
          <ul className="mt-4 flex flex-wrap gap-2">
            {catalog.data.map((tech) => {
              const on = current.includes(tech.slug);
              return (
                <li key={tech.slug}>
                  <button
                    type="button"
                    aria-pressed={on}
                    disabled={!on && full}
                    onClick={() =>
                      setPicked(
                        on
                          ? current.filter((s) => s !== tech.slug)
                          : [...current, tech.slug],
                      )
                    }
                    className={`flex h-9 items-center gap-2 rw-radius-sm border px-3 text-theme-sm transition rw-focus-ring disabled:opacity-50 ${
                      on ? "rw-accent-line rw-accent-soft" : "rw-line rw-dim-2 rw-hover-bg"
                    }`}
                  >
                    <BrandIcon icon={TECH_ICONS[tech.slug]} />
                    {tech.name}
                  </button>
                </li>
              );
            })}
          </ul>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <Button busy={action.busy} disabled={picked === null} onClick={save}>
              {t(locale, "settings.save")}
            </Button>
            <span className="text-theme-sm rw-faint">
              {fill(t(locale, "settings.selected"), {
                count: current.length,
                max: MAX_ROWS,
              })}
            </span>
            <Status error={action.error} done={action.done} />
          </div>
        </>
      )}
    </Card>
  );
}

export function SkillsSection() {
  return (
    <>
      <SkillsCard />
      <TechCard />
      <BadgesCard />
    </>
  );
}

const MAX_BADGES = 10;
const ICONS = Object.keys(TECH_ICONS);

function BadgesCard() {
  const locale = useLocale();
  const loaded = useLoad<SkillBadge[]>("/me/skill-badges/");
  const action = useAction();
  const [edited, setEdited] = useState<SkillBadge[] | null>(null);
  const rows = edited ?? loaded.data ?? [];

  function patch(i: number, part: Partial<SkillBadge>) {
    setEdited(rows.map((row, j) => (j === i ? { ...row, ...part } : row)));
  }

  async function save() {
    const filled = rows.filter((row) => row.text.trim());
    await action.run(async () => {
      loaded.setData(await putJson<SkillBadge[]>("/me/skill-badges/", filled));
      setEdited(null);
    });
  }

  return (
    <Card title={t(locale, "settings.badges")}>
      <Hint>{t(locale, "settings.badgesHint")}</Hint>
      {!loaded.data && !loaded.error ? (
        <div className="mt-3">
          <Loading />
        </div>
      ) : (
        <>
          <ul className="mt-4 space-y-4">
            {rows.map((row, i) => (
              <li key={i} className="relative rw-radius border rw-line p-4 pr-12">
                <button
                  type="button"
                  onClick={() => setEdited(rows.filter((_, j) => j !== i))}
                  aria-label={`${t(locale, "settings.remove")}: ${row.text}`}
                  className="absolute right-2 top-2 flex size-8 items-center justify-center rw-radius-sm rw-dim transition rw-hover-bg rw-focus-ring"
                >
                  <Icon name="nav.close" className="size-4" />
                </button>
                <div className="flex items-center gap-3">
                  <span
                    className="flex size-10 shrink-0 items-center justify-center rounded-full"
                    style={{ background: row.color, color: "#fff" }}
                  >
                    <BrandIcon icon={TECH_ICONS[row.icon]} className="size-5" />
                  </span>
                  <div className="grid min-w-0 flex-1 gap-3 sm:grid-cols-3">
                    <Field
                      label={t(locale, "settings.badgeText")}
                      name={`badge-${i}-text`}
                      value={row.text}
                      maxLength={24}
                      onChange={(event) => patch(i, { text: event.target.value })}
                    />
                    <Select
                      label={t(locale, "settings.badgeIcon")}
                      name={`badge-${i}-icon`}
                      value={row.icon}
                      onChange={(event) => patch(i, { icon: event.target.value })}
                    >
                      {ICONS.map((slug) => (
                        <option key={slug} value={slug}>
                          {slug}
                        </option>
                      ))}
                    </Select>
                    <Field
                      label={t(locale, "settings.badgeColor")}
                      name={`badge-${i}-color`}
                      type="color"
                      value={row.color}
                      onChange={(event) => patch(i, { color: event.target.value })}
                    />
                  </div>
                </div>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            {rows.length < MAX_BADGES && (
              <Button
                variant="outline"
                onClick={() =>
                  setEdited([...rows, { text: "", icon: "python", color: "#4f46e5" }])
                }
              >
                {t(locale, "settings.addBadge")}
              </Button>
            )}
            <Button busy={action.busy} disabled={edited === null} onClick={save}>
              {t(locale, "settings.save")}
            </Button>
            <Status error={action.error || loaded.error} done={action.done} />
          </div>
        </>
      )}
    </Card>
  );
}
