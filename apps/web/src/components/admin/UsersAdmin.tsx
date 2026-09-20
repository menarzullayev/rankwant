"use client";

import { useState } from "react";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { useLocale } from "@/i18n/LocaleProvider";
import { date, fill, t, errorText as translateError, type Locale } from "@/i18n/messages";

import { FM_INP } from "@/components/form/chrome";
import {
  type ColumnDef,
  CrudPage,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type StaffUser = {
  id: number;
  username: string;
  email: string;
  display_name: string;
  bio: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  rating_skills: number;
  rating_contest: number;
  rating_activity: number;
  rating_challenges: number;
  qvant_balance: number | null;
  date_joined: string;
  last_login: string | null;
  [key: string]: unknown;
};

const PATH = "/staff/users/";

const INPUT = FM_INP;

const COLUMNS: ColumnDef<StaffUser>[] = [
  { key: "username", labelKey: "admin.label.text.username" },
  { key: "display_name", labelKey: "admin.label.text.displayName" },
  { key: "email", labelKey: "admin.label.text.email" },
  {
    key: "ratings",
    labelKey: "admin.label.misc.ratings",
    render: (u) => (
      <span
        className="font-mono text-theme-xs"
        title="skills / contest / activity / challenges"
      >
        {u.rating_skills} / {u.rating_contest} / {u.rating_activity} /{" "}
        {u.rating_challenges}
      </span>
    ),
  },
  {
    key: "is_active",
    labelKey: "admin.label.flag.active",
    render: (u, _reload, locale) =>
      u.is_active ? (
        <Badge color="success">{t(locale, "admin.text.badgeActive")}</Badge>
      ) : (
        <Badge color="error">{t(locale, "admin.text.badgeBlocked")}</Badge>
      ),
  },
  {
    key: "is_staff",
    labelKey: "admin.label.flag.staff",
    render: (u, _reload, locale) =>
      u.is_superuser ? (
        <Badge color="brand">{t(locale, "admin.text.badgeSuperuser")}</Badge>
      ) : u.is_staff ? (
        <Badge color="info">{t(locale, "admin.text.badgeStaff")}</Badge>
      ) : (
        <span className="rw-faint">—</span>
      ),
  },
  {
    key: "date_joined",
    labelKey: "admin.label.date.joined",
    render: (u, _reload, locale) => date(u.date_joined, locale),
  },
];

const FIELDS: FieldDef[] = [
  { name: "display_name", labelKey: "admin.label.name.shown" },
  { name: "bio", labelKey: "admin.label.text.bio", type: "textarea", rows: 3 },
  {
    name: "is_active",
    labelKey: "admin.label.flag.activeHint",
    type: "checkbox",
  },
  {
    name: "is_staff",
    labelKey: "admin.label.flag.staff",
    type: "checkbox",
    helpKey: "admin.help.staffOnlySuperuser",
  },
];

function errorText(locale: Locale, e: unknown): string {
  return e instanceof ApiError
    ? translateError(locale, e.code, e.message)
    : String(e);
}

/** Bitta amal formasi holati: yuborilmoqda / natija / xato. */
function useAction() {
  const locale = useLocale();
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  async function run(fn: () => Promise<string>) {
    setBusy(true);
    setMsg("");
    setErr("");
    try {
      setMsg(await fn());
    } catch (e) {
      setErr(errorText(locale, e));
    } finally {
      setBusy(false);
    }
  }
  const status = (
    <>
      {msg && <p className="text-theme-xs rw-ok-ink">{msg}</p>}
      {err && <p className="text-theme-xs rw-bad-ink">{err}</p>}
    </>
  );
  return { busy, run, status };
}

function QvantForm({ user, reload }: { user: StaffUser; reload: () => void }) {
  const locale = useLocale();
  const { busy, run, status } = useAction();

  function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    void run(async () => {
      const r = await staff.action<{ amount: number; balance: number }>(
        `${PATH}${user.username}/qvant/`,
        {
          amount: Number(data.get("amount")),
          note: String(data.get("note") ?? ""),
        },
      );
      form.reset();
      reload();
      return `${r.amount > 0 ? "+" : ""}${r.amount} Qvant · balans: ${r.balance}`;
    });
  }

  return (
    <form onSubmit={submit} className="space-y-2">
      <p className="text-theme-sm font-medium rw-strong">
        Qvant tuzatish{" "}
        <span className="font-normal rw-faint">
          (balans: {user.qvant_balance ?? 0})
        </span>
      </p>
      <div className="flex gap-2">
        <input
          name="amount"
          type="number"
          required
          step={1}
          placeholder={t(locale, "admin.placeholder.amount")}
          className={`${INPUT} w-28`}
        />
        <input
          name="note"
          required
          maxLength={200}
          placeholder={t(locale, "admin.placeholder.ledgerComment")}
          className={INPUT}
        />
        <Button type="submit" className="h-10 shrink-0" disabled={busy}>
          {t(locale, "admin.text.apply")}
        </Button>
      </div>
      {status}
    </form>
  );
}

