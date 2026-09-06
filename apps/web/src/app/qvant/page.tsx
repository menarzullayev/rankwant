import type { Metadata } from "next";
import { api, ApiError, type Quest, type ShopItem, type Wallet } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = { title: "Qvant" };

// Balans va questlar shaxsiy — keshlanmaydi.
export const dynamic = "force-dynamic";

const CARD = {
  borderColor: "var(--border)",
  background: "var(--surface)",
} as const;

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border p-4" style={CARD}>
      <p className="text-xs" style={{ color: "var(--muted)" }}>
        {label}
      </p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  );
}

export default async function QvantPage() {
  const locale = DEFAULT_LOCALE;

  let wallet: Wallet | null = null;
  let quests: Quest[] = [];
  let shop: ShopItem[] = [];
  try {
    [wallet, quests, shop] = await Promise.all([api.wallet(), api.quests(), api.shop()]);
  } catch (error) {
    // Kirmagan foydalanuvchi hamyonni ko'ra olmaydi — do'kon ochiq qoladi.
    if (!(error instanceof ApiError) || (error.status !== 401 && error.status !== 403)) {
      throw error;
    }
    shop = await api.shop();
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">{t(locale, "qvant.title")}</h1>
        <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
          Vazifalarni bajarib Qvant to&apos;plang. Qvant reytingga
          ta&apos;sir qilmaydi — u faqat do&apos;kon uchun.
        </p>
      </header>

      {wallet ? (
        <section className="grid gap-4 sm:grid-cols-3">
          <Stat label={t(locale, "qvant.balance")} value={wallet.balance} />
          <Stat label={t(locale, "qvant.today")} value={wallet.earned_today} />
          <Stat label={t(locale, "qvant.remaining")} value={wallet.remaining_today} />
        </section>
      ) : (
        <p style={{ color: "var(--muted)" }}>
          Balansni ko&apos;rish uchun tizimga kiring.
        </p>
      )}

      {quests.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-medium">{t(locale, "qvant.quests")}</h2>
          <ul className="space-y-2">
            {quests.map((quest) => (
              <li
                key={quest.code}
                className="flex items-center justify-between rounded-lg border p-3 text-sm"
                style={CARD}
              >
                <span style={{ color: quest.done ? "var(--muted)" : "var(--text)" }}>
                  {quest.done && "✓ "}
                  {quest.title_uz}
                </span>
                <span style={{ color: quest.done ? "var(--muted)" : "var(--accent)" }}>
                  +{quest.reward}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-medium">{t(locale, "qvant.shop")}</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {shop.map((item) => (
            <div
              key={item.code}
              className="flex items-center justify-between rounded-lg border p-4 text-sm"
              style={CARD}
            >
              <span>{item.title_uz}</span>
              <span style={{ color: item.owned ? "var(--muted)" : "var(--accent)" }}>
                {item.owned ? t(locale, "qvant.owned") : `${item.price} Qvant`}
              </span>
            </div>
          ))}
        </div>
        {shop.length === 0 && (
          <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>
        )}
      </section>
    </div>
  );
}
