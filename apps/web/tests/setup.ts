import { vi } from 'vitest'

/**
 * jsdom implements no layout, so `window.scrollTo` throws a "Not implemented" notice on
 * every router navigation. It is noise, not a signal — the real scroll restoration is
 * covered end to end in Playwright, where a browser actually scrolls.
 */
vi.stubGlobal('scrollTo', vi.fn())
