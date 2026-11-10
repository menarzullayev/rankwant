"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

import { useConfirm } from "@/components/overlay/OverlayHost";
import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Checkbox } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t, type MessageKey } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import {
  VIDEO_ACCEPT,
  VIDEO_HEIGHTS,
  studioVideos,
  uploadVideo,
  type StudioVideo,
} from "../api/courses";

type Videos = { videos: StudioVideo[]; reload: () => Promise<void> };

const VideosContext = createContext<Videos>({ videos: [], reload: async () => {} });

/** The course's videos, shared by the panel and every lesson's picker. */
export function useCourseVideos(): Videos {
  return useContext(VideosContext);
}

const STATUS: Record<string, { key: MessageKey; color: BadgeColor }> = {
  uploading: { key: "studio.video.status.uploading", color: "info" },
  queued: { key: "studio.video.status.queued", color: "neutral" },
  processing: { key: "studio.video.status.processing", color: "warning" },
  ready: { key: "studio.video.status.ready", color: "success" },
  failed: { key: "studio.video.status.failed", color: "error" },
};

/** While anything is queued or encoding, the list is re-read this often. */
const POLL_MS = 5000;

export const minutes = (seconds: number) =>
  `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;

export function CourseVideosProvider({ slug, children }: { slug: string; children: React.ReactNode }) {
  const [videos, setVideos] = useState<StudioVideo[]>([]);
  const reload = useCallback(async () => {
    try {
      setVideos(await studioVideos.list(slug));
    } catch {
      // Storage not configured or a network hiccup: the panel says so.
    }
  }, [slug]);
  useEffect(() => {
    // The list lives on the server: read it once the editor mounts.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void reload();
  }, [reload]);
  const busy = videos.some((v) => v.status === "queued" || v.status === "processing");
  useEffect(() => {
    if (!busy) return;
    const timer = window.setInterval(() => void reload(), POLL_MS);
    return () => window.clearInterval(timer);
  }, [busy, reload]);
  return <VideosContext.Provider value={{ videos, reload }}>{children}</VideosContext.Provider>;
}

/** Upload a video file (encoded here) or a zip of a ready HLS, straight to
 *  the bucket; then watch it go from queued to ready. */
export function CourseVideos({ slug }: { slug: string }) {
  const locale = useLocale();
  const confirm = useConfirm();
  const { videos, reload } = useCourseVideos();
  const [file, setFile] = useState<File | null>(null);
  const [heights, setHeights] = useState<number[]>([...VIDEO_HEIGHTS]);
  const [share, setShare] = useState<number | null>(null);
  const [error, setError] = useState("");

  const toggle = (height: number) =>
    setHeights((old) => (old.includes(height) ? old.filter((h) => h !== height) : [...old, height].sort((a, b) => a - b)));

  async function upload() {
    if (!file) return;
    setError("");
    setShare(0);
    try {
      await uploadVideo(slug, file, heights, setShare);
      setFile(null);
      await reload();
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code) : t(locale, "studio.video.uploadFailed"));
    } finally {
      setShare(null);
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-theme-sm rw-dim">{t(locale, "studio.video.intro")}</p>
      {videos.length > 0 && (
        <ul className="divide-y rw-divide rw-radius border rw-line">
          {videos.map((video) => {
            const status = STATUS[video.status] ?? STATUS.queued;
            return (
              <li key={video.id} className="flex flex-wrap items-center gap-3 px-3 py-2 text-theme-sm">
                <span className="font-mono text-theme-xs rw-dim">{video.key}</span>
                {status && <Badge color={status.color}>{t(locale, status.key)}</Badge>}
                {video.heights.length > 0 && (
                  <span className="rw-dim">{video.heights.map((h) => `${h}p`).join(" · ")}</span>
                )}
                {video.seconds > 0 && <span className="rw-dim">{minutes(video.seconds)}</span>}
                {video.used && <span className="rw-accent-ink">{t(locale, "studio.video.used")}</span>}
                {video.error && <span className="w-full text-theme-xs rw-bad-ink">{video.error}</span>}
                {!video.used && (
                  <Button
                    type="button"
                    variant="outline"
                    className="ml-auto"
                    onClick={() =>
                      void (async () => {
                        const ok = await confirm(t(locale, "studio.video.deleteConfirm"), { danger: true });
                        if (!ok) return;
                        try {
                          await studioVideos.remove(slug, video.id);
                          await reload();
                        } catch (err) {
                          setError(err instanceof ApiError ? errorText(locale, err.code) : String(err));
                        }
                      })()
                    }
                  >
                    {t(locale, "studio.video.delete")}
                  </Button>
                )}
              </li>
            );
          })}
        </ul>
      )}
      <div className="space-y-3 rw-radius border border-dashed rw-line p-4">
        <label className="block">
          <span className="mb-1 block text-theme-sm font-medium rw-strong">{t(locale, "studio.video.file")}</span>
          <input
            type="file"
            accept={VIDEO_ACCEPT}
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            className="block w-full text-theme-sm rw-dim"
          />
          <span className="mt-1 block text-theme-xs rw-faint">{t(locale, "studio.video.fileHint")}</span>
        </label>
        <fieldset className="space-y-1">
          <legend className="text-theme-sm font-medium rw-strong">{t(locale, "studio.video.heights")}</legend>
          <p className="text-theme-xs rw-faint">{t(locale, "studio.video.heightsHint")}</p>
          <div className="flex flex-wrap gap-x-4">
            {VIDEO_HEIGHTS.map((height) => (
              <Checkbox key={height} checked={heights.includes(height)} onChange={() => toggle(height)}>
                {`${height}p`}
              </Checkbox>
            ))}
          </div>
        </fieldset>
        {share !== null && (
          <div
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.round(share * 100)}
            aria-label={t(locale, "studio.video.uploading")}
            className="h-2 overflow-hidden rounded-full rw-chip"
          >
            <div className="h-full rounded-full rw-accent-bg" style={{ width: `${Math.round(share * 100)}%` }} />
          </div>
        )}
        {share !== null && (
          <p className="text-theme-xs rw-dim">
            {fill(t(locale, "studio.video.progress"), { percent: Math.round(share * 100) })}
          </p>
        )}
        {error && (
          <p role="alert" className="text-theme-sm rw-bad-ink">
            {error}
          </p>
        )}
        <Button type="button" busy={share !== null} disabled={!file || heights.length === 0} onClick={() => void upload()}>
          {t(locale, "studio.video.upload")}
        </Button>
      </div>
    </div>
  );
}
