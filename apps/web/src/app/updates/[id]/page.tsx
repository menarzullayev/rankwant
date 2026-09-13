import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Card } from "@/components/ui/Card";
import { Markdown } from "@/components/Markdown";
import {
  UpdateKindBadge,
  UpdateModuleBadge,
} from "@/components/UpdateKindBadge";
import { getLocale } from "@/i18n/server";
import { date, t } from "@/i18n/messages";
import { ApiError, api } from "@/lib/api";

export const dynamic = "force-dynamic";

/** Havola barqaror: `id` hech qachon o'zgarmaydi va yozuv nashrdan
 *  olinganda ham o'chirilmaydi (qaror 20) — Telegram kanal va Codeforces
 *  blogdan kelgan havola sindirilmaydi. */
type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const locale = await getLocale();
  const row = await api.update(Number(id)).catch(() => null);
  if (!row) return { title: t(locale, "update.title") };
  return {
    title: row.title,
    description: row.body.slice(0, 160),
    alternates: { canonical: `/updates/${row.id}` },
  };
}

export default async function UpdatePage({ params }: Props) {
  const { id } = await params;
  const locale = await getLocale();

  const numeric = Number(id);
  // Raqam bo'lmagan yo'l (masalan `/updates/foo`) API ga umuman bormaydi —
  // aks holda 404 o'rniga API xatosi ko'rinardi.
  if (!Number.isInteger(numeric) || numeric <= 0) notFound();

  const row = await api.update(numeric).catch((error: unknown) => {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  });
  if (!row) notFound();

  return (
    <article className="space-y-6">
      <Link
        href={"/updates" as Route}
        className="inline-block text-theme-sm rw-accent-ink hover:underline"
      >
        ← {t(locale, "update.back")}
      </Link>

      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <UpdateKindBadge kind={row.kind} locale={locale} />
          <UpdateModuleBadge module={row.module} locale={locale} />
          {row.version && (
            <span className="text-theme-xs tabular-nums rw-faint">
              {row.version}
            </span>
          )}
        </div>
        <h1 className="text-title-sm font-bold rw-strong">{row.title}</h1>
        <p className="text-theme-sm rw-faint">
          {t(locale, "update.releasedOn")}: {date(row.released_at, locale)}
        </p>
      </header>

      {/* Qaror 20: nashrdan olingan yozuv o'chirilmaydi — havola ishlaydi,
          lekin sahifa buni OSHKOR aytishi kerak. Aks holda qaytarib olingan
          ma'lumot jimgina haqiqiydek o'qilardi. */}
      {row.status === "withdrawn" && (
        <p className="rw-radius border rw-line px-4 py-3 text-theme-sm rw-dim">
          {t(locale, "update.withdrawn")}
        </p>
      )}

      {row.image && (
        // Rasm manzili tashqi (S3) va o'lchami noma'lum — `next/image`
        // `remotePatterns` sozlamasini talab qiladi, skrinshot esa
        // kamdan-kam qo'shiladi. Shu sababli oddiy `<img>`.
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={row.image}
          alt=""
          className="w-full rw-radius border rw-line"
        />
      )}

      {row.body && (
        <Card>
          <Markdown>{row.body}</Markdown>
        </Card>
      )}

      {/* Tarjima hali yo'q bo'lsa API kanonik o'zbekcha matnni qaytaradi —
          buni yashirmaslik kerak, aks holda "tarjima qilinmagan" holat
          foydalanuvchiga o'zbekcha matn sifatida ko'rinadi. */}
      {!row.is_translated && (
        <p className="text-theme-xs rw-faint">{t(locale, "update.originUz")}</p>
      )}

      {row.source_url && (
        <p>
          <a
            href={row.source_url}
            rel="noreferrer noopener"
            target="_blank"
            className="text-theme-sm font-medium rw-accent-ink hover:underline"
          >
            {t(locale, "update.source")} ↗
          </a>
        </p>
      )}
    </article>
  );
}
