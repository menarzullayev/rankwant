"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";
import { safeNext } from "@/lib/site";
import { OtpInput } from "./OtpInput";

/** Seconds before "send again" opens. The mail was just sent when the page
 *  opens; asking for another at once only burns the hourly quota. */
const COOLDOWN = 30;

const clock = (seconds: number) =>
  `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;

/** Confirm the e-mail: by the link in the mail, or by its six-digit code.
 *
 *  The link opens in whatever browser the mail app picks, often on ANOTHER
 *  device with no session, so the link path asks for no sign-in. The code path
 *  is for the same device: only the six digits are typed (the handle comes
 *  from the session). Someone who is signed out is asked to sign in first. */
export function EmailVerify() {
  const locale = useLocale();
  const router = useRouter();
  const params = useSearchParams();
  const { user, reload } = useSession();
  const token = params.get("token") ?? "";
  const next = safeNext(params.get("next"));
  const [state, setState] = useState<"idle" | "busy" | "ok" | "fail">(token ? "busy" : "idle");
  const [code, setCode] = useState("");
  const [cooldown, setCooldown] = useState(COOLDOWN);
  const [resend, setResend] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [retryAfter, setRetryAfter] = useState(0);

  // The link path. The initial state is already `busy`, so nothing is set
  // synchronously here — the result is written only after the request.
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

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setTimeout(() => setCooldown((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);

  async function submit(digits: string) {
    setState("busy");
    try {
      await postJson("/auth/email/verify/", { code: digits });
      await reload();
      setState("ok");
    } catch {
      setState("fail");
      setCode("");
    }
  }

  async function send() {
    setResend("sending");
    setRetryAfter(0);
    try {
      await postJson("/auth/email/resend/", {});
      setResend("sent");
      setCooldown(COOLDOWN);
    } catch (err) {
      setRetryAfter(err instanceof ApiError ? err.retryAfter : 0);
      setResend("error");
    }
  }

  if (state === "ok" || (!token && user?.email_verified === true)) {
    return (
      <div className="flex flex-col gap-4">
        <Status status="ok" variant="alert" live label={t(locale, "auth.verifyOk")} />
        <Button type="button" onClick={() => router.push((next ?? "/") as Route)}>
          {t(locale, "auth.verifyContinue")}
        </Button>
      </div>
    );
  }

  // A link that failed: the code below is still a way in, for a signed-in person.
  if (!token && !user) {
    return (
      <div className="flex flex-col gap-4">
        <p className="text-theme-sm rw-dim">{t(locale, "auth.verifySignIn")}</p>
        <Link
          href={`/login?tab=login&next=${encodeURIComponent("/verify-email")}` as Route}
          className="flex h-11 items-center justify-center rw-radius-sm rw-accent-bg text-theme-sm font-medium rw-accent-fg rw-focus-ring"
        >
          {t(locale, "auth.login")}
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {token && state === "busy" ? null : (
        <p className="text-theme-sm rw-dim">
          {t(locale, "auth.verifySentTo").replace("{email}", user?.email ?? "")}
        </p>
      )}
      {state === "fail" && (
        <Status status="bad" variant="alert" alert label={t(locale, token ? "auth.verifyFail" : "auth.verifyCodeFail")} />
      )}
      <OtpInput
        label={t(locale, "auth.verifyCodeLabel")}
        value={code}
        onChange={(value) => {
          setCode(value);
          if (state === "fail") setState("idle");
        }}
        onComplete={(digits) => void submit(digits)}
        invalid={state === "fail"}
        disabled={state === "busy"}
      />
      {resend === "sent" && (
        <Status status="ok" variant="alert" live label={t(locale, "auth.verifySent")} />
      )}
      {resend === "error" && (
        <Status
          status="bad"
          variant="alert"
          alert
          label={`${t(locale, "auth.verifyResendFail")}${
            retryAfter > 0
              ? ` ${t(locale, "auth.throttledWait").replace("{seconds}", String(retryAfter))}`
              : ""
          }`}
        />
      )}
      <Button
        type="button"
        onClick={() => void send()}
        disabled={cooldown > 0 || resend === "sending"}
        busy={resend === "sending"}
        busyLabel={t(locale, "auth.verifySending")}
      >
        {cooldown > 0
          ? t(locale, "auth.verifyResendIn").replace("{time}", clock(cooldown))
          : t(locale, "auth.verifyResend")}
      </Button>
    </div>
  );
}
