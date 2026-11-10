"use client";

import { Icon } from "@/components/ui/Icon";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

import { HlsPlayer } from "./HlsPlayer";

import type { LessonDetail } from "../api/courses";

/** The embed address of a hosted video. The id was checked by the API
 *  (`courses.video.normalise`); it is encoded here all the same, because it
 *  ends up in a frame's address. The hosts are the two `frame-src` allows
 *  (`VIDEO_FRAME_ORIGINS`). */
const EMBED: Record<string, (ref: string) => string> = {
  youtube: (ref) => `https://www.youtube-nocookie.com/embed/${encodeURIComponent(ref)}?rel=0`,
  vimeo: (ref) => `https://player.vimeo.com/video/${encodeURIComponent(ref)}?dnt=1`,
};

/** A free lesson's YouTube or Vimeo player. A paid lesson's video lives on
 *  R2 and plays through a signed address (ADR-0056 § 3.5); until that part
 *  ships, the block says the video is being prepared. */
export function LessonVideo({
  video,
  title,
}: {
  video: NonNullable<LessonDetail["video"]>;
  title: string;
}) {
  const locale = useLocale();
  if (video.provider === "hls" && video.playlist) {
    return <HlsPlayer playlist={video.playlist} title={title} />;
  }
  const embed = video.ref ? EMBED[video.provider] : undefined;
  if (embed && video.ref) {
    return (
      <div className="aspect-video overflow-hidden rw-radius border rw-line bg-black">
        <iframe
          src={embed(video.ref)}
          title={title}
          className="size-full"
          loading="lazy"
          referrerPolicy="strict-origin-when-cross-origin"
          allow="encrypted-media; picture-in-picture; fullscreen"
          allowFullScreen
          // The player may run its own scripts; it may not navigate this
          // page or open forms on it.
          sandbox="allow-scripts allow-same-origin allow-presentation allow-popups"
        />
      </div>
    );
  }
  return (
    <div className="flex aspect-video flex-col items-center justify-center gap-3 rw-radius border rw-line rw-surface p-6 text-center">
      <Icon name="content.video" size="xl" className="size-8 rw-dim" />
      <p className="text-theme-sm rw-dim">{t(locale, "course.lesson.videoPending")}</p>
    </div>
  );
}
