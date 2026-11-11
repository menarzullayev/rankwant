/** Discussion threads (decision 2026-11-11, `community` app). */

import { deleteJson, getJson, patchJson, postJson } from "@/lib/api";
import type { UserTitle } from "@/lib/identity";

export type CommentAuthor = {
  username: string;
  display_name: string;
  title: UserTitle | null;
};

export type ThreadComment = {
  id: number;
  parent: number | null;
  depth: number;
  /** Null when the author deleted it. */
  author: CommentAuthor | null;
  /** Empty when deleted or hidden. Code blocks the reader may not see are
   *  replaced by `HIDDEN_CODE`. */
  body: string;
  hidden_code: number;
  score: number;
  my_vote: number;
  mine: boolean;
  author_solved: boolean;
  author_owner: boolean;
  is_deleted: boolean;
  is_hidden: boolean;
  created_at: string;
  edited_at: string | null;
};

export type ThreadPage = {
  count: number;
  /** Pass as `before` for older threads; null at the end. */
  next: number | null;
  /** Whether this reader sees code blocks (they solved the problem). */
  code_open: boolean;
  comments: ThreadComment[];
};

/** Where a thread lives — a problem now, a blog entry later. */
export type Target = { kind: "problem"; ref: string };

/** The marker the API puts in place of a hidden code block. */
export const HIDDEN_CODE = "[[hidden-code]]";

export const REPORT_REASONS = ["spam", "rude", "spoiler", "other"] as const;
export type ReportReason = (typeof REPORT_REASONS)[number];

export function threadPath(target: Target): string {
  return `/discussions/${target.kind}/${encodeURIComponent(target.ref)}/`;
}

export function loadThreads(target: Target, before?: number | null) {
  const query = before ? `?before=${before}` : "";
  return getJson<ThreadPage>(`${threadPath(target)}${query}`);
}

export function writeComment(target: Target, body: string, replyTo?: number) {
  return postJson<ThreadComment>(threadPath(target), {
    body,
    ...(replyTo ? { reply_to: replyTo } : {}),
  });
}

export const editComment = (id: number, body: string) =>
  patchJson<ThreadComment>(`/comments/${id}/`, { body });

export const deleteComment = (id: number) => deleteJson(`/comments/${id}/`);

export const voteComment = (id: number, value: -1 | 0 | 1) =>
  postJson<{ score: number; my_vote: number }>(`/comments/${id}/vote/`, { value });

export const reportComment = (id: number, reason: ReportReason) =>
  postJson<unknown>(`/comments/${id}/report/`, { reason });
