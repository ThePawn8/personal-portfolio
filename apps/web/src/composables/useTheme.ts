import { computed, readonly, ref, watch } from 'vue'

/**
 * Colour theme selection.
 *
 * Three states, not two. `system` is a real choice — it means "keep following my operating
 * system", including when the OS switches at sunset. Collapsing it into a light/dark toggle
 * silently opts the visitor out of that, which is why the toggle offers all three.
 *
 * The initial `data-theme` attribute is set by an inline script in index.html, before the
 * bundle loads, so the page never paints in the wrong theme. This module takes over from
 * there and keeps the attribute in sync.
 */
export type Theme = 'light' | 'dark' | 'system'
export type ResolvedTheme = 'light' | 'dark'

export const THEME_STORAGE_KEY = 'portfolio-theme'

const DARK_QUERY = '(prefers-color-scheme: dark)'

function isTheme(value: unknown): value is Theme {
  return value === 'light' || value === 'dark' || value === 'system'
}

function readStoredTheme(): Theme {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    return isTheme(stored) ? stored : 'system'
  } catch {
    // Private mode and blocked site data both throw here. A theme is not worth an error.
    return 'system'
  }
}

function prefersDark(): boolean {
  return typeof window !== 'undefined' && window.matchMedia?.(DARK_QUERY).matches === true
}

// Module-level state: the theme is a property of the document, not of any one component,
// so every consumer must observe the same value.
const theme = ref<Theme>(readStoredTheme())
const systemPrefersDark = ref(prefersDark())

const resolvedTheme = computed<ResolvedTheme>(() => {
  if (theme.value !== 'system') return theme.value
  return systemPrefersDark.value ? 'dark' : 'light'
})

function applyTheme(value: Theme): void {
  const root = document.documentElement
  if (value === 'system') {
    // Removing the attribute hands control back to the prefers-color-scheme media query.
    root.removeAttribute('data-theme')
  } else {
    root.setAttribute('data-theme', value)
  }
}

function persistTheme(value: Theme): void {
  try {
    if (value === 'system') {
      localStorage.removeItem(THEME_STORAGE_KEY)
    } else {
      localStorage.setItem(THEME_STORAGE_KEY, value)
    }
  } catch {
    // Storage being unavailable degrades to a per-session choice, which is fine.
  }
}

let listening = false

function startListening(): void {
  if (listening || typeof window === 'undefined' || !window.matchMedia) return
  listening = true

  window.matchMedia(DARK_QUERY).addEventListener('change', (event) => {
    systemPrefersDark.value = event.matches
  })

  watch(theme, (value) => {
    applyTheme(value)
    persistTheme(value)
  })
}

export function useTheme() {
  startListening()

  return {
    theme: readonly(theme),
    resolvedTheme,
    setTheme: (value: Theme) => {
      theme.value = value
    },
  }
}
