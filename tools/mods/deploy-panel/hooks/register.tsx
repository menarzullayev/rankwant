import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Snapshot } from '../types'

const PANE = 'deploy-panel'
const VERSION_URL = 'https://rankwant.uz/api/v1/version/'
// The watcher polls once a minute and CI takes a few; past this the deploy is
// not merely in flight (2026-10-23: a dead lock held it for two days).
const STUCK_AFTER_MS = 15 * 60 * 1000
// A turn can end every few seconds; do not hit the network that often.
const MIN_GAP_MS = 30 * 1000

const EMPTY: Snapshot = {
  main: null,
  live: null,
  checkedAt: 0,
  behindSince: 0,
  error: null,
}
// Change the tag when Snapshot's fields change: it declines what an earlier
// version stored, which outlives a reload.
const snapshot = atom({ plugin: 'deploy-panel', key: 'snapshot' } as const, EMPTY, {
  shape: 'snapshot-1',
})

const short = (sha: string | null) => (sha ? sha.slice(0, 7) : 'noma’lum')

async function refresh($: any, cwd?: string): Promise<Snapshot> {
  const now: number = await $.clock.now()
  const errors: string[] = []

  let live: string | null = null
  try {
    const res = await $.http.fetch(VERSION_URL)
    const sha = res.ok ? JSON.parse(res.text)?.sha : null
    if (typeof sha === 'string' && /^[0-9a-f]{7,40}$/.test(sha)) {
      live = sha
    } else {
      errors.push(`sayt: ${res.ok ? 'sha yo‘q' : `HTTP ${res.status}`}`)
    }
  } catch (err) {
    errors.push(`sayt: ${String(err)}`)
  }

  let main: string | null = null
  try {
    const run = await $.process.run(
      ['git', 'ls-remote', 'origin', 'refs/heads/main'],
      { cwd, timeoutMs: 15000 },
    )
    const sha = run.exitCode === 0 ? run.stdout.split(/\s+/)[0] : ''
    if (/^[0-9a-f]{40}$/.test(sha)) {
      main = sha
    } else {
      errors.push(`git: kod ${run.exitCode}`)
    }
  } catch (err) {
    errors.push(`git: ${String(err)}`)
  }

  return update($, snapshot, (prev: Snapshot) => {
    const isBehind = main !== null && live !== null && main !== live
    // Keep the first sighting of a difference; clear it when they match.
    // An unreadable side changes nothing: it is not evidence either way.
    const behindSince =
      main === null || live === null
        ? prev.behindSince
        : isBehind
          ? prev.behindSince || now
          : 0

    return {
      main,
      live,
      checkedAt: now,
      behindSince,
      error: errors.length ? errors.join('; ') : null,
    }
  })
}

function verdict(s: Snapshot, now: number) {
  if (s.checkedAt === 0) return { label: 'tekshirilmagan', tone: 'dim' } as const
  if (s.main === null || s.live === null) {
    return { label: 'o‘qilmadi', tone: 'dim' } as const
  }
  if (s.main === s.live) return { label: 'jonli sayt main bilan bir xil', tone: 'ok' } as const
  const minutes = Math.floor((now - s.behindSince) / 60000)
  return minutes * 60000 >= STUCK_AFTER_MS
    ? ({ label: `deploy ${minutes} daqiqadan beri chiqmayapti`, tone: 'bad' } as const)
    : ({ label: `deploy kutilyapti (${minutes} daqiqa)`, tone: 'warn' } as const)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'deploy-panel',
      description: 'Show origin/main against the commit the live site runs',
    })
    void $.ui.open({ id: PANE, title: 'Deploy' })
    void refresh($, e.cwd)

    return next(e)
  })

  on('command.run', { command: 'deploy-panel' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Deploy' })
    const s = await refresh($)
    const v = verdict(s, await $.clock.now())

    return {
      text: `main ${short(s.main)}, jonli ${short(s.live)}: ${v.label}`,
    }
  })

  on('turn.complete', async ($, e, next) => {
    const s = await read($, snapshot)
    if ((await $.clock.now()) - s.checkedAt > MIN_GAP_MS) {
      void refresh($)
    }

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Text } = $.ui.resolve(e)
    const s = await read($, snapshot)
    const v = verdict(s, await $.clock.now())
    const color =
      v.tone === 'ok' ? 'green' : v.tone === 'warn' ? 'yellow' : v.tone === 'bad' ? 'red' : undefined

    return (
      <Box flexDirection="column">
        <Text>origin/main  {short(s.main)}</Text>
        <Text>jonli sayt   {short(s.live)}</Text>
        <Text color={color} dimColor={v.tone === 'dim'}>
          {v.label}
        </Text>
        {s.error && <Text dimColor>{s.error}</Text>}
        <Button key="refresh" label="Yangilash" onPress={() => void refresh($)} />
      </Box>
    )
  })
}
