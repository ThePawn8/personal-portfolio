import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import App from '@/App.vue'
import { RELOAD_FLAG, handleNavigationError, router } from '@/router'

const PAGES = [
  { path: '/', heading: 'Andrés M' },
  { path: '/projects', heading: 'Work' },
  { path: '/projects/checkout-revamp', heading: 'checkout-revamp' },
  { path: '/about', heading: 'About' },
  { path: '/contact', heading: 'Contact' },
  { path: '/nope', heading: 'Page not found' },
]

describe('every route renders', () => {
  it.each(PAGES)('$path renders exactly one h1: $heading', async ({ path, heading }) => {
    // Mounting each route for real also loads its lazy chunk, which is the only way to
    // catch a view that fails to import or throws on setup.
    const wrapper = mount(App, { global: { plugins: [router] } })
    await router.isReady()
    await router.replace(path)
    await wrapper.vm.$nextTick()

    const headings = wrapper.findAll('h1')
    expect(headings).toHaveLength(1)
    expect(headings[0]?.text()).toBe(heading)
  })
})

describe('scroll behaviour', () => {
  const scrollBehavior = router.options.scrollBehavior

  /** A real navigation, so the route passed in is the same shape the router produces. */
  async function navigateTo(path: string) {
    await router.replace(path)
    return router.currentRoute.value
  }

  it('restores the previous position on back and forward', async () => {
    // Without this, every back navigation on a long page dumps the reader at the top.
    const saved = { left: 0, top: 420 }
    const to = await navigateTo('/projects')

    const result = await scrollBehavior?.(to, to, saved)

    expect(result).toEqual(saved)
  })

  it('scrolls to an anchor when the URL has a hash', async () => {
    const to = await navigateTo('/about#experience')

    const result = await scrollBehavior?.(to, to, null)

    expect(result).toEqual({ el: '#experience', behavior: 'smooth' })
  })

  it('starts a new page at the top', async () => {
    const to = await navigateTo('/contact')

    const result = await scrollBehavior?.(to, to, null)

    expect(result).toEqual({ top: 0 })
  })
})

describe('recovery from a stale chunk after a deploy', () => {
  const assign = vi.fn()

  beforeEach(() => {
    sessionStorage.clear()
    assign.mockClear()
    vi.stubGlobal('location', { assign, href: 'http://localhost/' })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('reloads once when a chunk no longer exists', () => {
    const error = new Error('Failed to fetch dynamically imported module: /assets/About.js')

    const reloaded = handleNavigationError(error, '/about')

    expect(reloaded).toBe(true)
    expect(assign).toHaveBeenCalledWith('/about')
    expect(sessionStorage.getItem(RELOAD_FLAG)).toBe('1')
  })

  it('does not reload twice, so a persistent failure cannot loop', () => {
    const error = new Error('Failed to fetch dynamically imported module: /assets/About.js')

    handleNavigationError(error, '/about')
    const secondAttempt = handleNavigationError(error, '/about')

    expect(secondAttempt).toBe(false)
    expect(assign).toHaveBeenCalledTimes(1)
  })

  it('leaves unrelated navigation errors alone', () => {
    const reloaded = handleNavigationError(new Error('guard rejected'), '/about')

    expect(reloaded).toBe(false)
    expect(assign).not.toHaveBeenCalled()
  })

  it('does nothing when storage is unavailable rather than throwing', () => {
    const getItem = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('storage disabled')
    })

    const reloaded = handleNavigationError(new Error('Importing a module script failed'), '/about')

    expect(reloaded).toBe(false)
    expect(assign).not.toHaveBeenCalled()
    getItem.mockRestore()
  })
})
