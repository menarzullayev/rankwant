import Link from "next/link";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export default async function NotFound() {
  const locale = await getLocale();
  return (
    <div className="py-24 text-center">
      <p className="text-5xl font-bold" style={{ color: "var(--muted)" }}>
        404
      </p>
      <h1 className="mt-4 text-xl font-medium">
        {t(locale, "notFound.title")}
      </h1>
      <p className="mt-2 text-sm" style={{ color: "var(--muted)" }}>
        {t(locale, "notFound.body")}
      </p>
      <Link href="/" className="mt-6 inline-block text-sm underline">
        {t(locale, "notFound.home")}
      </Link>
    </div>
  );
}
