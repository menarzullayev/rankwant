import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api } from "@/lib/api";

/** Ijtimoiy dalil (12-qaror).
 *
 * Statistika YIQILSA blok BUTUNLAY yo'qoladi — bo'sh satr yoki `0` emas.
 * Sabab: `0 ta dasturchi bellashadi` — bu ijtimoiy dalil emas, uning
 * aksi. Kirish sahifasi esa API holatiga bog'liq bo'lmasligi kerak.
 *
 * ⚠️ HUQUQIY HAVOLALAR BU YERDA YO'Q — ataylab.
 * Ular allaqachon ikki joyda bor va `/login` da ikkalasi ham ko'rinadi:
 *
 *  1. `AppFooter` — saytning HAR sahifasida (ADR-0016: Google OAuth
 *     tasdig'i maxfiylik siyosatini topib bo'ladigan joyda kutadi).
 *  2. `AuthForm` dagi `Legal()` — «ro'yxatdan o'tish bilan ... shartlarga
 *     rozilik bildirasiz» matni ICHIDA, ya'ni huquqiy jihatdan aynan
 *     rozilik bildiriladigan joyda.
 *
 * Ilgari bu komponent ularni UCHINCHI marta chizardi va `Terms`/
 * `Privacy` havolalari tab tartibida ikki marta chiqardi (o'lchandi:
 * `termsCount: 4`). Takroriy havola — shovqin, ekran o'quvchi uchun esa
 * bir xil nishonning ikki nusxasi.
 */
export async function AuthProof() {
  const locale = await getLocale();
  const stats = await api.stats().catch(() => null);

  // Statistika yo'q yoki nol — ko'rsatadigan narsa yo'q.
  if (!stats || stats.users <= 0) return null;

  return (
    <p className="mt-5 border-t rw-divider pt-4 text-center text-theme-xs rw-dim">
      {t(locale, "auth.socialProof").replace("{count}", stats.users.toLocaleString(locale))}
    </p>
  );
}
