import { expect, test } from 'claude-code/testing'

const MAIN = 'a'.repeat(40)
const OLD = 'b'.repeat(40)

const PANE = {
  plugin: 'deploy-panel',
  component: 'Pane',
  requestId: 'deploy-panel',
  props: {
    title: 'Deploy',
    isFocused: false,
    bodyColumns: 50,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 20 },
    view: {},
  },
} as const

async function start($: any, on: any, live: string, clock: { now: number }) {
  on('command.register', () => ({ value: { command: 'deploy-panel' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('clock.now', () => ({ value: clock.now }))
  on('http.fetch', () => ({
    value: { status: 200, ok: true, headers: {}, text: JSON.stringify({ sha: live }) },
  }))
  on('process.run', () => ({
    value: { exitCode: 0, stdout: `${MAIN}\trefs/heads/main\n`, stderr: '' },
  }))
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  // session.start does not wait for the first refresh.
  await new Promise(done => setTimeout(done, 50))
}

test('matching commits read as in sync', async ($, on) => {
  await start($, on, MAIN, { now: 1_000_000 })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect(await ui.find({ type: 'Text', text: /origin\/main\s+aaaaaaa/ })).toBeTruthy()
  expect(await ui.find({ type: 'Text', text: /main bilan bir xil/ })).toBeTruthy()
  await ui.unmount()
})

test('a live site left behind for a long time is called stuck', async ($, on) => {
  const clock = { now: 10_000_000 }
  await start($, on, OLD, clock)
  clock.now += 20 * 60 * 1000
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect(await ui.find({ type: 'Text', text: /chiqmayapti/ })).toBeTruthy()
  await ui.unmount()
})

test('a short lag is only waiting', async ($, on) => {
  const clock = { now: 10_000_000 }
  await start($, on, OLD, clock)
  clock.now += 3 * 60 * 1000
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect(await ui.find({ type: 'Text', text: /deploy kutilyapti/ })).toBeTruthy()
  await ui.unmount()
})
