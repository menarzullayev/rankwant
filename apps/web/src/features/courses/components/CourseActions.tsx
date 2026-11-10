"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { useConfirm } from "@/components/overlay/OverlayHost";
import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api/client";

import { completeLesson, enrollCourse } from "../api/courses";

function useAction(run: () => Promise<unknown>) {
  const locale = useLocale();
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const go = async () => {
    setBusy(true);
    setError("");
    try {
      await run();
      router.refresh();
    } catch (e) {
      setError(e instanceof ApiError ? errorText(locale, e.code, e.message) : String(e));
    } finally {
      setBusy(false);
    }
  };
  return { busy, error, go };
}

/** Free course: one click enrols, the page then re-reads its programme. */
export function EnrollButton({ slug }: { slug: string }) {
  const locale = useLocale();
  const { busy, error, go } = useAction(() => enrollCourse(slug));
  return (
    <div className="space-y-2">
      <Button onClick={go} busy={busy}>
        {t(locale, "course.enroll")}
      </Button>
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
    </div>
  );
}

/** A Qvant course: the reader confirms the price (no refund — owner
 *  decision 2026-11-10), the API takes exactly that price or refuses. */
export function UnlockButton({ slug, price }: { slug: string; price: number }) {
  const locale = useLocale();
  const confirm = useConfirm();
  const { busy, error, go } = useAction(() => enrollCourse(slug, price));
  return (
    <div className="space-y-2">
      <Button
        onClick={() =>
          void (async () => {
            const ok = await confirm(fill(t(locale, "course.unlockConfirm"), { price }), {
              confirmLabel: fill(t(locale, "course.unlock"), { price }),
            });
            if (ok) await go();
          })()
        }
        busy={busy}
      >
        {fill(t(locale, "course.unlock"), { price })}
      </Button>
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
    </div>
  );
}

/** Text and video lessons are finished by the reader; problem and quiz
 *  lessons finish on their own and never show this button. */
export function CompleteButton({ slug, lessonId }: { slug: string; lessonId: number }) {
  const locale = useLocale();
  const { busy, error, go } = useAction(() => completeLesson(slug, lessonId));
  return (
    <div className="space-y-2">
      <Button onClick={go} busy={busy}>
        {t(locale, "course.lesson.complete")}
      </Button>
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
    </div>
  );
}
