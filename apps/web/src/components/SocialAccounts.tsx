"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { GithubMark, GoogleMark } from "@/components/ProviderMark";
import { TelegramButton } from "@/components/TelegramButton";
import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { ApiError, deleteJson, getJson, postJson } from "@/lib/api";

const LABEL = { google: "Google", github: "GitHub", telegram: "Telegram" } as const;
type Provider = keyof typeof LABEL;

/** Kirgan holda ijtimoiy hisobni ulash va uzish.
 *
 * Ilgari bog'lashni FAQAT kirish paytida boshlash mumkin edi va u
 * provayder pochtasi hisob pochtasiga mos kelishini talab qilardi.
 * O'lchangan oqibat: ish pochtasi bilan Google'ga kirgan odam o'z
 * hisobiga ulanish o'rniga yangi hisob ochib olardi va uni qaytarishning
 * yo'li yo'q edi. Bu yerda pochta umuman tekshirilmaydi — odam
 * allaqachon o'z hisobiga kirgan, ya'ni o'zini isbotlagan.
 */
export function SocialAccounts() {
  const locale = useLocale();
  const params = useSearchParams();
  const { user, reload } = useSession();
  const [available, setAvailable] = useState<Provider[]>([]);
  const [bot, setBot] = useState("");
  // Telegram vidjeti FAQAT niyat belgilangach chiziladi: uning
  // callback'i `state` siz GET va niyatsiz bog'lash hisobni
  // egallash yo'li bo'lardi.
  const [tgReady, setTgReady] = useState(false);
  const [busy, setBusy] = useState<Provider | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<{ providers: Provider[]; telegram_bot: string }>("/auth/providers/")
      .then((d) => {
        setAvailable(d.providers);
        setBot(d.telegram_bot);
      })
      .catch(() => setAvailable([]));
  }, []);

  // Qaytish belgisi manzilda keladi: bog'lash provayder sahifasidan
  // o'tadi, ya'ni javobni forma emas, sahifa qabul qiladi.
  const flag = params.get("social");
  const notice =
    flag === "linked"
      ? { tone: "rw-ok-soft rw-ok-ink", text: t(locale, "settings.socialLinked") }
      : flag === "taken"
        ? { tone: "rw-bad-soft rw-bad-ink", text: t(locale, "settings.socialTaken") }
        : null;

  if (!user || available.length === 0) return null;
  const connected = new Set(user.social ?? []);

  async function disconnect(p: Provider) {
    setBusy(p);
    setError("");
    try {
      await deleteJson(`/auth/social/${p}/`);
      await reload();
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 400
          ? t(locale, "settings.socialLast")
          : String(err),
      );
    } finally {
      setBusy(null);
    }
  }

  return (
    <Card title={t(locale, "settings.social")}>
      <p className="text-theme-sm rw-dim">{t(locale, "settings.socialHint")}</p>
      {notice && (
        <p role="status" className={`mt-4 rw-radius-sm px-3 py-2 text-theme-sm ${notice.tone}`}>
          {notice.text}
        </p>
      )}
      {error && (
        <p role="alert" className="mt-4 rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <ul className="mt-4 rw-divide divide-y">
        {available.map((p) => (
          <li key={p} className="flex items-center gap-3 py-3">
            {p === "google" ? <GoogleMark /> : p === "github" ? <GithubMark /> : null}
            <span className="text-theme-sm font-medium rw-strong">{LABEL[p]}</span>
            {connected.has(p) && (
              <span className="rw-radius-sm rw-ok-soft px-2 py-0.5 text-theme-xs rw-ok-ink">
                {t(locale, "settings.socialConnected")}
              </span>
            )}
            <span className="ml-auto">
              {connected.has(p) ? (
                <Button
                  variant="outline"
                  className="h-9 px-3"
                  busy={busy === p}
                  onClick={() => disconnect(p)}
                >
                  {t(locale, "settings.socialDisconnect")}
                </Button>
              ) : p === "telegram" ? (
                tgReady && bot ? (
                  <span className="flex flex-col items-end gap-1">
                    <TelegramButton bot={bot} />
                    <span className="text-theme-xs rw-dim">
                      {t(locale, "settings.socialTelegramStep")}
                    </span>
                  </span>
                ) : (
                  <Button
                    variant="outline"
                    className="h-9 px-3"
                    busy={busy === p}
                    onClick={() => {
                      setBusy(p);
                      setError("");
                      postJson(`/auth/social/${p}/link-start/`, {})
                        .then(() => setTgReady(true))
                        .catch(() => setError(t(locale, "settings.socialTaken")))
                        .finally(() => setBusy(null));
                    }}
                  >
                    {t(locale, "settings.socialConnect")}
                  </Button>
                )
              ) : (
                <a
                  href={`/api/v1/auth/${p}/start/`}
                  className="inline-flex h-9 items-center rw-radius-sm border rw-line px-3 text-theme-sm font-medium rw-strong transition rw-hover-bg rw-focus-ring"
                >
                  {t(locale, "settings.socialConnect")}
                </a>
              )}
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}
