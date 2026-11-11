import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Card } from "@/components/ui/Card";
import { EntryEditor, type EntryDetail } from "@/features/community";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "blogs.editTitle"), robots: { index: false } };
}

/** Only the author edits; for anyone else the page does not exist. */
export default async function EditEntryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const locale = await getLocale();
  let entry: EntryDetail;
  try {
    entry = await getWithSession<EntryDetail>(`/blogs/${encodeURIComponent(id)}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  if (!entry.mine) notFound();
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">{t(locale, "blogs.editTitle")}</h1>
      <Card className="p-5">
        <EntryEditor entry={entry} />
      </Card>
    </div>
  );
}
