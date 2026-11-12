"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { ApiError } from "@/lib/api";

import {
  askTutor,
  deleteTutorConversation,
  tutorConversation,
  type TutorAsk,
  type TutorConversation,
} from "./api";

export type TutorFailure = { code: string; details: Record<string, unknown> };

/** How often a pending reply is re-read. A reply takes 6–9 s (measured
 *  2026-11-12); the server gives up on it after a few minutes. */
const POLL_MS = 1500;
const POLL_LIMIT_MS = 4 * 60 * 1000;

function failure(caught: unknown): TutorFailure {
  if (caught instanceof ApiError)
    return { code: caught.code, details: caught.details };
  return { code: "network", details: {} };
}

/** The student's conversation with the tutor on one problem. Loaded when
 *  `active` turns on; re-read while a reply is pending. */
export function useTutor(slug: string, active: boolean, lang: string) {
  const [conversation, setConversation] = useState<TutorConversation | null>(
    null,
  );
  const [problem, setProblem] = useState<TutorFailure | null>(null);
  const [sending, setSending] = useState(false);
  const pollingSince = useRef<number | null>(null);

  const reload = useCallback(async () => {
    try {
      setConversation(await tutorConversation(slug));
    } catch (caught) {
      setProblem(failure(caught));
    }
  }, [slug]);

  const loaded = conversation !== null;
  useEffect(() => {
    if (!active || loaded) return;
    let cancelled = false;
    tutorConversation(slug).then(
      (next) => {
        if (!cancelled) setConversation(next);
      },
      (caught) => {
        if (!cancelled) setProblem(failure(caught));
      },
    );
    return () => {
      cancelled = true;
    };
  }, [active, loaded, slug]);

  const pending = Boolean(
    conversation?.messages.some((m) => m.status === "pending"),
  );

  useEffect(() => {
    if (!pending) {
      pollingSince.current = null;
      return;
    }
    pollingSince.current ??= Date.now();
    if (Date.now() - pollingSince.current > POLL_LIMIT_MS) return;
    const handle = setTimeout(() => void reload(), POLL_MS);
    return () => clearTimeout(handle);
  }, [pending, conversation, reload]);

  const ask = useCallback(
    async (body: TutorAsk) => {
      setSending(true);
      setProblem(null);
      try {
        setConversation(await askTutor(slug, body, lang));
        return true;
      } catch (caught) {
        setProblem(failure(caught));
        return false;
      } finally {
        setSending(false);
      }
    },
    [slug, lang],
  );

  const clear = useCallback(async () => {
    setProblem(null);
    try {
      await deleteTutorConversation(slug);
    } catch (caught) {
      setProblem(failure(caught));
    }
    await reload();
  }, [slug, reload]);

  return { conversation, problem, sending, pending, ask, clear, reload };
}
