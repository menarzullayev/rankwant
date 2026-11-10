import type { Route } from "next";
import Link from "next/link";

import { formatDate } from "@rankwant/shared/format";

import { Status } from "@/components/ui/Status";
import { fill, t, type Locale } from "@/i18n/messages";
import { API_BASE } from "@/lib/api/client";

import type { CourseCertificate } from "../api/courses";

/** A course certificate on the shared verification page (`/certificates/<id>`). */
export function CourseCertificateView({ cert, locale }: { cert: CourseCertificate; locale: Locale }) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">{t(locale, "cert.title")}</h1>
      <Status status="ok" variant="alert" live label={t(locale, "cert.valid")} />
      <section className="space-y-2 rw-radius border rw-line rw-surface p-6 text-center">
        <p className="text-theme-xs font-semibold rw-accent-ink">{t(locale, "cert.courseDone")}</p>
        <p className="text-title-sm font-bold rw-strong">{cert.name}</p>
        <p className="text-theme-base rw-dim">{fill(t(locale, "cert.courseOf"), { course: cert.course_title })}</p>
        {cert.final_score !== null && (
          <p className="text-theme-sm rw-dim">{fill(t(locale, "cert.finalScore"), { percent: cert.final_score })}</p>
        )}
      </section>
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
      <a
        href={`${API_BASE}/courses/certificates/${cert.id}/pdf/`}
        className="inline-flex min-h-11 items-center text-theme-sm rw-accent-ink rw-focus-ring"
      >
        {t(locale, "cert.pdf")}
      </a>
    </div>
  );
}
