/** `GET /team/` — see `apps/api/team/serializers.py`. */

export type TeamDepartment = {
  id: number;
  name_uz: string;
  name_ru: string;
  name_en: string;
  order: number;
};

export type TeamRole = {
  id: number;
  department: number;
  title_uz: string;
  title_ru: string;
  title_en: string;
  about_uz: string;
  about_ru: string;
  about_en: string;
  reports_to_uz: string;
  reports_to_ru: string;
  reports_to_en: string;
  status_uz: string;
  status_ru: string;
  status_en: string;
  badge: string;
  hue: number;
  tone: "ok" | "warn";
  order: number;
};

export type TeamMember = {
  id: number;
  section: "core" | "contributor";
  name: string;
  title_uz: string;
  title_ru: string;
  title_en: string;
  context_uz: string;
  context_ru: string;
  context_en: string;
  photo_url: string;
  telegram_url: string;
  github_url: string;
  linkedin_url: string;
  instagram_url: string;
  website_url: string;
  holds_all_roles: boolean;
  order: number;
};

export type TeamPayload = {
  departments: TeamDepartment[];
  roles: TeamRole[];
  members: TeamMember[];
};
