"use client";

import { useCallback, useEffect, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { getJson } from "@/lib/api";

import type { CoachLinks, CoachStudent, Recommendation } from "../api";
import { CoachRequests } from "./CoachRequests";
import { MyCoaches } from "./MyCoaches";
import { MyStudents } from "./MyStudents";
import { Recommendations } from "./Recommendations";

/** `/coaching`: one page for both sides of a coach link (ADR-0061 § 4). */
export function CoachingPage() {
  const locale = useLocale();
  const [links, setLinks] = useState<CoachLinks | null>(null);
  const [tasks, setTasks] = useState<Recommendation[]>([]);
  const [students, setStudents] = useState<CoachStudent[]>([]);

  const load = useCallback(() => {
    void getJson<CoachLinks>("/coaching/")
      .then(setLinks)
      .catch(() => setLinks({ coaches: [], requests: [] }));
    void getJson<Recommendation[]>("/coaching/recommendations/")
      .then(setTasks)
      .catch(() => setTasks([]));
    void getJson<CoachStudent[]>("/coaching/students/")
      .then(setStudents)
      .catch(() => setStudents([]));
  }, []);

  useEffect(() => load(), [load]);

  if (links === null) return null;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "coaching.title")}</h1>
        <p className="mt-1 max-w-2xl text-theme-sm rw-dim">{t(locale, "coaching.intro")}</p>
      </header>
      {links.requests.length > 0 && <CoachRequests rows={links.requests} onChange={load} />}
      {students.length > 0 && <MyStudents rows={students} onChange={load} />}
      <MyCoaches links={links.coaches} onChange={load} />
      <Recommendations rows={tasks} />
    </div>
  );
}
