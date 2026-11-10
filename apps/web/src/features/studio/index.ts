/** `studio` — feature'ning ommaviy yuzasi (`/studio`, 2026-11-10).
 *
 * The author's own drafts. Tashqaridan faqat shu fayl orqali import
 * qilinadi: `import { X } from "@/features/studio"`.
 */

export { StudioNav } from "./components/StudioNav";

export { ProblemList } from "./components/ProblemList";

export { ProblemEditor } from "./components/ProblemEditor";

export { DEFAULT_TAB, editorTab, type EditorTab } from "./editor-tabs";

export type { DraftTest, MineProblem } from "./api/problems";

export { ContestList } from "./components/ContestList";

export { ContestEditor } from "./components/ContestEditor";

export { DEFAULT_CONTEST_TAB, contestTab, type ContestTab } from "./contest-tabs";

export type { ContestParticipant, MineContest } from "./api/contests";

export { CourseList } from "./components/CourseList";

export { CourseEditor } from "./components/CourseEditor";

export { CourseReview } from "./components/CourseReview";

export type { StaffCourse, StudioCourse } from "./api/courses";
