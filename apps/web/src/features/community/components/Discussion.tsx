"use client";

import { numericStamp } from "@rankwant/shared/format";
import { Fragment, useMemo, useState } from "react";

import { GuestPrompt } from "@/components/auth/SignInPopover";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { UserName } from "@/components/ui/Identity/UserName";
import { Markdown } from "@/components/ui/Markdown";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t, type Locale } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import {
  HIDDEN_CODE,
  REPORT_REASONS,
  deleteComment,
  editComment,
  loadThreads,
  reportComment,
  voteComment,
  writeComment,
  type ReportReason,
  type Target,
  type ThreadComment,
  type ThreadPage,
} from "../api";
import { linkMentions } from "../mentions";

/** The page stops indenting here; deeper replies name whom they answer. */
const MAX_INDENT = 4;
const BODY_MAX = 2000;

const ACTION =
  "inline-flex min-h-9 items-center rw-radius-sm px-2 text-theme-xs font-medium rw-dim rw-hover-bg rw-focus-ring";

/** The colour of a score: green above zero, red below. */
function scoreClass(score: number): string {
  if (score > 0) return "rw-ok-ink";
  if (score < 0) return "rw-bad-ink";
  return "rw-faint";
}

function problemText(locale: Locale, error: unknown): string {
  return error instanceof ApiError ? errorText(locale, error.code, error.message) : String(error);
}

function CommentBody({ body }: { body: string }) {
  const locale = useLocale();
  const parts = body.split(HIDDEN_CODE);
  return (
    <div className="space-y-2 text-theme-sm rw-strong">
      {parts.map((part, i) => (
        <Fragment key={i}>
          {part.trim() && <Markdown>{linkMentions(part)}</Markdown>}
          {i < parts.length - 1 && (
            <p
              role="note"
              className="rw-radius-sm border border-dashed rw-line rw-warn-soft px-3 py-2 text-theme-xs font-semibold rw-warn-ink"
            >
              {t(locale, "discussion.hiddenCode")}
            </p>
          )}
        </Fragment>
      ))}
    </div>
  );
}

function Composer({
  initial = "",
  busy,
  error,
  autoFocus,
  submitLabel,
  onSubmit,
  onCancel,
  codeHint,
}: {
  initial?: string;
  busy: boolean;
  error: string;
  autoFocus?: boolean;
  submitLabel: string;
  onSubmit: (body: string) => Promise<boolean>;
  onCancel?: () => void;
  /** Problem threads warn that code is hidden from those who have not solved it. */
  codeHint: boolean;
}) {
  const locale = useLocale();
  const [body, setBody] = useState(initial);
  return (
    <form
      className="space-y-2 rw-radius-sm border rw-line rw-field-bg p-3"
      onSubmit={async (event) => {
        event.preventDefault();
        if (await onSubmit(body)) setBody("");
      }}
    >
      <textarea
        value={body}
        maxLength={BODY_MAX}
        rows={3}
        autoFocus={autoFocus}
        aria-label={t(locale, "discussion.placeholder")}
        placeholder={t(locale, "discussion.placeholder")}
        onChange={(event) => setBody(event.target.value)}
        className="w-full resize-y bg-transparent text-theme-sm rw-strong outline-none"
      />
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-theme-xs rw-faint">
          {fill(t(locale, codeHint ? "discussion.limits" : "discussion.limitsPlain"), {
            count: body.length,
            max: BODY_MAX,
          })}
        </span>
        <span className="flex gap-2">
          {onCancel && (
            <Button type="button" variant="outline" onClick={onCancel}>
              {t(locale, "discussion.cancel")}
            </Button>
          )}
          <Button type="submit" busy={busy} disabled={!body.trim()}>
            {submitLabel}
          </Button>
        </span>
      </div>
      {error && (
        <p role="alert" className="text-theme-xs rw-bad-ink">
          {error}
        </p>
      )}
    </form>
  );
}

type Mode = "" | "reply" | "edit" | "report" | "delete";

type NodeProps = {
  comment: ThreadComment;
  byParent: Map<number | null, ThreadComment[]>;
  byId: Map<number, ThreadComment>;
  signedIn: boolean;
  target: Target;
  onChange: (comment: ThreadComment) => void;
  onAdd: (comment: ThreadComment) => void;
};

