import { errorText, type Locale } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

/** An API refusal in the reader's language (`error.<code>`). */
export function failure(locale: Locale, err: unknown): string {
  return err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err);
}
