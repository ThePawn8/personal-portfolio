import { onMounted, onScopeDispose, readonly, ref, shallowRef, type Ref } from 'vue'

import { ApiError } from '@/lib/api'

export type ResourceStatus = 'idle' | 'loading' | 'success' | 'error'

export interface AsyncResource<T> {
  data: Readonly<Ref<T | null>>
  status: Readonly<Ref<ResourceStatus>>
  error: Readonly<Ref<ApiError | null>>
  /** True when `data` came from the build-time snapshot rather than the API. */
  isStale: Readonly<Ref<boolean>>
  /** True when the API explicitly said the resource does not exist. */
  notFound: Readonly<Ref<boolean>>
  reload: () => Promise<void>
}

export interface AsyncResourceOptions<T> {
  /** Content to show when the API cannot be reached. Returning `null` means none exists. */
  fallback?: () => T | null
  /** Load immediately on mount. Off for resources triggered by user action. */
  immediate?: boolean
}

/**
 * One loading state machine for every remote resource.
 *
 * Written once so that "loading", "failed", "stale" and "not found" mean the same thing on
 * every page. Views that hand-roll this end up with four subtly different empty states, and
 * the one that matters — the API being down — is invariably the one nobody styled.
 *
 * The in-flight request is aborted when the owning scope is disposed, so a component that
 * unmounts mid-request cannot update state afterwards.
 */
export function useAsyncResource<T>(
  loader: (signal: AbortSignal) => Promise<T>,
  options: AsyncResourceOptions<T> = {},
): AsyncResource<T> {
  const data = shallowRef<T | null>(null)
  const status = ref<ResourceStatus>('idle')
  const error = shallowRef<ApiError | null>(null)
  const isStale = ref(false)
  const notFound = ref(false)

  let controller: AbortController | null = null

  async function reload(): Promise<void> {
    // A newer request supersedes an older one; leaving both in flight makes the response
    // order decide what the user sees.
    controller?.abort()
    controller = new AbortController()
    const currentController = controller

    status.value = 'loading'
    error.value = null
    notFound.value = false

    try {
      const result = await loader(currentController.signal)
      if (currentController.signal.aborted) return

      data.value = result
      isStale.value = false
      status.value = 'success'
    } catch (caught) {
      if (currentController.signal.aborted) return

      const apiError =
        caught instanceof ApiError
          ? caught
          : new ApiError('Unexpected client error', { kind: 'network' })

      if (apiError.kind === 'aborted') return

      if (apiError.status === 404) {
        notFound.value = true
        error.value = apiError
        status.value = 'error'
        return
      }

      const fallbackContent = options.fallback?.() ?? null
      if (fallbackContent !== null) {
        data.value = fallbackContent
        isStale.value = true
        status.value = 'success'
        error.value = apiError
        return
      }

      error.value = apiError
      status.value = 'error'
    }
  }

  if (options.immediate !== false) {
    onMounted(() => {
      void reload()
    })
  }

  onScopeDispose(() => {
    controller?.abort()
  })

  return {
    // `data` and `error` are returned unwrapped: Vue's `readonly()` produces a
    // `DeepReadonly<T>`, which would make every consumer treat the payload as deeply
    // immutable and fight the types. The interface already declares them read-only, which
    // is what actually guides callers.
    data,
    error,
    status: readonly(status),
    isStale: readonly(isStale),
    notFound: readonly(notFound),
    reload,
  }
}
