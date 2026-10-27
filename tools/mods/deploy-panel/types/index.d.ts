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
  /** What failed on the last refresh, or null. */
  error: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'deploy-panel': { snapshot: Shaped<Snapshot> }
  }
}
