"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, localName, t } from "@/i18n/messages";
import { CloseIcon } from "@/icons";
import {
  putJson,
  type MySkill,
  type SkillName,
  type Technology,
} from "@/lib/api";
import { BrandIcon, TECH_ICONS } from "@/lib/tech-icons";
import { Hint, Loading, Status, useAction, useLoad } from "./kit";

/** `profiles/views.py` dagi `MAX_ROWS` bilan bir xil. */
const MAX_ROWS = 20;

type Level = { skill: string; level: number };

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
                  {label(row.skill)}
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
                  <CloseIcon className="size-4" />
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
                    {localName(s, locale)}
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
    </>
  );
}
