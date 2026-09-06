import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = {
  title: {
    default: "RankWant — reyting xohlaganlar uchun",
    template: "%s · RankWant",
  },
  description:
    "Sport dasturlash va informatika olimpiadasi platformasi: masala arxivi, " +
    "musobaqa va ochiq reyting.",
};

const NAV = [
  { href: "/problems", key: "nav.problems" },
  { href: "/contests", key: "nav.contests" },
  { href: "/leaderboard", key: "nav.leaderboard" },
  { href: "/qvant", key: "nav.qvant" },
  { href: "/rating", key: "nav.ratingInfo" },
] as const;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = DEFAULT_LOCALE;
  return (
    <html lang={locale}>
      <body>
        <header className="border-b" style={{ borderColor: "var(--border)" }}>
          <nav className="mx-auto flex max-w-5xl items-center gap-6 px-4 py-4">
            <Link href="/" className="text-lg font-bold">
              Rank<span style={{ color: "var(--accent)" }}>Want</span>
            </Link>
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-sm hover:underline"
                style={{ color: "var(--muted)" }}
              >
                {t(locale, item.key)}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
