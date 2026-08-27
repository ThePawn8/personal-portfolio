import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import {
  useAsyncResource,
  type AsyncResource,
  type AsyncResourceOptions,
} from '@/composables/useAsyncResource'
import { ApiError } from '@/lib/api'

/**
 * Mounts the composable inside a throwaway component so it gets a real lifecycle — the
 * unmount behaviour is the whole point of several of these tests.
 */
function mountResource<T>(
  loader: (signal: AbortSignal) => Promise<T>,
  options?: AsyncResourceOptions<T>,
) {
  let resource!: AsyncResource<T>

  const wrapper = mount(
    defineComponent({
      setup() {
        resource = useAsyncResource(loader, options)
        return () => h('div')
      },
    }),
  )

  return { wrapper, resource: () => resource }
}

describe('useAsyncResource', () => {
  it('moves from loading to success', async () => {
    const { resource } = mountResource(() => Promise.resolve(['a']))

    expect(resource().status.value).toBe('loading')
    await flushPromises()

    expect(resource().status.value).toBe('success')
    expect(resource().data.value).toEqual(['a'])
    expect(resource().error.value).toBeNull()
    expect(resource().isStale.value).toBe(false)
  })

  it('reports an error when there is nothing to fall back to', async () => {
    const failure = new ApiError('down', { kind: 'network' })
    const { resource } = mountResource(() => Promise.reject(failure))

    await flushPromises()

    expect(resource().status.value).toBe('error')
    expect(resource().error.value).toBe(failure)
    expect(resource().data.value).toBeNull()
  })

  it('serves stale content instead of an empty page when the API is down', async () => {
    // The difference between a recruiter seeing the work and seeing a broken site.
    const { resource } = mountResource(
      () => Promise.reject(new ApiError('down', { kind: 'network' })),
      {
        fallback: () => ['cached'],
      },
    )

    await flushPromises()

    expect(resource().status.value).toBe('success')
    expect(resource().data.value).toEqual(['cached'])
    expect(resource().isStale.value).toBe(true)
    // The error is still exposed, so the UI can explain why the content may be old.
    expect(resource().error.value).not.toBeNull()
  })

  it('treats 404 as a distinct outcome, not as a failure to retry', async () => {
    const notFound = new ApiError('missing', { kind: 'http', status: 404 })
    const { resource } = mountResource(() => Promise.reject(notFound), {
      fallback: () => ['cached'],
    })

    await flushPromises()

    expect(resource().notFound.value).toBe(true)
    expect(resource().isStale.value).toBe(false)
    // A stale copy of a page that no longer exists would be worse than saying so.
    expect(resource().data.value).toBeNull()
  })

  it('aborts the in-flight request when the component unmounts', () => {
    let capturedSignal: AbortSignal | undefined
    const { wrapper } = mountResource((signal) => {
      capturedSignal = signal
      return new Promise<string[]>(() => {})
    })

    expect(capturedSignal?.aborted).toBe(false)
    wrapper.unmount()

    expect(capturedSignal?.aborted).toBe(true)
  })

  it('never updates state after unmount', async () => {
    // The classic memory-leak warning: a late response writing into a dead component.
    let resolveLoad!: (value: string[]) => void
    const { wrapper, resource } = mountResource(
      () => new Promise<string[]>((resolve) => (resolveLoad = resolve)),
    )

    wrapper.unmount()
    resolveLoad(['late'])
    await flushPromises()

    expect(resource().data.value).toBeNull()
  })

  it('discards a superseded request so responses cannot arrive out of order', async () => {
    const resolvers: ((value: string[]) => void)[] = []
    const { resource } = mountResource(
      () => new Promise<string[]>((resolve) => resolvers.push(resolve)),
    )

    void resource().reload()
    await flushPromises()

    // Answer the first (now abandoned) request last; it must not win.
    resolvers[1]?.(['second'])
    resolvers[0]?.(['first'])
    await flushPromises()

    expect(resource().data.value).toEqual(['second'])
  })

  it('can defer loading until asked', async () => {
    const loader = vi.fn(() => Promise.resolve(['a']))
    const { resource } = mountResource(loader, { immediate: false })

    await flushPromises()
    expect(loader).not.toHaveBeenCalled()
    expect(resource().status.value).toBe('idle')

    await resource().reload()
    expect(loader).toHaveBeenCalledTimes(1)
  })

  it('wraps an unexpected non-ApiError so callers only handle one type', async () => {
    const { resource } = mountResource(() => Promise.reject(new Error('boom')))

    await flushPromises()

    expect(resource().error.value).toBeInstanceOf(ApiError)
    expect(resource().status.value).toBe('error')
  })
})
