import type { Metadata } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { Card, StatCard } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import {
  api,
  ApiError,
  type Marathon,
  type Quest,
  type ShopItem,
  type Wallet,
} from "@/lib/api";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "qvant.title") };
}

// Balans va questlar shaxsiy — keshlanmaydi.
export const dynamic = "force-dynamic";

export default async function QvantPage() {
  const locale = await getLocale();

  let wallet: Wallet | null = null;
  let quests: Quest[] = [];
  let shop: ShopItem[] = [];
  let marathon: Marathon | null = null;
  try {
    [wallet, quests, shop, marathon] = await Promise.all([
      api.wallet(),
      api.quests(),
      api.shop(),
      api.marathon(),
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
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">{t(locale, "qvant.intro")}
        </p>
      </header>

      {wallet ? (
        <section className="grid gap-4 sm:grid-cols-3">
          <StatCard
            label={t(locale, "qvant.balance")}
            value={wallet.balance}
            icon={<Icon name="shop.coin" />}
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
            {t(locale, "qvant.signIn")}
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
                  {quest.done && <Icon name="action.confirm" className="size-3.5" />}
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

      {marathon && marathon.total > 0 && (
        <Card
          title={t(locale, "qvant.marathon")}
          bodyClassName="p-0"
          action={
            <Badge color={marathon.completed ? "success" : "brand"}>
              {marathon.completed
                ? t(locale, "qvant.marathonFinished")
                : `${marathon.solved_count}/${marathon.total} · +${marathon.reward}`}
            </Badge>
          }
        >
          <p className="px-5 pt-3 text-theme-sm rw-dim">
            Bu to&apos;plam faqat sizniki va hafta oxirigacha o&apos;zgarmaydi.
            Hammasini yeching — +{marathon.reward} Qvant.
          </p>
          <ul className="mt-3 divide-y rw-divide">
            {marathon.problems.map((problem) => (
              <li key={problem.slug}>
                <Link
                  href={`/problems/${problem.slug}`}
                  className="flex items-center gap-3 px-5 py-2.5 transition rw-hover-bg"
                >
                  <span
                    className={`flex size-6 shrink-0 items-center justify-center rounded-full ${
                      problem.marathon_solved
                        ? "rw-ok-soft rw-ok-ink"
                        : "border rw-line"
                    }`}
                  >
                    {problem.marathon_solved && (
                      <Icon name="action.confirm" className="size-3.5" />
                    )}
                  </span>
                  <span
                    className={`flex-1 truncate text-theme-sm ${
                      problem.marathon_solved
                        ? "rw-faint line-through"
                        : "rw-strong"
                    }`}
                  >
                    {problem.title}
                  </span>
                  <span className="shrink-0 text-theme-xs rw-faint tabular-nums">
                    {problem.difficulty}
                  </span>
                </Link>
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
          <p className="text-theme-sm rw-faint">{t(locale, "common.empty")}</p>
        )}
      </Card>
    </div>
  );
}
