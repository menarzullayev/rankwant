"use client";

import { useState } from "react";

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

const INPUT =
  "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-theme-sm outline-none " +
  "focus:border-brand-400 dark:border-[#232936] dark:bg-[#0b0d12] dark:text-white/90";

const COLUMNS: ColumnDef<StaffUser>[] = [
  { key: "username", label: "Login" },
  { key: "display_name", label: "Ism" },
  { key: "email", label: "Email" },
  {
    key: "ratings",
    label: "Reytinglar",
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
    label: "Faol",
    render: (u) =>
      u.is_active ? (
        <Badge color="success">faol</Badge>
      ) : (
        <Badge color="error">bloklangan</Badge>
      ),
  },
  {
    key: "is_staff",
    label: "Xodim",
    render: (u) =>
      u.is_superuser ? (
        <Badge color="brand">superuser</Badge>
      ) : u.is_staff ? (
        <Badge color="info">xodim</Badge>
      ) : (
        <span className="text-gray-400">—</span>
      ),
  },
  {
    key: "date_joined",
    label: "Qo'shilgan",
    render: (u) => new Date(u.date_joined).toLocaleDateString(),
  },
];

const FIELDS: FieldDef[] = [
  { name: "display_name", label: "Ko'rsatiladigan ism" },
  { name: "bio", label: "Bio", type: "textarea", rows: 3 },
  {
    name: "is_active",
    label: "Faol (bloklash uchun olib tashlang)",
    type: "checkbox",
  },
  {
    name: "is_staff",
    label: "Xodim",
    type: "checkbox",
    help: "Faqat superuser o'zgartira oladi. O'z hisobingizni o'zgartira olmaysiz.",
  },
];

function errorText(e: unknown): string {
  return e instanceof ApiError ? e.message : String(e);
}

/** Bitta amal formasi holati: yuborilmoqda / natija / xato. */
function useAction() {
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
      setErr(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  const status = (
    <>
      {msg && (
        <p className="text-theme-xs text-success-600 dark:text-success-400">
          {msg}
        </p>
      )}
      {err && (
        <p className="text-theme-xs text-error-600 dark:text-error-400">
          {err}
        </p>
      )}
    </>
  );
  return { busy, run, status };
}

function QvantForm({ user, reload }: { user: StaffUser; reload: () => void }) {
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
      <p className="text-theme-sm font-medium text-gray-700 dark:text-gray-300">
        Qvant tuzatish{" "}
        <span className="font-normal text-gray-400">
          (balans: {user.qvant_balance ?? 0})
        </span>
      </p>
      <div className="flex gap-2">
        <input
          name="amount"
          type="number"
          required
          step={1}
          placeholder="±miqdor"
          className={`${INPUT} w-28`}
        />
        <input
          name="note"
          required
          maxLength={200}
          placeholder="Izoh (ledgerga yoziladi)"
          className={INPUT}
        />
        <Button type="submit" className="h-10 shrink-0" disabled={busy}>
          {"Qo'llash"}
        </Button>
      </div>
      {status}
    </form>
  );
}

function NotifyForm({ user }: { user: StaffUser }) {
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
      <p className="text-theme-sm font-medium text-gray-700 dark:text-gray-300">
        Bildirishnoma
      </p>
      <input
        name="title"
        required
        maxLength={200}
        placeholder="Sarlavha"
        className={INPUT}
      />
      <textarea
        name="body"
        rows={2}
        placeholder="Matn"
        className={`${INPUT} h-auto py-2`}
      />
      <Button type="submit" variant="outline" className="h-10" disabled={busy}>
        Yuborish
      </Button>
      {status}
    </form>
  );
}

function BroadcastForm() {
  const { busy, run, status } = useAction();

  function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    const title = String(data.get("title") ?? "");
    if (
      !window.confirm(`«${title}» BARCHA faol foydalanuvchilarga yuborilsinmi?`)
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
    <Card title="Umumiy e'lon" bodyClassName="p-5">
      <form
        onSubmit={submit}
        className="grid gap-2 md:grid-cols-[1fr_2fr_auto]"
      >
        <input
          name="title"
          required
          maxLength={200}
          placeholder="Sarlavha"
          className={INPUT}
        />
        <input name="body" placeholder="Matn (ixtiyoriy)" className={INPUT} />
        <Button type="submit" className="h-10" disabled={busy}>
          Hammaga yuborish
        </Button>
        <div className="md:col-span-3">{status}</div>
      </form>
    </Card>
  );
}

export function UsersAdmin() {
  return (
    <div className="space-y-4">
      <BroadcastForm />
      <CrudPage<StaffUser>
        title="Foydalanuvchilar"
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
