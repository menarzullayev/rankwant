import Link from "next/link";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

// `as const` shart: typedRoutes yoqilgan, massivdan o'qilgan href
// literal tipini yo'qotsa Link uni qabul qilmaydi.
const CARDS = [
  { href: "/problems", key: "nav.problems" },
  { href: "/contests", key: "nav.contests" },
  { href: "/leaderboard", key: "nav.leaderboard" },
] as const;

export default function Home() {
  const locale = DEFAULT_LOCALE;
  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold">RankWant</h1>
        <p className="mt-2" style={{ color: "var(--muted)" }}>
          Reyting xohlaganlar uchun: masala yeching, musobaqada qatnashing,
          darajangizni ko&apos;ring.
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        {CARDS.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="rounded-lg border p-4 transition hover:border-current"
            style={{ borderColor: "var(--border)", background: "var(--surface)" }}
          >
            <span className="font-medium">{t(locale, card.key)}</span>
          </Link>
        ))}
      </section>

      <section
        className="rounded-lg border p-4"
        style={{ borderColor: "var(--border)", background: "var(--surface)" }}
      >
        <h2 className="font-medium">Reyting yashirin emas</h2>
        <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
          Har bir reytingning formulasi ochiq va har o&apos;zgarishning sababi
          yozib boriladi.{" "}
          <Link href="/rating" className="underline">
            {t(locale, "nav.ratingInfo")}
          </Link>
        </p>
      </section>
    </div>
  );
}