function NotifyForm({ user }: { user: StaffUser }) {
  const locale = useLocale();
  const { busy, run, status } = useAction();

  function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    void run(async () => {
      await staff.action(`${PATH}${user.username}/notify/`, {
        title: String(data.get("title") ?? ""),
        body: String(data.get("body") ?? ""),
      });
      form.reset();
      return "Bildirishnoma yuborildi";
    });
  }

  return (
    <form onSubmit={submit} className="space-y-2">
      <p className="text-theme-sm font-medium rw-strong">{t(locale, "common.notification")}</p>
      <input
        name="title"
        required
        maxLength={200}
        placeholder={t(locale, "admin.placeholder.title")}
        className={INPUT}
      />
      <textarea
        name="body"
        rows={2}
        placeholder={t(locale, "admin.placeholder.text")}
        className={`${INPUT} h-auto py-2`}
      />
      <Button type="submit" variant="outline" className="h-10" disabled={busy}>
        {t(locale, "roadmap.suggestSend")}
      </Button>
      {status}
    </form>
  );
}

function BroadcastForm() {
  const locale = useLocale();
  const confirm = useConfirm();
  const { busy, run, status } = useAction();

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    const title = String(data.get("title") ?? "");
    if (
      !(await confirm(
        fill(t(locale, "admin.broadcastConfirm"), { title }),
        { danger: true, kind: "cmdk" },
      ))
    )
      return;
    void run(async () => {
      const r = await staff.action<{ count: number }>(`${PATH}broadcast/`, {
        title,
        body: String(data.get("body") ?? ""),
      });
      form.reset();
      return `${r.count} foydalanuvchiga yuborildi`;
    });
  }

  return (
    <Card title={t(locale, "admin.title.broadcast")} bodyClassName="p-5">
      <form
        onSubmit={submit}
        className="grid gap-2 md:grid-cols-[1fr_2fr_auto]"
      >
        <input
          name="title"
          required
          maxLength={200}
          placeholder={t(locale, "admin.placeholder.title")}
          className={INPUT}
        />
        <input name="body" placeholder={t(locale, "admin.placeholder.textOptional")} className={INPUT} />
        <Button type="submit" className="h-10" disabled={busy}>
          {t(locale, "admin.text.sendToAll")}
        </Button>
        <div className="md:col-span-3">{status}</div>
      </form>
    </Card>
  );
}

export function UsersAdmin() {
  const locale = useLocale();
  return (
    <div className="space-y-4">
      <BroadcastForm />
      <CrudPage<StaffUser>
        title={t(locale, "admin.section.users")}
        path={PATH}
        idField="username"
        columns={COLUMNS}
        fields={FIELDS}
        ordering="-date_joined"
        canDelete={false}
        rowExtra={(u, reload) => (
          <div className="grid gap-6 md:grid-cols-2">
            <QvantForm user={u} reload={reload} />
            <NotifyForm user={u} />
          </div>
        )}
      />
    </div>
  );
}
