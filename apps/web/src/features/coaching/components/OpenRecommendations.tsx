"use client";

import { useEffect, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { getJson } from "@/lib/api";

import type { Recommendation } from "../api";
import { Recommendations } from "./Recommendations";

/** What the student's coaches suggested and is not solved yet, beside the
 *  classroom assignments: both are the student's tasks (ADR-0061 § 4). */
export function OpenRecommendations() {
  const { user } = useSession();
  const [rows, setRows] = useState<Recommendation[]>([]);

  useEffect(() => {
    if (!user) return;
    getJson<Recommendation[]>("/coaching/recommendations/")
      .then(setRows)
      .catch(() => setRows([]));
  }, [user]);

  return <Recommendations rows={rows} onlyOpen />;
}
