import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

/**
 * The composable holds module-level state on purpose — the theme is a property of the
 * document, not of a component — so each test re-imports it to get a clean read of
 * localStorage and the media query.
 */
async function loadTheme() {
  vi.resetModules()
  return import('@/composables/useTheme')
}

function stubMatchMedia(matches: boolean) {
  vi.stubGlobal(
    'matchMedia',
    vi.fn().mockReturnValue({
      matches,
      media: '(prefers-color-scheme: dark)',
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }),
  )
}

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    stubMatchMedia(false)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('defaults to following the system', async () => {
    const { useTheme } = await loadTheme()

    expect(useTheme().theme.value).toBe('system')
  })

  it('resolves the system preference to a concrete theme', async () => {
    stubMatchMedia(true)
    const { useTheme } = await loadTheme()

    expect(useTheme().resolvedTheme.value).toBe('dark')
  })

  it('restores a stored choice', async () => {
    localStorage.setItem('portfolio-theme', 'dark')
    const { useTheme } = await loadTheme()

    expect(useTheme().theme.value).toBe('dark')
    expect(useTheme().resolvedTheme.value).toBe('dark')
  })

  it('ignores a corrupted stored value instead of breaking the page', async () => {
    localStorage.setItem('portfolio-theme', 'chartreuse')
    const { useTheme } = await loadTheme()

    expect(useTheme().theme.value).toBe('system')
  })

  it('writes the choice to the document and to storage', async () => {
    const { useTheme } = await loadTheme()
    const { setTheme } = useTheme()

    setTheme('dark')
    await vi.waitFor(() => {
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
    })
    expect(localStorage.getItem('portfolio-theme')).toBe('dark')
  })

  it('removes the attribute for system, handing control back to the media query', async () => {
    const { useTheme } = await loadTheme()
    const { setTheme } = useTheme()

    setTheme('light')
    await vi.waitFor(() => {
      expect(document.documentElement.getAttribute('data-theme')).toBe('light')
    })

    setTheme('system')
    await vi.waitFor(() => {
      expect(document.documentElement.hasAttribute('data-theme')).toBe(false)
    })
    expect(localStorage.getItem('portfolio-theme')).toBeNull()
  })

  it('survives storage being unavailable', async () => {
    // Private browsing and blocked site data both throw on access.
    const getItem = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('storage disabled')
    })

    const { useTheme } = await loadTheme()
    expect(useTheme().theme.value).toBe('system')

    getItem.mockRestore()
  })
})
