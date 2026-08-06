import assert from 'node:assert/strict'
import test from 'node:test'

import {
  replaceActivityBlock,
  renderActivity,
} from '../.github/scripts/update-activity.mjs'

const repo = { name: 'YanleiZhao-lab/example' }
const events = [
  { type: 'PushEvent', repo, payload: { commits: [{}, {}] } },
  { type: 'IssuesEvent', repo, payload: { action: 'opened', issue: { number: 12 } } },
  { type: 'PullRequestEvent', repo, payload: { action: 'opened', pull_request: { number: 7 } } },
  { type: 'CreateEvent', repo, payload: { ref_type: 'branch', ref: 'feature' } },
  { type: 'ForkEvent', repo, payload: { forkee: { full_name: 'YanleiZhao-lab/example-fork' } } },
  { type: 'ReleaseEvent', repo, payload: { action: 'published', release: { tag_name: 'v1.0.0' } } },
  { type: 'WatchEvent', repo, payload: { action: 'started' } },
]

test('renderActivity formats supported events and limits output', () => {
  const output = renderActivity(events, 5)

  assert.match(output, /Pushed 2 commits/)
  assert.match(output, /YanleiZhao-lab\/example/)
  assert.match(output, /Opened issue #12/)
  assert.match(output, /Opened pull request #7/)
  assert.equal(output.trim().split('\n').length, 5)
})

test('replaceActivityBlock only replaces marked content', () => {
  const source = [
    '# Profile',
    '<!--RECENT_ACTIVITY:start-->',
    'old activity',
    '<!--RECENT_ACTIVITY:end-->',
    'footer',
  ].join('\n')

  const updated = replaceActivityBlock(source, '- new activity')

  assert.match(updated, /^# Profile/)
  assert.match(updated, /<!--RECENT_ACTIVITY:start-->\n- new activity\n<!--RECENT_ACTIVITY:end-->/)
  assert.match(updated, /footer$/)
})

test('replaceActivityBlock fails when markers are missing', () => {
  assert.throws(() => replaceActivityBlock('# Profile', '- item'), /markers/i)
})
