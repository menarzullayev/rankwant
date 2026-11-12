"use client";

import { useEffect, useId, useRef, useState } from "react";

import { Icon } from "@/components/ui/Icon";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t, type Locale } from "@/i18n/messages";
import { currentEditorCode } from "@/lib/editor-bridge";

import type { TutorConversation, TutorMessage } from "../api";
import { useTutor, type TutorFailure } from "../useTutor";
import { TutorReply, failureText } from "./TutorReply";

const STEPS = [1, 2, 3] as const;
const STEP_KEYS = {
  1: "tutor.step1",
  2: "tutor.step2",
  3: "tutor.step3",
} as const;

function usageText(
  locale: Locale,
  conversation: TutorConversation | null,
): string {
  if (!conversation) return "";
  const { used, limit } = conversation.usage;
  return limit === null
    ? fill(t(locale, "tutor.usageUnlimited"), { used })
    : fill(t(locale, "tutor.usage"), { used, limit });
}

/** Why the panel cannot ask: the server's `reason`, else the last refusal. */
function blockedText(
  locale: Locale,
  conversation: TutorConversation | null,
  problem: TutorFailure | null,
) {
  if (conversation && !conversation.available) {
    return t(
      locale,
      conversation.reason === "ai_off_in_contest"
        ? "tutor.contest"
        : "tutor.fail.unavailable",
    );
  }
  if (!problem) return null;
  if (problem.code === "tutor_limit") {
    return fill(t(locale, "tutor.limit"), {
      limit: String(problem.details.limit ?? ""),
    });
  }
  if (problem.code === "ai_off_in_contest") return t(locale, "tutor.contest");
  if (problem.code === "ai_unavailable")
    return t(locale, "tutor.fail.unavailable");
  if (problem.code === "tutor_busy") return t(locale, "tutor.thinking");
  if (problem.code === "no_code") return t(locale, "tutor.noCode");
  return failureText(locale, "other");
}

/** What the student asked, as a line in the conversation. */
function askedText(locale: Locale, message: TutorMessage): string {
  if (message.kind === "hint" && message.hint_level) {
    return t(
      locale,
      STEP_KEYS[message.hint_level as 1 | 2 | 3] ?? "tutor.step1",
    );
  }
  if (message.kind === "why_wrong") return t(locale, "tutor.whyWrong");
  return message.text;
}

/** The AI tutor beside the problem (ADR-0065; owner choice 2026-11-12:
 *  a side panel with a three-step hint ladder). A launcher button opens
 *  it; on a narrow screen it covers the page like the editor's sheet.
 *  Rendered only for a signed-in student who may solve the problem. */
