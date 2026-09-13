"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button, ButtonLink } from "@/components/ui/Button";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { deleteJson, postJson } from "@/lib/api";

type State = { followers: number; is_following: boolean };

/** Kuzatish. Sanoq sahifa sarlavhasida (server) — javobdan keyin sahifa
 *  yangilanadi, ya'ni raqam ham, tugma ham bir manbadan keladi. */
export function FollowButton({
  username,
  following,
}: {
  username: string;
  following: boolean;
}) {
  const locale = useLocale();
  const router = useRouter();
  const { user, ready } = useSession();
  const [on, setOn] = useState(following);
  const [busy, setBusy] = useState(false);

  if (!ready) return <div className="h-11 w-28" />;
  if (!user) {
    return (
      <ButtonLink href={"/kirish?tab=login" as Route} variant="outline">
        {t(locale, "profile.follow")}
      </ButtonLink>
    );
  }

  async function toggle() {
    setBusy(true);
    try {
      const path = `/users/${encodeURIComponent(username)}/follow/`;
      const next = on
        ? await deleteJson<State>(path)
        : await postJson<State>(path, {});
      setOn(next.is_following);
      router.refresh();
    } catch {
      // Holat o'zgarmadi — tugma avvalgi ko'rinishida qoladi.
    } finally {
      setBusy(false);
    }
  }

  return (
    <Button
      variant={on ? "outline" : "primary"}
      busy={busy}
      aria-pressed={on}
      onClick={toggle}
    >
      {on ? t(locale, "profile.following") : t(locale, "profile.follow")}
    </Button>
  );
}
