"use client";

import { useEffect, useRef, useState } from "react";

import { ButtonLink } from "@/components/ui/Button";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { fetchMe } from "@/lib/api";
import { loginHref } from "@/lib/access";
import { UNAUTHORIZED_EVENT } from "@/lib/api/client";

/** How long the notice is read before the page moves on. */
const LEAVE_AFTER_MS = 5000;

/** A session that ended while the page was open (ADR-0054, decision 8).
 *
 *  The API client announces every 401. For a guest that is ordinary. For
 *  somebody the page believes is signed in, `/me/` is asked once more: one
 *  endpoint answering 401 is not the session ending, and a network error
 *  is not either. Only when `/me/` itself says "nobody" does the notice
 *  appear; a few seconds later the page goes to sign in, and back here
 *  afterwards. What was typed in the editor is a draft in this browser and
 *  is still there on return.
 */
export function SessionExpired() {
  const { user, clear } = useSession();
  const locale = useLocale();
  const [href, setHref] = useState<string | null>(null);
  const checking = useRef(false);
  const signedIn = user !== null;

  useEffect(() => {
    if (!signedIn) return;
    const onUnauthorized = () => {
      if (checking.current) return;
      checking.current = true;
      fetchMe()
        .then((me) => {
          if (me !== null) return;
          setHref(loginHref(`${window.location.pathname}${window.location.search}`));
          clear();
        })
        .catch(() => {
          // Offline or the API is down: not a verdict on the session.
        })
        .finally(() => {
          checking.current = false;
        });
    };
    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
  }, [signedIn, clear]);

  useEffect(() => {
    if (href === null) return;
    const timer = window.setTimeout(() => window.location.assign(href), LEAVE_AFTER_MS);
    return () => window.clearTimeout(timer);
  }, [href]);

  if (href === null) return null;
  return (
    <div
      role="alert"
      data-session-expired=""
      className="fixed inset-x-3 top-3 z-[70] mx-auto flex max-w-xl flex-wrap items-center justify-between gap-3 border p-4 rw-radius rw-surface rw-shadow rw-line"
    >
      <p className="min-w-0 text-theme-sm rw-strong">
        <b>{t(locale, "session.expiredTitle")}</b> {t(locale, "session.expiredBody")}
      </p>
      <ButtonLink href={href as never}>{t(locale, "auth.login")}</ButtonLink>
    </div>
  );
}
