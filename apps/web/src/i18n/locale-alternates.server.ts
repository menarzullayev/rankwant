import { headers } from "next/headers";

import { localeAlternates } from "./locale-alternates";
import { LANG_PARAM_HEADER } from "./locale-params";

/** Layout `searchParams` ni ko'rmaydi — proxy `LANG_PARAM_HEADER` yozadi. */
export async function localeAlternatesFor(path: string): Promise<{
  canonical: string;
  languages: Record<string, string>;
}> {
  const langParam = (await headers()).get(LANG_PARAM_HEADER);
  return localeAlternates(path, langParam);
}
