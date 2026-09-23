/**
 * Shared i18n core — locale identity, dictionary registry, translation
 * lookup, content-name resolution.
 *
 * The dictionaries themselves stay in the app (`apps/web/src/i18n/locales`).
 * This package is the *mechanism*; the app is the *data*.
 */
export * from "./core";
