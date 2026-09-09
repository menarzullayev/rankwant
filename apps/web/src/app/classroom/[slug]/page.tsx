import type { Metadata } from "next";

import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

import { ClassroomDetail } from "@/components/ClassroomDetail";

type Props = { params: Promise<{ slug: string }> };
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.classroom") };
}

export default async function ClassroomRoomPage({ params }: Props) {
  const { slug } = await params;
  return <ClassroomDetail slug={slug} />;
}
