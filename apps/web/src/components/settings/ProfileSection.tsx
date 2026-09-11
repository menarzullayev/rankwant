"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { Avatar } from "@/components/Avatar";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field, type FieldStatus } from "@/components/ui/Field";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import {
  deleteJson,
  getJson,
  patchJson,
  postForm,
  postJson,
  type Paginated,
} from "@/lib/api";
import { SLOT_OF } from "@/lib/cosmetics";
import { Hint, Status, TextArea, useAction, useLoad } from "./kit";

const PROVIDERS: Record<string, string> = {
  google: "Google",
  github: "GitHub",
  telegram: "Telegram",
};

/** Markazdan kvadrat qirqib, 256 pikselga kichraytiradi.
 *
 *  Server 1 MB gacha qabul qiladi — telefondagi 4 MB lik suratni
 *  to'g'ridan-to'g'ri yuborish rad etilardi. Safari WebP yoza olmaydi va
 *  `toBlob` jimgina PNG qaytaradi; server turni fayl imzosidan aniqlaydi. */
async function squareAvatar(file: File): Promise<Blob> {
  const bitmap = await createImageBitmap(file);
  const side = Math.min(bitmap.width, bitmap.height);
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("canvas");
  ctx.drawImage(
    bitmap,
    (bitmap.width - side) / 2,
    (bitmap.height - side) / 2,
    side,
    side,
    0,
    0,
    256,
    256,
  );
  bitmap.close();
  const blob = await new Promise<Blob | null>((resolve) =>
    canvas.toBlob(resolve, "image/webp", 0.9),
  );
  if (!blob) throw new Error("encode");
  return blob;
}

function AvatarCard() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const input = useRef<HTMLInputElement>(null);
  const action = useAction();
  if (!user) return null;
  const linked = user.social.filter((p) => p in PROVIDERS);

  async function upload(file: File) {
    let blob: Blob;
    try {
      blob = await squareAvatar(file);
    } catch {
      action.setError(t(locale, "settings.avatarBad"));
      return;
    }
    const form = new FormData();
    form.append("file", blob, blob.type === "image/png" ? "a.png" : "a.webp");
    await action.run(async () => {
      await postForm("/me/avatar/", form);
      await reload();
    });
  }

  return (
    <Card title={t(locale, "settings.avatar")}>
      <div className="flex flex-wrap items-center gap-5">
        <Avatar
          url={user.avatar_url}
          name={user.display_name || user.username}
          className="size-20 text-title-sm"
        />
        <div className="min-w-0 flex-1 space-y-3">
          <Hint>{t(locale, "settings.avatarHint")}</Hint>
          <div className="flex flex-wrap gap-2">
            <input
              ref={input}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="sr-only"
              tabIndex={-1}
              aria-hidden="true"
              onChange={(event) => {
                const file = event.target.files?.[0];
                event.target.value = "";
                if (file) void upload(file);
              }}
            />
            <Button busy={action.busy} onClick={() => input.current?.click()}>
              {t(locale, "settings.avatarUpload")}
            </Button>
            {linked.map((provider) => (
              <Button
                key={provider}
                variant="outline"
                disabled={action.busy}
                onClick={() =>
                  action.run(async () => {
                    await postJson("/me/avatar/import/", { provider });
                    await reload();
                  })
                }
              >
                {fill(t(locale, "settings.avatarImport"), {
                  provider: PROVIDERS[provider],
                })}
              </Button>
            ))}
            {user.avatar_url && (
              <Button
                variant="outline"
                disabled={action.busy}
                onClick={() =>
                  action.run(async () => {
                    await deleteJson("/me/avatar/");
                    await reload();
                  })
                }
              >
                {t(locale, "settings.avatarRemove")}
              </Button>
            )}
          </div>
          <Status error={action.error} done={action.done} />
        </div>
      </div>
    </Card>
  );
}

function AboutCard() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  if (!user) return null;

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await action.run(async () => {
      await patchJson("/me/", {
        display_name: String(form.get("display_name") ?? "").trim(),
        bio: String(form.get("bio") ?? "").trim(),
      });
      await reload();
    });
  }

  return (
    <Card title={t(locale, "settings.nav.profile")}>
      <form onSubmit={save} className="flex flex-col gap-4">
        <Field
          label={t(locale, "auth.displayName")}
          name="display_name"
          defaultValue={user.display_name}
          maxLength={100}
          autoComplete="name"
        />
        <TextArea
          label={t(locale, "settings.bio")}
          hint={t(locale, "settings.bioHint")}
          name="bio"
          defaultValue={user.bio}
          maxLength={500}
          rows={4}
        />
        <Status error={action.error} done={action.done} />
        <Button type="submit" busy={action.busy} className="self-start">
          {t(locale, "settings.save")}
        </Button>
      </form>
    </Card>
  );
}

type Check = { name: string; ok: boolean; reason: string };

