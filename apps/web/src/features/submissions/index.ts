/** `submissions` — feature'ning ommaviy yuzasi.
 *
 * Tashqaridan faqat shu fayl orqali import qilinadi:
 * `import { X } from "@/features/submissions"`.
 * Ichki tuzilma (`components/`, `api/`) — xususiy.
 */

export { Attachments } from "./components/Attachments";

export { AttemptFilters } from "./components/AttemptFilters";

export {
  AttemptLive,
  AttemptLiveProvider,
  useAttemptLive,
  useAttemptLiveOptional,
} from "./components/AttemptLiveProvider";

export { AttemptLiveProgress } from "./components/AttemptLiveProgress";

export { AttemptTable } from "./components/AttemptTable";

export { AttemptView } from "./components/AttemptView";

export {
  mergeAttemptRow,
  type AttemptLivePatch,
} from "./attemptLiveOverlay";
