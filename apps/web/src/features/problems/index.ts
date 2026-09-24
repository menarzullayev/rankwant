/** `problems` — feature'ning ommaviy yuzasi.
 *
 * Tashqaridan faqat shu fayl orqali import qilinadi:
 * `import { X } from "@/features/problems"`.
 * Ichki tuzilma (`components/`, `api/`) — xususiy.
 */

export { Editorial } from "./components/Editorial";

export { FavouriteToggle } from "./components/FavouriteToggle";

export { ProblemActions } from "./components/ProblemActions";

export { ProblemFilters } from "./components/ProblemFilters";
export type { FilterTopic } from "./components/ProblemFilters";

export { ProblemTabs } from "./components/ProblemTabs";

export { ReportProblem } from "./components/ReportProblem";

export { SubmitPanel } from "./components/SubmitPanel";

export { SampleTests } from "./components/SampleTests";

export { SimilarProblems } from "./components/SimilarProblems";

export { StatementSize } from "./components/StatementSize";

export { TopicBadges } from "./components/TopicBadges";

export { LANGUAGES_PATH, REPORT_REASONS, VERDICT_FILTERS, fetchAttempt, fetchCustomRun, fetchLanguages, fetchProblemAttempts, rateProblem, reportProblem, runCustomTest, setFavourite, submitAttempt, unlockEditorial, voteProblem } from "./api/problems";
export type { ArchiveProgress, Attachment, Attempt, AttemptDetail, CustomRun, EditorialState, Language, Problem, ProblemDetail, ProblemLanguage, ProblemStats, Recommendation, Sample, SimilarProblem, Solver, TestResult, Topic, TopicSkill } from "./api/problems";
