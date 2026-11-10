"use client";

import { useEffect, useRef, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { API_BASE } from "@/lib/api/client";

/** Our own encrypted HLS (ADR-0056 § 3.5). Safari plays it natively;
 *  elsewhere hls.js does, loaded only on a page that has such a video. The
 *  key comes from the API with the reader's session, the segments from the
 *  bucket without it. */
export function HlsPlayer({ playlist, title }: { playlist: string; title: string }) {
  const locale = useLocale();
  const video = useRef<HTMLVideoElement>(null);
  const [failed, setFailed] = useState(false);
  const source = `${API_BASE}${playlist}`;

  useEffect(() => {
    const element = video.current;
    if (!element) return;
    let player: { destroy: () => void } | null = null;
    let cancelled = false;
    void import("hls.js").then(({ default: Hls }) => {
      if (cancelled) return;
      // hls.js wherever Media Source works — even where the browser also
      // plays HLS itself (Chrome answers "maybe" since 2025): only hls.js
      // lets the key request carry the session and report a failure.
      // Native playback is the fallback for iOS, which has no MSE.
      if (!Hls.isSupported()) {
        if (element.canPlayType("application/vnd.apple.mpegurl")) element.src = source;
        else setFailed(true);
        return;
      }
      const api = new URL(API_BASE).origin;
      const hls = new Hls({
        xhrSetup: (xhr, url) => {
          // The session goes to our API only; a bucket must not see it.
          xhr.withCredentials = new URL(url, window.location.href).origin === api;
        },
      });
      hls.on(Hls.Events.ERROR, (_event, data) => {
        if (data.fatal) setFailed(true);
      });
      hls.loadSource(source);
      hls.attachMedia(element);
      player = hls;
    });
    return () => {
      cancelled = true;
      player?.destroy();
    };
  }, [source]);

  return (
    <div className="space-y-2">
      <div className="aspect-video overflow-hidden rw-radius border rw-line bg-black">
        <video ref={video} controls playsInline preload="metadata" title={title} className="size-full" />
      </div>
      {failed && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {t(locale, "course.lesson.videoFailed")}
        </p>
      )}
    </div>
  );
}
