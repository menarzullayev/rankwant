"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { Avatar } from "@/components/Avatar";
import { rankClass } from "@/components/UserName";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { CopyButton } from "@/components/kit/CopyControl";
import { InlineConfirm } from "@/components/kit/ConfirmExtras";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { deleteJson, postJson, type Team } from "@/lib/api";
import { SITE_URL } from "@/lib/site";
import { Hint, Loading, Status, useAction, useLoad } from "./kit";

const inviteLink = (team: Team) =>
  `${SITE_URL}/settings/jamoalar?join=${encodeURIComponent(team.join_code)}`;

function TeamCard({ team, onChange }: { team: Team; onChange: () => void }) {
  const locale = useLocale();
  const confirm = useConfirm();
  const { user } = useSession();
  const action = useAction();
  const owner = team.role === "owner";
  const act = (fn: () => Promise<unknown>) =>
    action.run(async () => {
      await fn();
      onChange();
    });

  return (
    <Card
      title={
        <h2 className="flex flex-wrap items-center gap-2 text-theme-xl font-semibold rw-strong">
          {team.name}
          <span className="rw-radius-sm rw-chip px-2 py-0.5 text-theme-xs font-medium">
            {owner ? t(locale, "settings.teamOwner") : t(locale, "settings.teamMember")}
          </span>
        </h2>
      }
    >
      <ul className="divide-y rw-divide">
        {team.members.map((member) => (
          <li key={member.username} className="flex items-center gap-3 py-2.5">
            <Avatar url={member.avatar_url} name={member.display_name || member.username} className="size-8 text-theme-sm" />
            <Link
              href={`/users/${member.username}`}
              className={`min-w-0 flex-1 truncate text-theme-sm hover:underline ${rankClass(member.title)}`}
            >
              {member.display_name || member.username}
              <span className="ml-1.5 rw-faint">@{member.username}</span>
            </Link>
            {member.role === "owner" ? (
              <span className="text-theme-xs rw-faint">{t(locale, "settings.teamOwner")}</span>
            ) : (
              owner &&
              member.username !== user?.username && (
                <InlineConfirm
                  label={t(locale, "settings.teamRemove")}
                  danger
                  disabled={action.busy}
                  onConfirm={() =>
                    void act(() =>
                      deleteJson(`/teams/${team.id}/members/${member.username}/`),
                    )
                  }
                />
              )
            )}
          </li>
        ))}
      </ul>

      <div className="mt-4 space-y-2">
        <p className="text-theme-sm font-medium rw-strong">{t(locale, "settings.teamInvite")}</p>
        <div className="flex flex-wrap items-center gap-2">
          <code className="min-w-0 flex-1 truncate rw-radius-sm rw-chip px-3 py-2 text-theme-xs">
            {inviteLink(team)}
          </code>
          <CopyButton
            text={inviteLink(team)}
            tone="chip"
            label={t(locale, "settings.teamCopy")}
            copiedLabel={t(locale, "settings.teamCopied")}
          />
          {owner && (
            <Button
              variant="outline"
              className="h-9 px-3"
              title={t(locale, "settings.teamRefreshHint")}
              disabled={action.busy}
              onClick={() => act(() => postJson(`/teams/${team.id}/refresh-code/`, {}))}
            >
              {t(locale, "settings.teamRefresh")}
            </Button>
          )}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <InlineConfirm
          label={t(locale, "settings.teamLeave")}
          danger
          disabled={action.busy}
          onConfirm={() => void act(() => postJson(`/teams/${team.id}/leave/`, {}))}
        />
        {owner && (
          <Button
            variant="outline"
            className="h-9 px-3 rw-bad-ink"
            disabled={action.busy}
            onClick={() => {
              void (async () => {
                if (
                  await confirm(t(locale, "settings.teamDeleteConfirm"), {
                    danger: true,
                  })
                )
                  void act(() => deleteJson(`/teams/${team.id}/`));
              })();
            }}
          >
            {t(locale, "settings.teamDelete")}
          </Button>
        )}
      </div>
      <div className="mt-3">
        <Status error={action.error} />
      </div>
    </Card>
  );
}

export function TeamsSection() {
  const locale = useLocale();
  const params = useSearchParams();
  const teams = useLoad<Team[]>("/me/teams/");
  const create = useAction();
  const join = useAction();
  const invite = params.get("join") ?? "";

  async function onCreate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const element = event.currentTarget;
    const name = String(new FormData(element).get("name") ?? "").trim();
    const ok = await create.run(() => postJson("/me/teams/", { name }));
    if (ok) {
      element.reset();
      teams.reload();
    }
  }

  async function onJoin(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const element = event.currentTarget;
    const code = String(new FormData(element).get("code") ?? "").trim();
    const ok = await join.run(() => postJson("/teams/join/", { code }));
    if (ok) {
      element.reset();
      teams.reload();
    }
  }

  return (
    <>
      <Card title={t(locale, "settings.teams")}>
        <Hint>{t(locale, "settings.teamsHint")}</Hint>
        <div className="mt-4 grid gap-6 md:grid-cols-2">
          <form onSubmit={onCreate} className="flex flex-col gap-3">
            <Field label={t(locale, "settings.teamName")} name="name" required minLength={2} maxLength={60} />
            <Status error={create.error} />
            <Button type="submit" busy={create.busy} className="self-start">
              {t(locale, "settings.teamCreate")}
            </Button>
          </form>
          <form onSubmit={onJoin} className="flex flex-col gap-3">
            <Field
              label={t(locale, "settings.teamJoinCode")}
              name="code"
              required
              defaultValue={invite}
              autoComplete="off"
              spellCheck={false}
              hint={invite ? t(locale, "settings.teamInvited") : undefined}
            />
            <Status error={join.error} done={join.done} text={t(locale, "settings.teamJoined")} />
            <Button type="submit" busy={join.busy} className="self-start">
              {t(locale, "settings.teamJoin")}
            </Button>
          </form>
        </div>
      </Card>

      {!teams.data && !teams.error && <Loading />}
      {teams.error && <Status error={teams.error} />}
      {teams.data?.length === 0 && (
        <p className="text-theme-sm rw-dim">{t(locale, "settings.teamsEmpty")}</p>
      )}
      {teams.data?.map((team) => (
        <TeamCard key={team.id} team={team} onChange={teams.reload} />
      ))}
    </>
  );
}
