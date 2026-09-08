"use client";

import { Badge } from "@/components/ui/Badge";
import { useHideTags } from "@/lib/hideTags";

export function TopicBadges({
  topics,
  solved,
}: {
  topics: string[];
  solved: boolean;
}) {
  const [hidden] = useHideTags();

  if (topics.length === 0) return null;
  // Yechilgan masalada teg spoyler emas — u yerda doim ko'rinadi.
  if (hidden && !solved) return null;

  return (
    <div className="mt-1 flex flex-wrap gap-1">
      {topics.map((topic) => (
        <Badge key={topic}>{topic}</Badge>
      ))}
    </div>
  );
}
