import Link from "next/link";

// The root layout carries no stylesheet: each route group imports its own.
// A not-found at the root therefore rendered the whole shell unstyled —
// a 33 000 px page with a native scrollbar (measured 2026-10-06).
import "./globals.css";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export default async function NotFound() {
  const locale = await getLocale();
  return (
    <div className="py-24 text-center">
      <p className="text-5xl font-bold rw-faint">
        404
      </p>
      <h1 className="mt-4 text-xl font-medium rw-strong">
        {t(locale, "notFound.title")}
      </h1>
      <p className="mt-2 text-sm rw-dim">
        {t(locale, "notFound.body")}
      </p>
      <Link href="/" className="mt-6 inline-flex min-h-11 items-center text-sm rw-accent-ink underline">
        {t(locale, "notFound.home")}
      </Link>
    </div>
  );
}
