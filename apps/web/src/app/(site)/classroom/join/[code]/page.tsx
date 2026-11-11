import type { Metadata } from "next";

import { ClassroomInvite } from "@/features/classroom";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

type Props = { params: Promise<{ code: string }> };

export async function generateMetadata(): Promise<Metadata> {
  // An invite carries a join code: it is never indexed.
  return { title: t(await getLocale(), "classroom.invite.title"), robots: { index: false } };
}

export default async function ClassroomInvitePage({ params }: Props) {
  const { code } = await params;
  return <ClassroomInvite code={code} />;
}
