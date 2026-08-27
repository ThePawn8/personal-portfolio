import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, h, ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type * as ApiModule from '@/lib/api'

import { useProject, useProjects } from '@/composables/useProjects'
import { ApiError } from '@/lib/api'
import type { ProjectSummary } from '@/types/api'

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual<typeof ApiModule>('@/lib/api')
  return {
    ...actual,
    api: {
      getProjects: vi.fn(),
      getProject: vi.fn(),
      getProfile: vi.fn(),
      submitContact: vi.fn(),
    },
  }
})

const { api } = await import('@/lib/api')

function project(overrides: Partial<ProjectSummary> = {}): ProjectSummary {
  return {
    slug: 'a',
    title: 'A',
    summary: 'Summary',
    kind: 'professional',
    role: 'Frontend Developer',
    period: { start: '2024-01', end: null },
    stack: ['vue'],
    tags: ['frontend'],
    featured: false,
    order: 100,
    confidential: false,
    links: {},
    metrics: [],
    mockups: [],
    ...overrides,
  }
}

function mountComposable<T>(composable: () => T) {
  let result!: T
  const wrapper = mount(
    defineComponent({
      setup() {
        result = composable()
        return () => h('div')
      },
    }),
  )
  return { wrapper, result: () => result }
}

describe('useProjects', () => {
  beforeEach(() => {
    vi.mocked(api.getProjects).mockReset()
    vi.mocked(api.getProject).mockReset()
  })

  it('exposes an empty list rather than null while loading', () => {
    vi.mocked(api.getProjects).mockReturnValue(new Promise(() => {}))

    const { result } = mountComposable(() => useProjects())

    // Views can iterate immediately; no `v-if="projects"` guard on every template.
    expect(result().projects.value).toEqual([])
  })

  it('derives the featured subset and the tag list', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([
      project({ slug: 'a', featured: true, tags: ['frontend', 'performance'] }),
      project({ slug: 'b', featured: false, tags: ['frontend'] }),
    ])

    const { result } = mountComposable(() => useProjects())
    await flushPromises()

    expect(result().projects.value).toHaveLength(2)
    expect(result().featured.value.map((item) => item.slug)).toEqual(['a'])
    expect(result().allTags.value).toEqual(['frontend', 'performance'])
  })

  it('falls back to the bundled snapshot when the API is unreachable', async () => {
    vi.mocked(api.getProjects).mockRejectedValue(new ApiError('down', { kind: 'network' }))

    const { result } = mountComposable(() => useProjects())
    await flushPromises()

    // The snapshot ships empty until T-404 generates it, so there is nothing to show and
    // an honest error beats pretending the portfolio is empty.
    expect(result().status.value).toBe('error')
    expect(result().isStale.value).toBe(false)
  })
})

describe('useProject', () => {
  beforeEach(() => {
    vi.mocked(api.getProject).mockReset()
  })

  it('requests the slug it was given', async () => {
    vi.mocked(api.getProject).mockResolvedValue({ ...project({ slug: 'x' }), bodyHtml: '<p>x</p>' })

    mountComposable(() => useProject('x'))
    await flushPromises()

    expect(vi.mocked(api.getProject).mock.calls[0]?.[0]).toBe('x')
  })

  it('reloads when the slug changes', async () => {
    vi.mocked(api.getProject).mockResolvedValue({ ...project(), bodyHtml: '' })
    const slug = ref('first')

    mountComposable(() => useProject(slug))
    await flushPromises()

    slug.value = 'second'
    await flushPromises()

    expect(vi.mocked(api.getProject).mock.calls.map((call) => call[0])).toEqual(['first', 'second'])
  })

  it('marks an unknown slug as not found instead of as a failure', async () => {
    vi.mocked(api.getProject).mockRejectedValue(
      new ApiError('missing', { kind: 'http', status: 404 }),
    )

    const { result } = mountComposable(() => useProject('nope'))
    await flushPromises()

    expect(result().notFound.value).toBe(true)
  })
})
