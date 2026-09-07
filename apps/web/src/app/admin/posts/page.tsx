import type { Metadata } from "next";

import { PostsAdmin } from "@/components/admin/PostsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Yangiliklar" };

export default function AdminPostsPage() {
  return <PostsAdmin />;
}
