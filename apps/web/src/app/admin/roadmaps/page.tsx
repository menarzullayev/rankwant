import type { Metadata } from "next";

import { RoadmapsAdmin } from "@/components/admin/RoadmapsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Traektoriya" };

export default function AdminRoadmapsPage() {
  return <RoadmapsAdmin />;
}
