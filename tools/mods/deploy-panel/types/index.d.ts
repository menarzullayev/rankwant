export type Snapshot = {
  /** Full SHA of origin/main, or null when it could not be read. */
  main: string | null
  /** Full SHA the live site reports at /api/v1/version/, or null. */
  live: string | null
  /** Full SHA the web app reports at /version, or null. */
  web: string | null
  /** When the snapshot was taken, ms since the epoch; 0 before the first. */
  checkedAt: number
  /** When live and main were first seen to differ, ms; 0 while they match. */
  behindSince: number
  /**
   * Latest `main` push CI run as `<sha7> <conclusion|status>`, or null.
   * The gate may deploy before it finishes (decision 2026-11-10), so a red
   * one is shown even when the site matches main.
   */
  mainCi: string | null
  /** What failed on the last refresh, or null. */
  error: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'deploy-panel': { snapshot: Shaped<Snapshot> }
  }
}
