import type { Metadata } from "next";

import { ClassroomDetail } from "@/components/ClassroomDetail";

type Props = { params: Promise<{ slug: string }> };
export const metadata: Metadata = { title: "Auditoriya" };

export default async function ClassroomRoomPage({ params }: Props) {
  const { slug } = await params;
  return <ClassroomDetail slug={slug} />;
}
