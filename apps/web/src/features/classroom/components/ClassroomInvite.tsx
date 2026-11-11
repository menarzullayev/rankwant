"use client";

import { SignInGate } from "@/components/auth/SignInGate";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import {
  getJson,
  postJson,
  type ClassroomInvite as Invite,
  type ClassroomJoinResult,
} from "@/lib/api";

import { failure } from "./failure";

/** An invite link (`/classroom/join/<code>`): whose classroom it is, then one
 *  button. A classroom that asks for approval sends a request instead of
 *  letting the student in (ADR-0061 § 3). */
export function ClassroomInvite({ code }: { code: string }) {
  const locale = useLocale();
  const router = useRouter();
  const { user, ready } = useSession();
  const [invite, setInvite] = useState<Invite | null>(null);
  const [missing, setMissing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    getJson<Invite>(`/classrooms/invite/${encodeURIComponent(code)}/`)
      .then(setInvite)
      .catch(() => setMissing(true));
  }, [user, code]);

  async function join() {
    setBusy(true);
    setError("");
    try {
      const result = await postJson<ClassroomJoinResult>("/classrooms/join/", { join_code: code });
      if (result.status === "member") {
        router.push(`/classroom/${encodeURIComponent(result.slug)}`);
        return;
      }
      setInvite((current) => (current ? { ...current, state: "pending" } : current));
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(false);
    }
  }

  if (ready && !user) return <SignInGate reason="classroom" />;
  if (missing)
    return (
      <Card title={t(locale, "classroom.invite.title")}>
        <p className="text-theme-sm rw-dim">{t(locale, "classroom.invite.invalid")}</p>
      </Card>
    );
  if (!invite) return null;

  const inside = invite.state === "member" || invite.state === "owner";
  const approval = invite.join_mode === "approval";

  return (
    <Card title={t(locale, "classroom.invite.title")}>
      <div className="space-y-4">
        <div>
          <h1 className="text-title-sm font-bold rw-strong">{invite.name}</h1>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge>{fill(t(locale, "classroom.invite.by"), { owner: invite.owner })}</Badge>
            <Badge>{fill(t(locale, "classroom.students"), { count: invite.member_count })}</Badge>
          </div>
        </div>
        {inside ? (
          <ButtonLink href={`/classroom/${encodeURIComponent(invite.slug)}` as Route}>
            {t(locale, "classroom.invite.open")}
          </ButtonLink>
        ) : invite.state === "pending" ? (
          <p role="status" className="text-theme-sm rw-dim">
            {t(locale, "classroom.invite.pending")}
          </p>
        ) : (
          <div className="space-y-2">
            {approval && (
              <p className="text-theme-sm rw-dim">{t(locale, "classroom.invite.approvalNote")}</p>
            )}
            <Button busy={busy} onClick={() => void join()}>
              {t(locale, approval ? "classroom.invite.request" : "classroom.invite.join")}
            </Button>
          </div>
        )}
        {error && (
          <p role="alert" className="text-theme-sm rw-bad-ink">
            {error}
          </p>
        )}
      </div>
    </Card>
  );
}
