import type { ContactSubmission, Problem, Profile, Project, ProjectSummary } from '@/types/api'

/**
 * Typed HTTP client.
 *
 * Native `fetch` with three things added: a timeout, a single error type, and no silent
 * `any`. There is no HTTP library because there is nothing here a library would do better —
 * the API has six endpoints and one error shape.
 */

const BASE_URL = (import.meta.env['VITE_API_BASE_URL'] ?? 'http://localhost:8000').replace(
  /\/$/,
  '',
)

/** Long enough for a cold container on Fly, short enough that nobody watches a spinner. */
export const DEFAULT_TIMEOUT_MS = 5000

/**
 * Every failure the client can produce, as one type.
 *
 * `problem` is present when the server answered with RFC 9457 details; it is absent for
 * transport failures, where there was no answer at all. Callers can therefore distinguish
 * "the API said no" from "the API never replied" without parsing strings.
 */
export class ApiError extends Error {
  readonly status: number
  readonly problem: Problem | undefined
  readonly kind: 'http' | 'network' | 'timeout' | 'aborted'

  constructor(
    message: string,
    options: { status?: number; problem?: Problem; kind: ApiError['kind'] },
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = options.status ?? 0
    this.problem = options.problem
    this.kind = options.kind
  }

  /** True when retrying could plausibly succeed. Used by the UI to offer a retry. */
  get isRetryable(): boolean {
    return this.kind === 'network' || this.kind === 'timeout' || this.status >= 500
  }
}

function isProblem(value: unknown): value is Problem {
  if (typeof value !== 'object' || value === null) return false
  const candidate = value as Record<string, unknown>
  return typeof candidate['title'] === 'string' && typeof candidate['status'] === 'number'
}

/**
 * Combine the caller's abort signal with the timeout.
 *
 * `AbortSignal.any` would do this in one line but is not available in every runtime the
 * unit tests run in, and a polyfill for eight lines of logic is not a trade worth making.
 */
function withTimeout(signal: AbortSignal | undefined, timeoutMs: number) {
  const controller = new AbortController()
  const timer = setTimeout(
    () => controller.abort(new DOMException('timeout', 'TimeoutError')),
    timeoutMs,
  )

  const abortFromCaller = () => controller.abort(signal?.reason)
  if (signal) {
    if (signal.aborted) abortFromCaller()
    else signal.addEventListener('abort', abortFromCaller, { once: true })
  }

  return {
    signal: controller.signal,
    cleanup: () => {
      clearTimeout(timer)
      signal?.removeEventListener('abort', abortFromCaller)
    },
  }
}

export interface RequestOptions {
  /** Aborts the request — pass the component's unmount signal. */
  signal?: AbortSignal
  timeoutMs?: number
  method?: 'GET' | 'POST'
  body?: unknown
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { signal, cleanup } = withTimeout(options.signal, options.timeoutMs ?? DEFAULT_TIMEOUT_MS)

  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method: options.method ?? 'GET',
      signal,
      headers: {
        Accept: 'application/json',
        ...(options.body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      ...(options.body === undefined ? {} : { body: JSON.stringify(options.body) }),
    })
  } catch (error) {
    // A caller-initiated abort is not a failure — it means the component went away.
    if (options.signal?.aborted) {
      throw new ApiError('Request aborted', { kind: 'aborted' })
    }
    if (error instanceof DOMException && error.name === 'TimeoutError') {
      throw new ApiError(`Request to ${path} timed out`, { kind: 'timeout' })
    }
    throw new ApiError(`Could not reach the API`, { kind: 'network' })
  } finally {
    cleanup()
  }

  if (!response.ok) {
    // The body should be problem+json, but an outage can put a proxy's HTML in its place —
    // so parsing failure must not replace the real status with a parse error.
    let problem: Problem | undefined
    try {
      const payload: unknown = await response.json()
      if (isProblem(payload)) problem = payload
    } catch {
      problem = undefined
    }

    throw new ApiError(problem?.detail ?? `Request to ${path} failed (${response.status})`, {
      status: response.status,
      kind: 'http',
      ...(problem === undefined ? {} : { problem }),
    })
  }

  if (response.status === 204) return undefined as T

  return (await response.json()) as T
}

export const api = {
  getProjects: (options?: RequestOptions) => request<ProjectSummary[]>('/api/v1/projects', options),

  getProject: (slug: string, options?: RequestOptions) =>
    request<Project>(`/api/v1/projects/${encodeURIComponent(slug)}`, options),

  getProfile: (options?: RequestOptions) => request<Profile>('/api/v1/profile', options),

  submitContact: (submission: ContactSubmission, options?: RequestOptions) =>
    request<void>('/api/v1/contact', { ...options, method: 'POST', body: submission }),
}
