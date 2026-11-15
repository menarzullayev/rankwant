"use client";

import type { Route } from "next";
import { useEffect } from "react";

import { ButtonLink } from "@/components/ui/Button";
import { track } from "@/lib/analytics";

/**
 * The hero's two buttons and its measurement (decision 2026-11-15): the first block was
 * seen (`home.hero_view`), and which button was pressed (`home.hero_cta`, `cta` is
 * `register` or `browse`). Both join the funnel the sign-up form already writes to
 * (`auth.form_started` → `auth.register_done`), under the same per-tab id, so the staff
 * view reads seen → pressed → form → registered. No personal data is attached.
 *
 * The page is cached for guests, so the events are sent from the browser, not the server.
 */
export function HeroActions({ start, browse }: { start: string; browse: string }) {
  useEffect(() => {
    track("home.hero_view");
  }, []);

  return (
    <div className="mt-6 flex flex-wrap gap-3">
      <ButtonLink
        intent
        href={"/login?tab=register" as Route}
        onClick={() => track("home.hero_cta", { cta: "register" })}
      >
        {start}
      </ButtonLink>
      <ButtonLink
        intent
        href="/problems"
        variant="outline"
        onClick={() => track("home.hero_cta", { cta: "browse" })}
      >
        {browse}
      </ButtonLink>
    </div>
  );
}
