import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { getLocale } from "@/i18n/server";
import { t, dateTime, type Locale } from "@/i18n/messages";
import { api, type Contest } from "@/lib/api";

/** Yaqin musobaqa — hozir ketayotgani ustun, aks holda eng yaqini. */
function pickContest(contests: Contest[]): Contest | null {
  const live = contests.filter((c) => !c.is_finished);
  if (live.length === 0) return null;
  return (
    live.find((c) => c.is_running) ??
    live.sort((a, b) => +new Date(a.start_at) - +new Date(b.start_at))[0]
  );
}

/** Brend bloki — desktop panelda ham, mobil sarlavhada ham bir xil. */
function Brand({ locale }: { locale: Locale }) {
  return (
    <>
      <p className="text-2xl font-bold">
        Rank<span className="rw-accent-ink">Want</span>
      </p>
      <p className="mt-2 text-theme-md rw-dim">{t(locale, "auth.tagline")}</p>
    </>
  );
}

/** Kirish va ro'yxat uchun split-screen qobiq (qaror 10, 11, 12).
 *
 * Chap panel ATAYLAB rasmsiz: platformada 12 ta uslub tizimi bor, ya'ni
 * statik illyustratsiya har uslub × har tema uchun alohida rang moslashini
 * talab qilardi. Buning o'rniga naqsh `--rw-accent` va `--rw-line`
 * tokenlaridan chiziladi — yangi uslub qo'shilganda u o'zi moslashadi.
 *
 * Kontent `justify-center` bilan MARKAZDA turadi, `justify-between` bilan
 * emas. Sabab o'lchandi: musobaqa bo'lmaganda (odatiy hol) `pickContest`
 * `null` qaytaradi, uchta blokdan ikkitasi qoladi va `justify-between`
 * ularni chetga surib, orasida ~880px bo'shliq qoldirardi — panel buzuq
 * ko'rinardi.
 *
 * Panel mobilda yashiriladi (`hidden lg:flex`), lekin brend butunlay
 * yo'qolmaydi: telefonda forma ustida qisqa sarlavha chiqadi.
 */
export async function AuthLayout({ children }: { children: React.ReactNode }) {
  const locale = await getLocale();

  // Statistika va musobaqa MUSTAQIL — ketma-ket kutilsa sahifa
  // sekinlashadi. Ikkalasi yiqilsa ham sahifa ochilishi kerak: kirish
  // panelga bog'liq emas. `api.*` ichida `revalidate` bor (stats 60 s,
  // contests 30 s), ya'ni bu so'rovlar Next keshidan keladi — har
  // yuklanishda API ga bormaydi.
  const [stats, contests] = await Promise.all([
    api.stats().catch(() => null),
    api.contests().catch(() => null),
  ]);
  const soon = contests ? pickContest(contests.results) : null;

  return (
    <div className="grid min-h-[70vh] lg:min-h-[80vh] lg:grid-cols-2">
      <aside className="relative hidden overflow-hidden border-r rw-divider rw-surface lg:flex lg:flex-col lg:justify-center lg:gap-10 lg:p-10">
        {/* Fon naqshi — uslub tokenlaridan, ya'ni har temada to'g'ri.
            MARKAZDA va qirqilmasdan: ilgari `-right-24 -bottom-24` bilan
            chetdan chiqib ketardi va tugallanmagan shaklga o'xshardi. */}
        <svg
          aria-hidden
          className="pointer-events-none absolute top-1/2 left-1/2 size-[560px] -translate-x-1/2 -translate-y-1/2 rw-accent-ink opacity-[0.10]"
          viewBox="0 0 200 200"
          fill="none"
        >
          {[40, 65, 90, 115, 140].map((r) => (
            <circle key={r} cx="100" cy="100" r={r} stroke="currentColor" strokeWidth="1.5" />
          ))}
          <path d="M20 150 L70 95 L110 125 L180 40" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>

        <div className="relative">
          <Brand locale={locale} />
        </div>

        {stats && (
          <dl className="relative grid grid-cols-3 gap-4">
            {(
              [
                [t(locale, "nav.problems"), stats.problems],
                [t(locale, "nav.contests"), stats.contests],
                // `stats.users` — FOYDALANUVCHILAR soni. Ilgari bu yerda
                // `nav.leaderboard` ("Reyting") turardi, ya'ni 10008 kabi
                // raqam reyting balli bo'lib o'qilardi.
                [t(locale, "auth.members"), stats.users],
              ] as const
            ).map(([label, value]) => (
              <div key={label}>
                <dd className="text-title-sm font-bold rw-strong tabular-nums">
                  {value}
                </dd>
                <dt className="mt-0.5 text-theme-xs rw-faint">{label}</dt>
              </div>
            ))}
          </dl>
        )}

        {soon && (
          <Link
            href={{ pathname: `/contests/${soon.slug}` }}
            className="relative block rw-radius border rw-line p-4 transition rw-hover-line"
          >
            <p className="font-mono text-theme-micro uppercase tracking-theme-label rw-faint">
              {t(locale, "home.upcoming")}
            </p>
            <p className="mt-2 truncate font-medium rw-strong">{soon.title}</p>
            <p className="mt-1 flex items-center gap-2 text-theme-xs rw-faint">
              {dateTime(soon.start_at, locale)}
              <Badge color={soon.is_running ? "success" : "info"}>
                {t(
                  locale,
                  soon.is_running ? "contests.running" : "contests.upcoming",
                )}
              </Badge>
            </p>
          </Link>
        )}
      </aside>

      <div className="flex flex-col">
        {/* Telefonda chap panel yo'q, ya'ni kontekst umuman qolmasdi. */}
        <div className="border-b rw-divider rw-surface px-6 py-5 lg:hidden">
          <Brand locale={locale} />
        </div>
        <div className="flex flex-1 items-center justify-center p-6">
          <div className="w-full max-w-md">{children}</div>
        </div>
      </div>
    </div>
  );
}
