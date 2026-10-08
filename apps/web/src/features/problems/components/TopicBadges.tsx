"use client";

import { useHideTags } from "@/lib/hideTags";

/** Ro'yxatdagi mavzular.
 *
 * Badge EMAS, kichik kulrang matn va uchtadan ko'pi yig'iladi. Sabab
 * o'lchandi: masalalarning 20 % ida 4+ mavzu bor va rangli badge'lar
 * qatorni uch qatorga cho'zib, jadvalni notekis qilardi. KEP va
 * RoboContest ro'yxatda mavzuni umuman ko'rsatmaydi; Codeforces —
 * eng katta arxiv — aynan shu yo'lni tanlagan: ko'rinadi, lekin
 * qatorni buzmaydi.
 */
const VISIBLE = 3;

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

  const shown = topics.slice(0, VISIBLE);
  const rest = topics.length - shown.length;

  return (
    <p
      data-topics
      // In a table cell `truncate` alone cannot shorten anything: the
      // unbroken line IS the cell's minimum width. The cap gives it one
      // on a phone (the 320 px archive scrolled 47 px sideways).
      className="mt-0.5 max-w-[56vw] truncate text-theme-xs rw-faint sm:max-w-none"
    >
      {shown.join(" · ")}
      {rest > 0 && (
        <span title={topics.slice(VISIBLE).join(", ")}> +{rest}</span>
      )}
    </p>
  );
}
