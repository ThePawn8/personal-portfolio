import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError, api, request } from '@/lib/api'
import type { Problem } from '@/types/api'

const PROBLEM: Problem = {
  type: 'https://example.test/errors#project-not-found',
  title: 'Project not found',
  status: 404,
  detail: 'No published project exists with that slug.',
  instance: '/api/v1/projects/nope',
  requestId: '01JC4Z8K7Q3M9XKQ0F8W2E5T1V',
}

function jsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
}

/** Never settles until aborted — the shape of a hung request. */
function hangingFetch() {
  return vi.fn((_url: string, init: RequestInit) => {
    return new Promise<Response>((_resolve, reject) => {
      init.signal?.addEventListener('abort', () => {
        // Keep the original reason: the client distinguishes a timeout from an abort by
        // its name, and `instanceof Error` is unreliable across realms in jsdom.
        const reason = (init.signal?.reason ?? new DOMException('aborted', 'AbortError')) as Error
        reject(reason)
      })
    })
  })
}

describe('request', () => {
  const fetchMock = vi.fn()

  beforeEach(() => {
    fetchMock.mockReset()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns parsed JSON on success', async () => {
    fetchMock.mockResolvedValue(jsonResponse([{ slug: 'a' }]))

    await expect(request('/api/v1/projects')).resolves.toEqual([{ slug: 'a' }])
  })

  it('prefixes the configured base URL', async () => {
    fetchMock.mockResolvedValue(jsonResponse({}))

    await request('/api/v1/profile')

    expect(fetchMock.mock.calls[0]?.[0]).toMatch(/\/api\/v1\/profile$/)
    expect(fetchMock.mock.calls[0]?.[0]).not.toMatch(/\/\/api/)
  })

  it('sends a JSON body only when there is one', async () => {
    // A fresh Response per call: a body can only be read once.
    fetchMock.mockImplementation(() => Promise.resolve(jsonResponse({})))

    await request('/api/v1/contact', { method: 'POST', body: { name: 'A' } })
    const [, postInit] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(postInit.method).toBe('POST')
    expect(postInit.body).toBe('{"name":"A"}')
    expect((postInit.headers as Record<string, string>)['Content-Type']).toBe('application/json')

    fetchMock.mockClear()
    await request('/api/v1/projects')
    const [, getInit] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(getInit.body).toBeUndefined()
    expect((getInit.headers as Record<string, string>)['Content-Type']).toBeUndefined()
  })

  it('turns a problem+json response into a typed error', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(PROBLEM, {
        status: 404,
        headers: { 'Content-Type': 'application/problem+json' },
      }),
    )

    const error = await request('/api/v1/projects/nope').catch((caught: unknown) => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(404)
    expect((error as ApiError).kind).toBe('http')
    expect((error as ApiError).problem).toEqual(PROBLEM)
    expect((error as ApiError).message).toBe(PROBLEM.detail)
  })

  it('survives an error body that is not problem+json', async () => {
    // An outage can put a proxy's HTML error page where the API's JSON should be; the real
    // status must not be replaced by a JSON parse failure.
    fetchMock.mockResolvedValue(new Response('<html>502 Bad Gateway</html>', { status: 502 }))

    const error = (await request('/api/v1/projects').catch((caught: unknown) => caught)) as ApiError

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(502)
    expect(error.problem).toBeUndefined()
    expect(error.isRetryable).toBe(true)
  })

  it('reports an unreachable API as a retryable network error', async () => {
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'))

    const error = (await request('/api/v1/projects').catch((caught: unknown) => caught)) as ApiError

    expect(error.kind).toBe('network')
    expect(error.isRetryable).toBe(true)
  })

  it('times out rather than hanging forever', async () => {
    fetchMock.mockImplementation(hangingFetch())

    const error = (await request('/api/v1/projects', { timeoutMs: 5 }).catch(
      (caught: unknown) => caught,
    )) as ApiError

    expect(error.kind).toBe('timeout')
    expect(error.isRetryable).toBe(true)
  })

  it('distinguishes a caller abort from a failure', async () => {
    // A component unmounting is not an error, and must not be reported as one.
    fetchMock.mockImplementation(hangingFetch())
    const controller = new AbortController()

    const pending = request('/api/v1/projects', { signal: controller.signal }).catch(
      (caught: unknown) => caught,
    )
    controller.abort()

    const error = (await pending) as ApiError
    expect(error.kind).toBe('aborted')
    expect(error.isRetryable).toBe(false)
  })

  it('does not treat a 4xx as retryable', async () => {
    fetchMock.mockResolvedValue(jsonResponse(PROBLEM, { status: 404 }))

    const error = (await request('/x').catch((caught: unknown) => caught)) as ApiError

    expect(error.isRetryable).toBe(false)
  })
})

describe('api endpoints', () => {
  const fetchMock = vi.fn()

  beforeEach(() => {
    fetchMock.mockReset()
    fetchMock.mockImplementation(() => Promise.resolve(jsonResponse({})))
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('escapes the slug so a hostile path cannot rewrite the URL', async () => {
    await api.getProject('../../admin')

    expect(fetchMock.mock.calls[0]?.[0]).toContain('%2F')
  })

  it.each([
    ['getProjects', () => api.getProjects(), '/api/v1/projects'],
    ['getProfile', () => api.getProfile(), '/api/v1/profile'],
  ])('%s calls %s', async (_name, call, path) => {
    await call()

    expect(fetchMock.mock.calls[0]?.[0]).toContain(path)
  })

  it('posts a contact submission', async () => {
    await api.submitContact({ name: 'A', email: 'a@b.co', message: 'hello there' })

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain('/api/v1/contact')
    expect(init.method).toBe('POST')
  })
})
