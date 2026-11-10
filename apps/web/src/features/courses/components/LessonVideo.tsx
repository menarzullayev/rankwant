"use client";

import { Icon } from "@/components/ui/Icon";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

import type { LessonDetail } from "../api/courses";

/** Where a hosted video plays. The ref is the provider's video id. */
const WATCH: Record<string, (ref: string) => string> = {
  youtube: (ref) => `https://www.youtube.com/watch?v=${encodeURIComponent(ref)}`,
  vimeo: (ref) => `https://vimeo.com/${encodeURIComponent(ref)}`,
};

/** Part 3 links out; the embedded player (and the signed HLS playlist for
 *  paid courses) comes with the video pipeline, ADR-0056 § 3.6. */
export function LessonVideo({ video }: { video: NonNullable<LessonDetail["video"]> }) {
  const locale = useLocale();
  const watch = video.ref ? WATCH[video.provider] : undefined;
  return (
    <div className="flex aspect-video flex-col items-center justify-center gap-3 rw-radius border rw-line rw-surface p-6 text-center">
      <Icon name="content.video" size="xl" className="size-8 rw-dim" />
      {watch && video.ref ? (
        <a
          href={watch(video.ref)}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex min-h-11 items-center gap-2 rw-radius-sm px-4 text-theme-sm font-medium rw-accent-ink rw-hover-bg rw-focus-ring"
        >
          {t(locale, "course.lesson.videoExternal")}
          <Icon name="nav.external" size="sm" className="size-4" />
          <span className="sr-only">{t(locale, "footer.opensNewTab")}</span>
        </a>
      ) : (
        <p className="text-theme-sm rw-dim">{t(locale, "course.lesson.videoPending")}</p>
      )}
    </div>
  );
}
