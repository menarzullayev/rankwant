import type { Metadata } from "next";

import { RoadmapCommentsAdmin } from "@/components/admin/RoadmapCommentsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Yo'l xaritasi izohlari" };

export default function AdminRoadmapCommentsPage() {
  return <RoadmapCommentsAdmin />;
}
