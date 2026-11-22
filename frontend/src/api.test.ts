import { afterEach, expect, it, vi } from 'vitest'
import { request } from './api'

afterEach(() => vi.unstubAllGlobals())

it('sends JSON to the analysis endpoint', async () => {
  const fetch = vi.fn().mockResolvedValue(Response.json({ what_happened: 'Demo' }))
  vi.stubGlobal('fetch', fetch)
  const body = { message: 'Test alert', language: 'english' }
  await expect(request('/api/analyze', body)).resolves.toEqual({ what_happened: 'Demo' })
  expect(fetch).toHaveBeenCalledWith(expect.stringMatching(/\/api\/analyze$/), expect.objectContaining({
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  }))
})

it('returns the server error without echoing the submitted body', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json({ detail: 'Usage limit reached.' }, { status: 429 })))
  await expect(request('/api/analyze', { message: 'Private input' })).rejects.toThrow('Usage limit reached.')
})