function CommentNode({ comment, byParent, byId, signedIn, target, onChange, onAdd }: NodeProps) {
  const locale = useLocale();
  const [mode, setMode] = useState<Mode>("");
  // Pressing the same action again closes it.
  const flip = (next: Mode) => setMode((current) => (current === next ? "" : next));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const replies = byParent.get(comment.id) ?? [];
  const removed = comment.is_deleted || comment.is_hidden;
  const parent = comment.parent !== null ? byId.get(comment.parent) : undefined;

  async function run<T>(work: () => Promise<T>, done: (value: T) => void): Promise<boolean> {
    setBusy(true);
    setError("");
    try {
      done(await work());
      return true;
    } catch (caught) {
      setError(problemText(locale, caught));
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function vote(value: -1 | 1) {
    const next = comment.my_vote === value ? 0 : value;
    await run(
      () => voteComment(comment.id, next),
      (res) => onChange({ ...comment, score: res.score, my_vote: res.my_vote }),
    );
  }

  const voteButton = (value: -1 | 1) => {
    const label = t(locale, value > 0 ? "discussion.voteUp" : "discussion.voteDown");
    const glyph = value > 0 ? "▲" : "▼";
    if (!signedIn)
      return (
        <GuestPrompt
          reason="vote"
          trigger={(props) => (
            <button {...props} aria-label={label} className={ACTION}>
              {glyph}
            </button>
          )}
        />
      );
    return (
      <button
        type="button"
        aria-label={label}
        aria-pressed={comment.my_vote === value}
        disabled={busy || comment.mine || removed}
        onClick={() => void vote(value)}
        className={`${ACTION} ${comment.my_vote === value ? "rw-accent-ink" : ""}`}
      >
        {glyph}
      </button>
    );
  };

  return (
    <li id={`c${comment.id}`} className="space-y-2">
      <article className="space-y-1">
        <header className="flex flex-wrap items-baseline gap-x-2 gap-y-1 text-theme-xs rw-faint">
          {comment.author ? (
            <UserName
              username={comment.author.username}
              name={comment.author.display_name}
              title={comment.author.title}
              locale={locale}
              className="text-theme-sm"
            />
          ) : (
            <span className="text-theme-sm rw-dim">—</span>
          )}
          {comment.author_owner && <Badge color="brand">{t(locale, "discussion.owner")}</Badge>}
          {comment.author_solved && <Badge color="success">✓ {t(locale, "discussion.solved")}</Badge>}
          {comment.depth > MAX_INDENT && parent?.author && (
            <span>{fill(t(locale, "discussion.replyTo"), { user: parent.author.username })}</span>
          )}
          <a href={`#c${comment.id}`} className="tabular-nums rw-link-hover">
            <time dateTime={comment.created_at}>{numericStamp(comment.created_at).slice(0, 16)}</time>
          </a>
          {comment.edited_at && <span>· {t(locale, "discussion.edited")}</span>}
        </header>

        {mode === "edit" ? (
          <Composer
            codeHint={target.kind === "problem"}
            initial={comment.body}
            busy={busy}
            error={error}
            autoFocus
            submitLabel={t(locale, "discussion.save")}
            onCancel={() => setMode("")}
            onSubmit={(body) =>
              run(
                () => editComment(comment.id, body),
                (row) => {
                  onChange(row);
                  setMode("");
                },
              )
            }
          />
        ) : removed && !comment.body ? (
          <p className="text-theme-sm italic rw-faint">
            {t(locale, comment.is_deleted ? "discussion.deleted" : "discussion.hidden")}
          </p>
        ) : (
          <CommentBody body={comment.body} />
        )}

        {!removed && mode !== "edit" && (
          <div className="flex flex-wrap items-center gap-1">
            {voteButton(1)}
            <span className={`min-w-6 text-center text-theme-xs font-bold tabular-nums ${scoreClass(comment.score)}`}>
              {comment.score > 0 ? `+${comment.score}` : comment.score}
            </span>
            {voteButton(-1)}
            {signedIn ? (
              <button type="button" className={ACTION} onClick={() => flip("reply")}>
                {t(locale, "discussion.reply")}
              </button>
            ) : (
              <GuestPrompt
                reason="comment"
                trigger={(props) => (
                  <button {...props} className={ACTION}>
                    {t(locale, "discussion.reply")}
                  </button>
                )}
              />
            )}
            {comment.mine ? (
              <>
                <button type="button" className={ACTION} onClick={() => setMode("edit")}>
                  {t(locale, "discussion.edit")}
                </button>
                <button type="button" className={ACTION} onClick={() => setMode("delete")}>
                  {t(locale, "discussion.delete")}
                </button>
              </>
            ) : signedIn ? (
              <button type="button" className={ACTION} onClick={() => flip("report")}>
                {t(locale, "discussion.report")}
              </button>
            ) : (
              <GuestPrompt
                reason="report"
                trigger={(props) => (
                  <button {...props} className={ACTION}>
                    {t(locale, "discussion.report")}
                  </button>
                )}
              />
            )}
            {note && <span className="text-theme-xs rw-ok-ink">{note}</span>}
          </div>
        )}

        {mode === "delete" && (
          <div className="flex flex-wrap items-center gap-2 text-theme-xs rw-dim">
            <span>{t(locale, "discussion.deleteConfirm")}</span>
            <Button
              variant="outline"
              busy={busy}
              onClick={() =>
                void run(
                  () => deleteComment(comment.id),
                  () => {
                    onChange({ ...comment, is_deleted: true, body: "", author: null });
                    setMode("");
                  },
                )
              }
            >
              {t(locale, "discussion.delete")}
            </Button>
            <Button variant="outline" onClick={() => setMode("")}>
              {t(locale, "discussion.cancel")}
            </Button>
          </div>
        )}

        {mode === "report" && (
          <fieldset className="flex flex-wrap items-center gap-2 text-theme-xs">
            <legend className="sr-only">{t(locale, "discussion.reportTitle")}</legend>
            <span className="rw-dim">{t(locale, "discussion.reportTitle")}</span>
            {REPORT_REASONS.map((reason: ReportReason) => (
              <Button
                key={reason}
                variant="outline"
                busy={busy}
                onClick={() =>
                  void run(
                    () => reportComment(comment.id, reason),
                    () => {
                      setMode("");
                      setNote(t(locale, "discussion.reported"));
                    },
                  )
                }
              >
                {t(locale, `discussion.reason.${reason}`)}
              </Button>
            ))}
          </fieldset>
        )}

        {error && mode !== "edit" && mode !== "reply" && (
          <p role="alert" className="text-theme-xs rw-bad-ink">
            {error}
          </p>
        )}

        {mode === "reply" && (
          <Composer
            codeHint={target.kind === "problem"}
            busy={busy}
            error={error}
            autoFocus
            submitLabel={t(locale, "discussion.reply")}
            onCancel={() => setMode("")}
            onSubmit={(body) =>
              run(
                () => writeComment(target, body, comment.id),
                (row) => {
                  onAdd(row);
                  setMode("");
                },
              )
            }
          />
        )}
      </article>

      {replies.length > 0 && (
        <ul
          className={`space-y-3 ${
            comment.depth < MAX_INDENT ? "ms-3 border-s-2 rw-line ps-3 sm:ms-5 sm:ps-4" : ""
          }`}
        >
          {replies.map((reply) => (
            <CommentNode
              key={reply.id}
              comment={reply}
              byParent={byParent}
              byId={byId}
              signedIn={signedIn}
              target={target}
              onChange={onChange}
              onAdd={onAdd}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

/** A discussion: a page of threads, newest first, replies as a tree. */
export function Discussion({
  target,
  initial,
  signedIn,
}: {
  target: Target;
  initial: ThreadPage;
  signedIn: boolean;
}) {
  const locale = useLocale();
  const [comments, setComments] = useState(initial.comments);
  const [count, setCount] = useState(initial.count);
  const [next, setNext] = useState(initial.next);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const { byParent, byId } = useMemo(() => {
    const parents = new Map<number | null, ThreadComment[]>();
    const ids = new Map<number, ThreadComment>();
    for (const row of comments) {
      ids.set(row.id, row);
      const key = row.parent;
      parents.set(key, [...(parents.get(key) ?? []), row]);
    }
    return { byParent: parents, byId: ids };
  }, [comments]);

  const change = (row: ThreadComment) =>
    setComments((rows) => rows.map((old) => (old.id === row.id ? row : old)));
  const add = (row: ThreadComment) => {
    setComments((rows) => (row.parent === null ? [row, ...rows] : [...rows, row]));
    setCount((n) => n + 1);
  };

  async function write(body: string): Promise<boolean> {
    setBusy(true);
    setError("");
    try {
      add(await writeComment(target, body));
      return true;
    } catch (caught) {
      setError(problemText(locale, caught));
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function more() {
    setBusy(true);
    try {
      const page = await loadThreads(target, next);
      setComments((rows) => [...rows, ...page.comments]);
      setNext(page.next);
    } catch (caught) {
      setError(problemText(locale, caught));
    } finally {
      setBusy(false);
    }
  }

  const roots = byParent.get(null) ?? [];

  return (
    <section aria-labelledby="discussion-title" className="space-y-4">
      <h2 id="discussion-title" className="text-theme-xl font-semibold rw-strong">
        {t(locale, "discussion.title")}{" "}
        <span className="text-theme-sm font-normal rw-faint">
          {fill(t(locale, "discussion.count"), { count })}
        </span>
      </h2>

      {signedIn ? (
        <Composer
          busy={busy}
          error={error}
          codeHint={target.kind === "problem"}
          submitLabel={t(locale, "discussion.send")}
          onSubmit={write}
        />
      ) : (
        <GuestPrompt
          reason="comment"
          trigger={(props) => (
            <button
              {...props}
              className="w-full rw-radius-sm border rw-line rw-field-bg p-3 text-start text-theme-sm rw-faint rw-focus-ring"
            >
              {t(locale, "discussion.placeholder")}
            </button>
          )}
        />
      )}

      {roots.length === 0 ? (
        <p className="text-theme-sm rw-dim">{t(locale, "discussion.empty")}</p>
      ) : (
        <ul className="divide-y rw-divide">
          {roots.map((root) => (
            <li key={root.id} className="py-4 first:pt-0">
              <ul>
                <CommentNode
                  comment={root}
                  byParent={byParent}
                  byId={byId}
                  signedIn={signedIn}
                  target={target}
                  onChange={change}
                  onAdd={add}
                />
              </ul>
            </li>
          ))}
        </ul>
      )}

      {next !== null && (
        <Button variant="outline" busy={busy} onClick={() => void more()}>
          {t(locale, "discussion.more")}
        </Button>
      )}
    </section>
  );
}
