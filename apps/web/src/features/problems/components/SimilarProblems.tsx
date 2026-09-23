import Link from "next/link";

import { Card } from "@/components/ui/Card";
import { t, type Locale } from "@/i18n/messages";
import type { SimilarProblem } from "@/lib/api";

/** O'xshash masalalar — taqalib qolganda keyingi qadam.
 *
 * Ro'yxat qidiruv emas: shu masalaning o'zidan kelib chiqadi, ya'ni
 * «shu g'oyani yana bir marta mashq qilaman» degan aniq niyat uchun. */
export function SimilarProblems({
  items,
  locale,
}: {
  items: SimilarProblem[];
  // Server komponentda hook yo'q, shuning uchun `locale` yuqoridan
  // beriladi (`getLocale()` sahifa ichida chaqiriladi). Shu sababli bu
  // komponent KLIENTga aylanmaydi va bundle o'smaydi.
  locale: Locale;
}) {
  if (items.length === 0) return null;

  return (
    <Card title={t(locale, "problem.similar")} bodyClassName="p-0">
      <ul className="rw-divide divide-y">
        {items.map((item) => (
          <li key={item.slug}>
            <Link
              href={`/problems/${item.slug}`}
              className="flex flex-wrap items-center gap-x-3 gap-y-1 px-5 py-2.5 text-theme-sm transition rw-hover-bg"
            >
              <span className="font-medium rw-strong">{item.title}</span>
              <span className={`level-${item.level} text-theme-xs font-medium`}>
                {item.level_label}
              </span>
              <span className="ml-auto rw-faint tabular-nums">
                {Math.round(item.score * 100)}% o&apos;xshash
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </Card>
  );
}
