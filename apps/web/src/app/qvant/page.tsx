import type { Metadata } from "next";

import { Badge } from "@/components/ui/Badge";
import { Card, StatCard } from "@/components/ui/Card";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { CheckIcon, QvantIcon } from "@/icons";
import {
  api,
  ApiError,
  type Quest,
  type ShopItem,
  type Wallet,
} from "@/lib/api";

export const metadata: Metadata = { title: "Qvant" };

// Balans va questlar shaxsiy — keshlanmaydi.
export const dynamic = "force-dynamic";

export default async function QvantPage() {
  const locale = DEFAULT_LOCALE;

  let wallet: Wallet | null = null;
  let quests: Quest[] = [];
  let shop: ShopItem[] = [];
  try {
    [wallet, quests, shop] = await Promise.all([
      api.wallet(),
      api.quests(),
      api.shop(),
    ]);
  } catch (error) {
    // Kirmagan foydalanuvchi hamyonni ko'ra olmaydi — do'kon ochiq qoladi.
    if (
      !(error instanceof ApiError) ||
      (error.status !== 401 && error.status !== 403)
    ) {
      throw error;
    }
    shop = await api.shop();
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "qvant.title")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">
          Vazifalarni bajarib Qvant to&apos;plang. Qvant reytingga ta&apos;sir
          qilmaydi — u faqat do&apos;kon uchun.
        </p>
      </header>

      {wallet ? (
        <section className="grid gap-4 sm:grid-cols-3">
          <StatCard
            label={t(locale, "qvant.balance")}
            value={wallet.balance}
            icon={<QvantIcon />}
          />
          <StatCard
            label={t(locale, "qvant.today")}
            value={wallet.earned_today}
          />
          <StatCard
            label={t(locale, "qvant.remaining")}
            value={wallet.remaining_today}
          />
        </section>
      ) : (
        <Card>
          <p className="text-theme-sm rw-dim">
            Balansni ko&apos;rish uchun tizimga kiring.
          </p>
        </Card>
      )}

      {quests.length > 0 && (
        <Card title={t(locale, "qvant.quests")} bodyClassName="p-0">
          <ul className="divide-y rw-divide">
            {quests.map((quest) => (
              <li
                key={quest.code}
                className="flex items-center gap-3 px-5 py-3"
              >
                <span
                  className={`flex size-6 shrink-0 items-center justify-center rounded-full
 ${quest.done ? "rw-ok-soft rw-ok-ink " : "border rw-line "}`}
                >
                  {quest.done && <CheckIcon className="size-3.5" />}
                </span>
                <span
                  className={`flex-1 text-theme-sm ${
                    quest.done ? "rw-faint line-through" : "rw-strong "
                  }`}
                >
                  {quest.title_uz}
                </span>
                <Badge color={quest.done ? "neutral" : "brand"}>
                  +{quest.reward}
                </Badge>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <Card title={t(locale, "qvant.shop")}>
        <div className="grid gap-3 sm:grid-cols-2">
          {shop.map((item) => (
            <div
              key={item.code}
              className="flex items-center justify-between gap-3 rw-radius border rw-line px-4 py-3"
            >
              <span className="text-theme-sm rw-strong">{item.title_uz}</span>
              <Badge color={item.owned ? "success" : "brand"}>
                {item.owned ? t(locale, "qvant.owned") : `${item.price} Qvant`}
              </Badge>
            </div>
          ))}
        </div>
        {shop.length === 0 && (
          <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>
        )}
      </Card>
    </div>
  );
}
