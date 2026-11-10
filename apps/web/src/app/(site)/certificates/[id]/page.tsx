import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { cache } from "react";

import { CertificateCard } from "@/features/profile/server";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { CourseCertificateView, type CourseCertificate } from "@/features/courses";
import { ApiError, type Certificate } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { formatDate } from "@rankwant/shared/format";
import { Status } from "@/components/ui/Status";

type Props = { params: Promise<{ id: string }> };

export const dynamic = "force-dynamic";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

/** QR shu sahifaga olib keladi: sertifikat haqiqiyligi va egasi. A course
 *  certificate (ADR-0056) shares the address: one place to verify. */
type Loaded = { kind: "contest"; cert: Certificate } | { kind: "course"; cert: CourseCertificate };

async function tryGet<T>(path: string): Promise<T | null> {
  try {
    return await getWithSession<T>(path);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

const load = cache(async (id: string): Promise<Loaded | null> => {
  if (!UUID.test(id)) return null;
  const contest = await tryGet<Certificate>(`/certificates/${id}/`);
  if (contest) return { kind: "contest", cert: contest };
  const course = await tryGet<CourseCertificate>(`/courses/certificates/${id}/`);
  return course ? { kind: "course", cert: course } : null;
});

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const found = await load((await params).id);
  return { title: found ? `${t(await getLocale(), "cert.title")} — ${found.cert.name}` : "404" };
}

export default async function CertificatePage({ params }: Props) {
  const found = await load((await params).id);
  if (!found) notFound();
  const locale = await getLocale();
  if (found.kind === "course") return <CourseCertificateView cert={found.cert} locale={locale} />;
  const cert = found.cert;

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
