"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";

/** Buy one day of streak freeze with Qvant: the shop's own purchase. */
export function FreezeButton({ code, price }: { code: string; price: number }) {
  const locale = useLocale();
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function buy() {
    setBusy(true);
    setError("");
    try {
      await postJson("/qvant/shop/purchase/", { item: code });
      router.refresh();
    } catch (caught) {
      setError(caught instanceof ApiError ? errorText(locale, caught.code, caught.message) : String(caught));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-2">
      <Button busy={busy} onClick={() => void buy()}>
        {fill(t(locale, "streak.buyFreeze"), { price })}
      </Button>
      {error && (
        <p role="alert" className="text-theme-xs rw-bad-ink">
          {error}
        </p>
      )}
    </div>
  );
}