function UsernameCard() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  const [name, setName] = useState("");
  const [check, setCheck] = useState<Check | null>(null);
  const value = name.trim();
  const current = user?.username ?? "";

  // Javoblar tartibsiz kelishi mumkin — eskisini bekor qilamiz, aks
  // holda oxirgi yozilgan nomga oldingi nomning javobi yopishardi.
  useEffect(() => {
    if (!value || value === current) return;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      getJson<{ available: boolean; reason: string }>(
        `/auth/username-check/?u=${encodeURIComponent(value)}`,
        { signal: controller.signal },
      )
        .then((r) => setCheck({ name: value, ok: r.available, reason: r.reason }))
        .catch(() => {});
    }, 350);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [value, current]);

  if (!user) return null;
  const { free_at: freeAt, price } = user.username_change;
  const checked = check?.name === value ? check : null;
  const status: FieldStatus | undefined =
    !value || value === user.username
      ? undefined
      : !checked
        ? { kind: "busy", text: t(locale, "auth.checking") }
        : checked.ok
          ? { kind: "ok", text: t(locale, "auth.usernameFree") }
          : { kind: "bad", text: checked.reason };

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!window.confirm(fill(t(locale, "settings.usernameConfirm"), { name: value })))
      return;
    const ok = await action.run(async () => {
      await postJson("/me/username/", { username: value, pay: Boolean(freeAt) });
      await reload();
    });
    if (ok) setName("");
  }

  return (
    <Card title={t(locale, "settings.username")}>
      <p className="text-theme-sm font-medium rw-strong">@{user.username}</p>
      <div className="mt-1">
        <Hint>
          {freeAt
            ? fill(t(locale, "settings.usernameNextFree"), {
                date: new Date(freeAt).toLocaleDateString(locale),
                price,
              })
            : t(locale, "settings.usernameFree")}
        </Hint>
      </div>
      <form onSubmit={submit} className="mt-4 flex flex-col gap-4">
        <Field
          label={t(locale, "settings.usernameNew")}
          name="username"
          value={name}
          onChange={(event) => setName(event.target.value)}
          hint={t(locale, "auth.usernameHint")}
          status={status}
          autoComplete="off"
          spellCheck={false}
          maxLength={30}
        />
        <Hint>{t(locale, "settings.usernameKept")}</Hint>
        <Status
          error={action.error}
          done={action.done}
          text={t(locale, "settings.usernameDone")}
        />
        <Button
          type="submit"
          busy={action.busy}
          disabled={!checked?.ok}
          className="self-start"
        >
          {freeAt
            ? fill(t(locale, "settings.usernamePay"), { price })
            : t(locale, "settings.usernameChange")}
        </Button>
      </form>
    </Card>
  );
}

type InventoryEntry = {
  id: number;
  is_equipped: boolean;
  item: { code: string; category: string; title_uz: string };
};

function CosmeticsCard() {
  const locale = useLocale();
  const inventory = useLoad<InventoryEntry[] | Paginated<InventoryEntry>>(
    "/qvant/inventory/",
  );
  const action = useAction();
  const rows = inventory.data
    ? Array.isArray(inventory.data)
      ? inventory.data
      : inventory.data.results
    : [];
  const wearable = rows.filter((row) => row.item.category in SLOT_OF);

  return (
    <Card title={t(locale, "settings.cosmetics")}>
      <Hint>{t(locale, "settings.cosmeticsHint")}</Hint>
      {inventory.data && wearable.length === 0 && (
        <p className="mt-3 text-theme-sm rw-dim">
          {t(locale, "settings.cosmeticsEmpty")}{" "}
          <Link href="/qvant" className="rw-accent-ink hover:underline">
            {t(locale, "settings.cosmeticsShop")}
          </Link>
        </p>
      )}
      <ul className="mt-4 grid gap-3 sm:grid-cols-2">
        {wearable.map((entry) => (
          <li
            key={entry.id}
            className="flex items-center justify-between gap-3 rw-radius border rw-line px-4 py-3"
          >
            <span className="min-w-0">
              <span className="block truncate text-theme-sm font-medium rw-strong">
                {entry.item.title_uz}
              </span>
              <span className="text-theme-xs rw-faint">
                {t(locale, `settings.slot.${SLOT_OF[entry.item.category]}`)}
              </span>
            </span>
            <Button
              variant={entry.is_equipped ? "outline" : "primary"}
              className="h-9 px-3"
              disabled={action.busy}
              aria-pressed={entry.is_equipped}
              onClick={() =>
                action.run(async () => {
                  await postJson(
                    `/qvant/inventory/${entry.id}/${entry.is_equipped ? "unequip" : "equip"}/`,
                    {},
                  );
                  inventory.reload();
                })
              }
            >
              {entry.is_equipped
                ? t(locale, "settings.takeOff")
                : t(locale, "settings.wear")}
            </Button>
          </li>
        ))}
      </ul>
      <div className="mt-3">
        <Status error={action.error || inventory.error} />
      </div>
    </Card>
  );
}

export function ProfileSection() {
  return (
    <>
      <AvatarCard />
      <AboutCard />
      <UsernameCard />
      <CosmeticsCard />
    </>
  );
}