export function TutorPanel({ slug }: { slug: string }) {
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [local, setLocal] = useState<TutorFailure | null>(null);
  const { conversation, problem, sending, pending, ask, clear } = useTutor(
    slug,
    open,
  );
  const titleId = useId();
  const inputId = useId();
  const panelRef = useRef<HTMLDivElement>(null);
  const launcherRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    panelRef.current?.focus();
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
        launcherRef.current?.focus();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const blocked = blockedText(locale, conversation, local ?? problem);
  const canAsk = Boolean(conversation?.available) && !pending && !sending;
  const level = conversation?.hint_level ?? 0;

  async function send(body: Parameters<typeof ask>[0]) {
    setLocal(null);
    return ask(body);
  }

  async function checkCode() {
    const code = currentEditorCode();
    if (!code || !code.source.trim()) {
      setLocal({ code: "no_code", details: {} });
      return;
    }
    await send({
      kind: "ask",
      question: t(locale, "tutor.checkCodeQuestion"),
      code: code.source,
      code_language: code.language,
    });
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const text = question.trim();
    if (!text || !canAsk) return;
    if (await send({ kind: "ask", question: text })) setQuestion("");
  }

  return (
    <>
      <button
        ref={launcherRef}
        type="button"
        aria-expanded={open}
        aria-controls={titleId}
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-36 right-4 z-30 inline-flex min-h-11 items-center gap-2 rw-radius-full border rw-line rw-panel-bg px-4 py-2.5 text-theme-sm font-semibold rw-strong shadow-lg rw-focus-ring xl:bottom-6 xl:right-6"
      >
        {t(locale, "tutor.title")}
      </button>

      {open && (
        <div
          ref={panelRef}
          role="dialog"
          aria-modal="false"
          aria-labelledby={titleId}
          tabIndex={-1}
          className="fixed inset-x-0 bottom-0 top-[var(--rw-header-h)] z-40 flex flex-col border-l rw-divider rw-panel-bg shadow-[0_0_32px_rgba(0,0,0,.14)] outline-none sm:left-auto sm:w-[26rem]"
        >
          <div className="flex items-center justify-between gap-3 border-b rw-divider px-4 py-3">
            <div className="min-w-0">
              <h2
                id={titleId}
                className="text-theme-base font-semibold rw-strong"
              >
                {t(locale, "tutor.title")}
              </h2>
              <p className="text-theme-xs rw-faint tabular-nums">
                {usageText(locale, conversation)}
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                launcherRef.current?.focus();
              }}
              aria-label={t(locale, "tutor.close")}
              className="inline-flex size-11 items-center justify-center rw-radius-sm rw-dim rw-hover-bg rw-focus-ring"
            >
              <Icon name="nav.close" className="size-5" />
            </button>
          </div>

          <div className="flex-1 space-y-4 rw-scroll-y px-4 py-4">
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={!canAsk}
                onClick={() =>
                  void send({
                    kind: "ask",
                    question: t(locale, "tutor.explainQuestion"),
                  })
                }
                className="min-h-11 rw-radius-sm border rw-line px-3 text-theme-sm rw-strong rw-hover-bg rw-focus-ring disabled:opacity-50"
              >
                {t(locale, "tutor.explain")}
              </button>
              <button
                type="button"
                disabled={!canAsk}
                onClick={() => void checkCode()}
                className="min-h-11 rw-radius-sm border rw-line px-3 text-theme-sm rw-strong rw-hover-bg rw-focus-ring disabled:opacity-50"
              >
                {t(locale, "tutor.checkCode")}
              </button>
            </div>

            <section
              aria-label={t(locale, "tutor.ladder")}
              className="space-y-2"
            >
              <h3 className="text-theme-xs font-semibold uppercase tracking-wide rw-faint">
                {t(locale, "tutor.ladder")}
              </h3>
              <ol className="grid grid-cols-3 gap-2">
                {STEPS.map((step) => {
                  const given = step <= level;
                  const next = step === level + 1;
                  return (
                    <li key={step}>
                      <button
                        type="button"
                        disabled={!canAsk || (!given && !next)}
                        onClick={() =>
                          void send({ kind: "hint", hint_level: step })
                        }
                        className={`flex min-h-11 w-full flex-col items-start rw-radius-sm border px-2.5 py-1.5 text-left rw-focus-ring disabled:opacity-50 ${
                          given
                            ? "rw-accent-soft border-transparent"
                            : "rw-line rw-hover-bg"
                        }`}
                      >
                        <span className="text-theme-xs rw-faint tabular-nums">
                          {step}
                        </span>
                        <span className="text-theme-sm font-medium rw-strong">
                          {t(locale, STEP_KEYS[step])}
                        </span>
                        {given && (
                          <span className="sr-only">
                            {t(locale, "tutor.stepGiven")}
                          </span>
                        )}
                      </button>
                    </li>
                  );
                })}
              </ol>
            </section>

            {blocked && (
              <p
                role="status"
                className="rw-radius-sm rw-field-bg px-3 py-2 text-theme-sm rw-dim-2"
              >
                {blocked}
              </p>
            )}

            {conversation && conversation.messages.length === 0 && !blocked && (
              <p className="text-theme-sm rw-dim">{t(locale, "tutor.empty")}</p>
            )}

            <ul className="space-y-3">
              {conversation?.messages.map((message) =>
                message.role === "student" ? (
                  <li
                    key={message.id}
                    className="ml-8 rw-radius-sm rw-field-bg px-3 py-2 text-theme-sm rw-strong"
                  >
                    <span className="sr-only">{t(locale, "tutor.you")}: </span>
                    {askedText(locale, message)}
                  </li>
                ) : (
                  <li key={message.id} className="mr-4">
                    <span className="sr-only">
                      {t(locale, "tutor.title")}:{" "}
                    </span>
                    <TutorReply message={message} />
                  </li>
                ),
              )}
            </ul>
          </div>

          <form
            onSubmit={submit}
            className="space-y-2 border-t rw-divider px-4 py-3"
          >
            <label htmlFor={inputId} className="sr-only">
              {t(locale, "tutor.askPlaceholder")}
            </label>
            <textarea
              id={inputId}
              rows={2}
              maxLength={1500}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={t(locale, "tutor.askPlaceholder")}
              className="w-full resize-none rw-radius-sm border rw-line rw-field-bg px-3 py-2 text-theme-sm rw-strong rw-focus-ring"
            />
            <div className="flex items-center justify-between gap-2">
              <button
                type="button"
                onClick={() => void clear()}
                disabled={!conversation?.messages.length || pending}
                className="min-h-11 rw-radius-sm px-2 text-theme-xs rw-faint rw-hover-bg rw-focus-ring disabled:opacity-50"
              >
                {t(locale, "tutor.delete")}
              </button>
              <button
                type="submit"
                disabled={!canAsk || !question.trim()}
                className="min-h-11 rw-radius-sm rw-accent-bg px-4 text-theme-sm font-semibold rw-btn-label rw-focus-ring disabled:opacity-50"
              >
                {t(locale, "tutor.send")}
              </button>
            </div>
            <p className="text-theme-xs rw-faint">
              {t(locale, "tutor.retention")}
            </p>
          </form>
        </div>
      )}
    </>
  );
}
