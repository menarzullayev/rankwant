"use client";

import Link from "next/link";
import { useState } from "react";

import { FormBox } from "@/components/form/FormKit";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { patchJson, postJson } from "@/lib/api";

import { MAX_COACHES, type CoachLink } from "../api";
import { failure } from "./failure";

/** The student's side: ask someone to coach you, see who accepted, decide
 *  per coach whether they may open your solutions, end a link. */
export function MyCoaches({ links, onChange }: { links: CoachLink[]; onChange: () => void }) {
  const locale = useLocale();
  const confirm = useConfirm();
  const [name, setName] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const full = links.length >= MAX_COACHES;

  async function run(key: string, action: () => Promise<unknown>) {
    setBusy(key);
    setError("");
    try {
      await action();
      onChange();
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy("");
    }
  }

  async function ask(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const coach = name.trim().replace(/^@/, "");
    if (!coach) return;
    await run("ask", async () => {
      await postJson("/coaching/", { coach });
      setName("");
    });
  }

  async function end(link: CoachLink, origin: HTMLElement) {
    const pending = link.status === "pending";
    const question = fill(
      t(locale, pending ? "coaching.withdrawConfirm" : "coaching.endConfirm"),
      { user: link.coach.username },
    );
    const label = t(locale, pending ? "coaching.withdraw" : "coaching.end");
    if (!(await confirm(question, { danger: true, kind: "popover", origin, confirmLabel: label })))
      return;
    await run(`end${link.id}`, () => postJson(`/coaching/${link.id}/end/`, {}));
  }

  return (
    <Card title={t(locale, "coaching.mine")}>
      <div className="space-y-4">
        <p className="text-theme-sm rw-dim">{t(locale, "coaching.mineHint")}</p>
        <form onSubmit={ask} className="flex flex-wrap items-end gap-2">
          <div className="min-w-0 flex-1">
            <Field
              name="coach"
              label={t(locale, "coaching.askLabel")}
              value={name}
              onChange={(event) => setName(event.target.value)}
              disabled={full}
            />
          </div>
          <Button type="submit" busy={busy === "ask"} disabled={full || !name.trim()}>
            {t(locale, "coaching.ask")}
          </Button>
        </form>
        <p className={`text-theme-xs ${full ? "rw-bad-ink" : "rw-faint"}`}>
          {fill(t(locale, "coaching.limit"), { count: links.length, limit: MAX_COACHES })}
        </p>
        {error && (
          <p role="alert" className="text-theme-sm rw-bad-ink">
            {error}
          </p>
        )}
        {links.length > 0 && (
          <ul className="divide-y rw-divide">
            {links.map((link) => (
              <li key={link.id} className="flex flex-wrap items-center gap-3 py-3">
                <div className="min-w-0 flex-1">
                  <Link href={`/users/${link.coach.username}`} className="font-medium rw-link-hover">
                    {link.coach.display_name || link.coach.username}
                  </Link>
                  <span className="ml-2">
                    <Badge color={link.status === "active" ? "success" : "warning"}>
                      {t(locale, link.status === "active" ? "coaching.active" : "coaching.pending")}
                    </Badge>
                  </span>
                </div>
                <label className="flex items-center gap-2 text-theme-sm rw-dim">
                  <FormBox
                    shape="switch"
                    checked={link.can_view_attempts}
                    aria-label={fill(t(locale, "coaching.consentFor"), {
                      user: link.coach.username,
                    })}
                    disabled={busy !== ""}
                    onChange={(event) =>
                      void run(`consent${link.id}`, () =>
                        patchJson(`/coaching/${link.id}/`, {
                          can_view_attempts: event.target.checked,
                        }),
                      )
                    }
                  />
                  {t(locale, "coaching.consent")}
                </label>
                <Button
                  variant="outline"
                  busy={busy === `end${link.id}`}
                  onClick={(event) => void end(link, event.currentTarget)}
                >
                  {t(locale, link.status === "pending" ? "coaching.withdraw" : "coaching.end")}
                </Button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Card>
  );
}
