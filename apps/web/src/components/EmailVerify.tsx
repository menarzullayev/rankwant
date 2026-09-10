"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { postJson } from "@/lib/api";

/** Havola bo'yicha tasdiqlash, kod esa zaxira yo'l.
 *
 * Havola pochtadan ochiladi va u ko'pincha BOSHQA qurilmadagi brauzer
 * bo'ladi — u yerda sessiya yo'q, shuning uchun sahifa kirishni talab
 * qilmaydi. Kod bilan yo'l ham shu sababdan: telefondagi pochtadan
 * kompyuterga havola o'tmaydi, olti xonali raqam esa o'tadi.
 */
export function EmailVerify() {
  const locale = useLocale();
  const params = useSearchParams();
  const { reload } = useSession();
  const token = params.get("token") ?? "";
  const [state, setState] = useState<"idle" | "busy" | "ok" | "fail">(
    token ? "busy" : "idle",
  );

  async function send(body: Record<string, string>) {
    try {
      await postJson("/auth/email/verify/", body);
      await reload();
      setState("ok");
    } catch {
      setState("fail");
    }
  }

  // Boshlang'ich holat allaqachon `busy`, shuning uchun effekt ichida
  // sinxron hech narsa o'rnatilmaydi — natija faqat so'rovdan KEYIN
  // yoziladi. `alive` esa sahifadan chiqib ketilgan holat uchun.
  useEffect(() => {
    if (!token) return;
    let alive = true;
    postJson("/auth/email/verify/", { token })
      .then(() => reload())
      .then(() => {
        if (alive) setState("ok");
      })
      .catch(() => {
        if (alive) setState("fail");
      });
    return () => {
      alive = false;
    };
  }, [token, reload]);

  if (state === "ok") {
    return (
      <div className="flex flex-col gap-4">
        <p role="status" className="rw-radius-sm rw-ok-soft px-3 py-2 text-theme-sm rw-ok-ink">
          ✓ {t(locale, "auth.verifyOk")}
        </p>
        <Link href="/" className="text-center text-theme-sm rw-accent-ink hover:underline">
          RankWant
        </Link>
      </div>
    );
  }

  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        setState("busy");
        void send({
          username: String(form.get("username") ?? ""),
          code: String(form.get("code") ?? ""),
        });
      }}
    >
      {state === "fail" && (
        <p role="alert" className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink">
          {t(locale, "auth.verifyFail")}
        </p>
      )}
      <Field label={t(locale, "auth.username")} name="username" required autoComplete="username" />
      <Field
        label={t(locale, "auth.verifyTitle")}
        name="code"
        inputMode="numeric"
        pattern="[0-9]{6}"
        maxLength={6}
        required
      />
      <Button type="submit" disabled={state === "busy"}>
        {t(locale, "auth.verifyTitle")}
      </Button>
    </form>
  );
}
