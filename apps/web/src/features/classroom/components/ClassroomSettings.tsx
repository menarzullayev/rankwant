"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { CopyButton } from "@/components/kit/CopyControl";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Segmented } from "@/components/ui/Segmented";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import {
  deleteJson,
  patchJson,
  postJson,
  type ClassroomDetail,
  type ClassroomJoinMode,
} from "@/lib/api";

import { failure } from "./failure";

/** The owner's controls: how students join, the code and its link, archiving
 *  (ADR-0061 § 3). Assistants never see this card — they get no code. */
export function ClassroomSettings({
  room,
  onChange,
}: {
  room: ClassroomDetail;
  onChange: (next: ClassroomDetail) => void;
}) {
  const locale = useLocale();
  const router = useRouter();
  const confirm = useConfirm();
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const path = `/classrooms/${encodeURIComponent(room.slug)}/`;
  const code = room.join_code ?? "";
  // The page's own origin: the card renders only in the browser, after the
  // classroom is fetched, and `SITE_URL` falls back to the API origin locally.
  const link = `${window.location.origin}/classroom/join/${encodeURIComponent(code)}`;

  async function run(name: string, action: () => Promise<void>) {
    setBusy(name);
    setError("");
    try {
      await action();
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy("");
    }
  }

  const setMode = (join_mode: ClassroomJoinMode) =>
    run("mode", async () => {
      await patchJson(path, { join_mode });
      onChange({ ...room, join_mode });
    });

  const refresh = async (origin: HTMLElement) => {
    if (!(await confirm(t(locale, "classroom.refreshConfirm"), {
        kind: "popover",
        origin,
        confirmLabel: t(locale, "classroom.refreshCode"),
      })))
      return;
    await run("code", async () => {
      const next = await postJson<{ join_code: string }>(`${path}refresh-code/`, {});
      onChange({ ...room, join_code: next.join_code });
    });
  };

  const archive = async (origin: HTMLElement) => {
    if (
      !(await confirm(t(locale, "classroom.archiveConfirm"), {
        danger: true,
        kind: "popover",
        origin,
        confirmLabel: t(locale, "classroom.archive"),
      }))
    )
      return;
    await run("archive", async () => {
      await deleteJson(path);
      router.push("/classroom");
    });
  };

  return (
    <Card title={t(locale, "classroom.settings")}>
      <div className="space-y-5">
        <div className="space-y-1">
          <Segmented<ClassroomJoinMode>
            label={t(locale, "classroom.joinMode")}
            value={room.join_mode}
            onChange={(next) => {
              if (next !== room.join_mode && !busy) void setMode(next);
            }}
            options={[
              { value: "approval", label: t(locale, "classroom.joinMode.approval") },
              { value: "instant", label: t(locale, "classroom.joinMode.instant") },
            ]}
          />
          <p className="text-theme-xs rw-dim">{t(locale, "classroom.joinMode.hint")}</p>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <div className="min-w-0 space-y-1">
            <p className="text-theme-sm font-medium rw-strong">{t(locale, "classroom.code")}</p>
            <CopyButton shape="field" text={code} label={t(locale, "classroom.code")} />
          </div>
          <div className="min-w-0 space-y-1">
            <p className="text-theme-sm font-medium rw-strong">
              {t(locale, "classroom.inviteLink")}
            </p>
            <CopyButton shape="field" text={link} label={t(locale, "classroom.inviteLink")} />
          </div>
        </div>

        {error && (
          <p role="alert" className="text-theme-sm rw-bad-ink">
            {error}
          </p>
        )}

        <div className="flex flex-wrap gap-3">
          <Button
            variant="outline"
            busy={busy === "code"}
            onClick={(e) => void refresh(e.currentTarget)}
          >
            {t(locale, "classroom.refreshCode")}
          </Button>
          <Button
            variant="outline"
            busy={busy === "archive"}
            onClick={(e) => void archive(e.currentTarget)}
          >
            {t(locale, "classroom.archive")}
          </Button>
        </div>
      </div>
    </Card>
  );
}
