import Link from "next/link";

import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

/** Kirish sahifasining yagona markazlashgan qobig'i (18-qaror).
 *
 * Ilgari `/login` `AuthLayout` bilan ikki ustunli split-screen edi:
 * chap panelda brend, statistika va yaqin musobaqa turardi. 18-qaror
 * buni bekor qildi — kirish sahifasi BITTA markazlashgan karta bo'lishi
 * kerak.
 *
 * Sabab: split-screen paneli `api.stats()` va `api.contests()` ga
 * bog'liq edi, ya'ni API sekinlashsa yoki yiqilsa CHAP PANEL bo'sh
 * qolardi (kod `catch(() => null)` bilan yashirardi, lekin bo'shliq
 * qolardi). Kirish sahifasi esa hech narsaga bog'liq bo'lmasligi kerak —
 * u eng ko'p yuklanadigan sahifa.
 *
 * Ijtimoiy dalil yo'qolmadi (12-qaror): u endi `AuthProof` ichida
 * kartaning o'zida, kichik satr bo'lib turadi.
 */
export async function AuthShell({ children }: { children: React.ReactNode }) {
  const locale = await getLocale();

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-10">
      <div className="mb-6 text-center">
        <Link href="/" className="inline-block rw-focus-ring rw-radius-sm">
          <p className="text-2xl font-bold">
            Rank<span className="rw-accent-ink">Want</span>
          </p>
        </Link>
        <p className="mt-2 text-theme-md rw-dim">{t(locale, "auth.tagline")}</p>
      </div>
      {children}
    </div>
  );
}
