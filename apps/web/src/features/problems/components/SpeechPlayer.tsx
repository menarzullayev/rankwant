"use client";

import { useEffect, useRef, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { API_BASE, ApiError, getJson, postJson } from "@/lib/api";
import type { components } from "@/lib/api/generated/schema";

type Speech = components["schemas"]["ProblemSpeech"];
type State =
  | "idle"
  | "loading"
  | "playing"
  | "paused"
  | "waiting"
  | "off"
  | "busy"
  | "error";

/** How often a piece still being made is re-read, and for how long. */
const POLL_MS = 1000;
const WAIT_LIMIT_MS = 3 * 60 * 1000;

const speechPath = (slug: string) =>
  `/problems/${encodeURIComponent(slug)}/speech/`;

/** «Tinglash»: the statement read aloud by Navoiy (ADR-0064 § 5).
 *
 *  Pieces are made on demand and kept; the first one is short, so the first
 *  listener waits seconds, and each next piece is ready before the one
 *  before it ends. Shown only where the page shows the Uzbek text. */
export function SpeechPlayer({ slug }: { slug: string }) {
  const locale = useLocale();
  const [state, setState] = useState<State>("idle");
  const [index, setIndex] = useState(0);
  const [total, setTotal] = useState(0);
  const audio = useRef<HTMLAudioElement | null>(null);
  const pieces = useRef<Speech["pieces"]>([]);
  const stopped = useRef(false);

  useEffect(() => {
    return () => {
      stopped.current = true;
      audio.current?.pause();
    };
  }, []);

  async function refresh(): Promise<void> {
    const speech = await getJson<Speech>(speechPath(slug));
    pieces.current = speech.pieces;
  }

  const pieceUrl = (at: number) =>
    `${API_BASE}/speech/${pieces.current[at].key}.mp3`;

  /** Wait until piece `at` is made. `visible` — the listener is waiting for
   *  it now; otherwise it is the next piece, looked for while one plays. */
  async function waitReady(at: number, visible: boolean): Promise<boolean> {
    const started = Date.now();
    while (!pieces.current[at]?.ready) {
      if (stopped.current) return false;
      if (Date.now() - started > WAIT_LIMIT_MS) {
        if (visible) setState("busy");
        return false;
      }
      if (visible) setState("waiting");
      await new Promise((resolve) => setTimeout(resolve, POLL_MS));
      await refresh();
    }
    return true;
  }

  async function play(at: number): Promise<void> {
    if (stopped.current) return;
    if (at >= pieces.current.length) {
      setState("idle");
      setIndex(0);
      return;
    }
    setIndex(at);
    if (!(await waitReady(at, true))) return;
    const player = audio.current ?? new Audio();
    audio.current = player;
    player.src = pieceUrl(at);
    player.onended = () => void play(at + 1);
    player.onerror = () => setState("error");
    setState("playing");
    await player.play().catch(() => setState("error"));
    // Look for the next piece while this one plays, and fetch it into the
    // browser cache (the file is immutable): measured 2026-11-12, waiting
    // for it only after the end left a 2 s gap between pieces.
    if (at + 1 < pieces.current.length && (await waitReady(at + 1, false))) {
      const next = new Audio();
      next.preload = "auto";
      next.src = pieceUrl(at + 1);
    }
  }

  async function start(): Promise<void> {
    stopped.current = false;
    setState("loading");
    try {
      const speech = await getJson<Speech>(speechPath(slug));
      if (!speech.available) {
        setState("off");
        return;
      }
      pieces.current = speech.pieces;
      setTotal(speech.pieces.length);
      if (speech.pieces.some((p) => !p.ready)) {
        const queued = await postJson<Speech>(
          `${speechPath(slug)}generate/`,
          {},
        );
        pieces.current = queued.pieces;
      }
      await play(0);
    } catch (caught) {
      setState(
        caught instanceof ApiError && caught.status === 429 ? "busy" : "error",
      );
    }
  }

  function pause(): void {
    audio.current?.pause();
    setState("paused");
  }

  function resume(): void {
    setState("playing");
    void audio.current?.play();
  }

  function stop(): void {
    stopped.current = true;
    audio.current?.pause();
    setState("idle");
    setIndex(0);
  }

  const active =
    state === "playing" || state === "paused" || state === "waiting";
  const note =
    state === "waiting" || state === "loading"
      ? t(locale, "problem.listenPreparing")
      : state === "off"
        ? t(locale, "problem.listenOff")
        : state === "busy"
          ? t(locale, "problem.listenBusy")
          : state === "error"
            ? t(locale, "tutor.fail.other")
            : null;

  return (
    <div className="mb-4 flex flex-wrap items-center gap-2 border-b rw-divider pb-3">
      {!active ? (
        <button
          type="button"
          onClick={() => void start()}
          disabled={state === "loading"}
          className="min-h-11 rw-radius-sm border rw-line px-3 text-theme-sm font-medium rw-strong rw-hover-bg rw-focus-ring disabled:opacity-50"
        >
          {t(locale, "problem.listen")}
        </button>
      ) : (
        <>
          <button
            type="button"
            onClick={state === "paused" ? resume : pause}
            disabled={state === "waiting"}
            className="min-h-11 rw-radius-sm border rw-line px-3 text-theme-sm font-medium rw-strong rw-hover-bg rw-focus-ring disabled:opacity-50"
          >
            {t(
              locale,
              state === "paused"
                ? "problem.listenResume"
                : "problem.listenPause",
            )}
          </button>
          <button
            type="button"
            onClick={stop}
            className="min-h-11 rw-radius-sm px-3 text-theme-sm rw-dim rw-hover-bg rw-focus-ring"
          >
            {t(locale, "problem.listenStop")}
          </button>
          {total > 1 && (
            <span className="text-theme-xs rw-faint tabular-nums">
              {fill(t(locale, "problem.listenProgress"), {
                n: index + 1,
                total,
              })}
            </span>
          )}
        </>
      )}
      {note && (
        <span role="status" className="text-theme-xs rw-dim">
          {note}
        </span>
      )}
      {(active || state === "idle") && total > 0 && (
        <span className="w-full text-theme-xs rw-faint">
          {t(locale, "problem.listenCredit")}
        </span>
      )}
    </div>
  );
}
