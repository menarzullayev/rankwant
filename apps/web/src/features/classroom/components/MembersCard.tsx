"use client";

import Link from "next/link";
import { useState } from "react";

import { useConfirm } from "@/components/overlay/OverlayHost";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { deleteJson, patchJson, type ClassroomMember } from "@/lib/api";

import { failure } from "./failure";
import { RoleBadge } from "./RoleBadge";

/** A member's role after the owner's toggle. */
const OTHER_ROLE: Record<ClassroomMember["role"], ClassroomMember["role"]> = {
  assistant: "student",
  student: "assistant",
};

/** The classroom's members. The owner makes a member an assistant (or a
 *  student again) and takes one out; an assistant only reads the list. */
export function MembersCard({
  slug,
  members,
  owner,
  onChange,
}: {
  slug: string;
  members: ClassroomMember[];
  owner: boolean;
  onChange: () => void;
}) {
  const locale = useLocale();
  const confirm = useConfirm();
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const path = (username: string) =>
    `/classrooms/${encodeURIComponent(slug)}/members/${encodeURIComponent(username)}/`;

  async function run(username: string, action: () => Promise<unknown>) {
    setBusy(username);
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

  const toggle = (m: ClassroomMember) =>
    run(m.username, () => patchJson(path(m.username), { role: OTHER_ROLE[m.role] }));

  const remove = async (m: ClassroomMember, origin: HTMLElement) => {
    const question = fill(t(locale, "classroom.removeConfirm"), { user: m.username });
    if (!(await confirm(question, {
        danger: true,
        kind: "popover",
        origin,
        confirmLabel: t(locale, "classroom.remove"),
      }))) return;
    await run(m.username, () => deleteJson(path(m.username)));
  };

  return (
    <Card title={t(locale, "classroom.members")} bodyClassName="p-0">
      {error && (
        <p role="alert" className="px-5 pt-3 text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <Table>
        <THead>
          <TH>{t(locale, "standings.user")}</TH>
          <TH>{t(locale, "col.role")}</TH>
          <TH align="right">Skills</TH>
          {owner && <TH align="right">{t(locale, "admin.actions")}</TH>}
        </THead>
        <TBody>
          {members.map((m) => (
            <TR key={m.username}>
              <TD>
                <Link href={`/users/${m.username}`} className="font-medium rw-link-hover">
                  {m.username}
                </Link>
              </TD>
              <TD>
                <RoleBadge role={m.role} />
              </TD>
              <TD align="right">{m.rating_skills}</TD>
              {owner && (
                <TD align="right">
                  <div className="flex flex-wrap justify-end gap-2">
                    <Button
                      variant="outline"
                      busy={busy === m.username}
                      onClick={() => void toggle(m)}
                    >
                      {t(
                        locale,
                        m.role === "assistant" ? "classroom.makeStudent" : "classroom.makeAssistant",
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      disabled={busy === m.username}
                      onClick={(e) => void remove(m, e.currentTarget)}
                    >
                      {t(locale, "classroom.remove")}
                    </Button>
                  </div>
                </TD>
              )}
            </TR>
          ))}
          {members.length === 0 && (
            <EmptyRow colSpan={owner ? 4 : 3}>{t(locale, "common.empty")}</EmptyRow>
          )}
        </TBody>
      </Table>
    </Card>
  );
}
