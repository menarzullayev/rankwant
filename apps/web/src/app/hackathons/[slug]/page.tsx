import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { HackathonEntries } from "@/components/HackathonEntries";
import { Markdown } from "@/components/Markdown";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { dateTime, t } from "@/i18n/messages";
import { api, ApiError } from "@/lib/api";

type Props = { params: Promise<{ slug: string }> };
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    return { title: (await api.hackathon(slug)).title };
  } catch {
    return { title: "404" };
  }
}

export default async function HackathonPage({ params }: Props) {
  const { slug } = await params;
  const locale = await getLocale();
  let h;
  try {
    h = await api.hackathon(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{h.title}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-2 text-theme-xs rw-faint">
          <Badge color={h.accepts_submissions ? "success" : "neutral"}>
            {h.accepts_submissions
              ? t(locale, "contests.running")
              : h.is_finished
                ? t(locale, "contests.finished")
                : t(locale, "contests.upcoming")}
          </Badge>
          <span>
            {t(locale, "hackathon.deadline")}:{" "}
            {dateTime(h.submission_deadline, locale)}
          </span>
        </div>
      </header>
      {h.description && (
        <Card>
          <Markdown>{h.description}</Markdown>
        </Card>
      )}
      <HackathonEntries hackathon={h} />
    </div>
  );
}
