/** Hook'ni ro'yxatga oluvchi yupqa qatlam.
 *
 *  `--import` bilan beriladigan fayl `register()` ni O'ZI chaqirishi
 *  shart — shunchaki `export function load()` yozish yetmaydi. Shuning
 *  uchun mantiq `i18n-runtime-hook.mjs` da, chaqiruv esa shu yerda.
 */

import { register } from "node:module";
import { pathToFileURL } from "node:url";

register("./i18n-runtime-hook.mjs", pathToFileURL(import.meta.dirname + "/"));
