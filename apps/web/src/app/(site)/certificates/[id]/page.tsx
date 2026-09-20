import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { cache } from "react";

import { CertificateCard } from "@/components/profile/CertificatesTab";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { ApiError, type Certificate } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { formatDate } from "@/lib/format";
import { Status } from "@/components/ui/Status";

type Props = { params: Promise<{ id: string }> };

export const dynamic = "force-dynamic";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

/** QR shu sahifaga olib keladi: sertifikat haqiqiyligi va egasi. */
const load = cache(async (id: string): Promise<Certificate | null> => {
  if (!UUID.test(id)) return null;
  try {
    return await getWithSession<Certificate>(`/certificates/${id}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
});

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const cert = await load((await params).id);
  return { title: cert ? `${t(await getLocale(), "cert.title")} — ${cert.name}` : "404" };
}

export default async function CertificatePage({ params }: Props) {
  const cert = await load((await params).id);
  if (!cert) notFound();
  const locale = await getLocale();

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">{t(locale, "cert.title")}</h1>
      <Status status="ok" variant="alert" live label={t(locale, "cert.valid")} />
      <CertificateCard cert={cert} locale={locale} withName />
      <dl className="grid gap-3 text-theme-sm sm:grid-cols-2">
        <div>
          <dt className="text-theme-xs rw-faint">{t(locale, "cert.holder")}</dt>
          <dd>
            <Link href={`/users/${cert.username}` as Route} className="rw-accent-ink hover:underline">
              @{cert.username}
            </Link>
          </dd>
        </div>
        <div>
          <dt className="text-theme-xs rw-faint">{t(locale, "cert.issued")}</dt>
          <dd className="rw-strong">{formatDate(cert.issued_at, locale)}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-theme-xs rw-faint">{t(locale, "cert.id")}</dt>
          <dd className="break-all font-mono text-theme-xs rw-strong">{cert.id}</dd>
        </div>
      </dl>
    </div>
  );
}
