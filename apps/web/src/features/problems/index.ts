/** `problems` — feature'ning ommaviy yuzasi.
 *
 * Tashqaridan faqat shu fayl orqali import qilinadi:
 * `import { X } from "@/features/problems"`.
 * Ichki tuzilma (`components/`, `api/`) — xususiy.
 */

export { ProblemStatementCard } from "./components/ProblemStatementCard";

export { StatementSectionNav } from "./components/StatementSectionNav";

export { VerdictPresentationLayer } from "./components/VerdictPresentationLayer";

export { Editorial } from "./components/Editorial";

export { FavouriteToggle } from "./components/FavouriteToggle";

export { ProblemActions } from "./components/ProblemActions";

export { ProblemEditorialPanel } from "./components/ProblemEditorialPanel";

export { ProblemFilters } from "./components/ProblemFilters";
export type { FilterTopic } from "./components/ProblemFilters";

export { ProblemTabs } from "./components/ProblemTabs";

export { ProblemSolversPanel } from "./components/ProblemSolversPanel";

export { ProblemStatsPanel } from "./components/ProblemStatsPanel";

export { ReportProblem } from "./components/ReportProblem";

export { ProblemMetaAccordion } from "./components/ProblemMetaAccordion";

export { ProblemSolveTimer } from "./components/ProblemSolveTimer";

export { ProblemWorkspace } from "./components/ProblemWorkspace";

export { SubmitPanel } from "./components/SubmitPanel";

export { SampleTests } from "./components/SampleTests";

export { SimilarProblems } from "./components/SimilarProblems";

export { StatementSize, StatementTextSizeControls } from "./components/StatementSize";

export { TopicBadges } from "./components/TopicBadges";

export { LANGUAGES_PATH, REPORT_REASONS, VERDICT_FILTERS, fetchAttempt, fetchCustomRun, fetchLanguages, fetchProblemAttempts, rateProblem, reportProblem, runCustomTest, setFavourite, submitAttempt, unlockEditorial, voteProblem } from "./api/problems";
export type { ArchiveProgress, Attachment, Attempt, AttemptDetail, CustomRun, EditorialState, Language, Problem, ProblemDetail, ProblemLanguage, ProblemStats, Recommendation, Sample, SimilarProblem, Solver, TestResult, Topic, TopicSkill } from "./api/problems";
