import Link from "next/link";
import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = { title: "Qanday ishlaydi" };

const STEPS = [
  ["Yeching", "Masala yechasiz — sandbox'da judge tekshiradi, verdict soniyalarda keladi."],
  ["O'lchanadi", "Har AC Skills reytingiga kiradi. Formula ochiq: joriy qiyinlik × kamayuvchi koeffitsient."],
  ["Bellashing", "Musobaqa, Arena, Duel, Chempionat — har biri o'z reytingi yoki jadvali bilan."],
  ["Qvant to'plang", "Kunlik vazifalar va streak Qvant beradi. Qvant reytingga ta'sir qilmaydi — faqat do'kon."],
  ["Sababini ko'ring", "Profilingizda har reyting o'zgarishining sababi yozilgan. Yashirin algoritm yo'q."],
];

export default function AboutPage() {
  const locale = DEFAULT_LOCALE;
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">
        {t(locale, "about.title")}
      </h1>
      <ol className="space-y-4">
        {STEPS.map(([title, body], i) => (
          <li key={title}>
            <Card>
              <div className="flex gap-4">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-brand-50 font-bold text-brand-600 dark:bg-brand-500/12 dark:text-brand-400">
                  {i + 1}
                </span>
                <div>
                  <p className="font-semibold text-gray-800 dark:text-white/90">{title}</p>
                  <p className="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">{body}</p>
                </div>
              </div>
            </Card>
          </li>
        ))}
      </ol>
      <Card title={t(locale, "home.openRating")}>
        <p className="text-theme-sm text-gray-500 dark:text-gray-400">
          To&apos;rtala reytingning formulasi{" "}
          <Link href="/rating" className="font-medium text-brand-500 hover:underline">
            {t(locale, "nav.formulas")}
          </Link>{" "}
          sahifasida. Bu — bizning boshqa platformalardan asosiy farqimiz.
        </p>
      </Card>
    </div>
  );
}
