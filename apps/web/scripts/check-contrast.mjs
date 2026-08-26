#!/usr/bin/env node
/**
 * Verifies the design tokens meet WCAG 2.2 contrast requirements in both themes.
 *
 * A design system that claims AA and is never measured is a design system that is AA by
 * accident. This reads the actual token values out of main.css, converts OKLCH to sRGB,
 * and fails the build if any documented pairing falls below its threshold — so a palette
 * tweak cannot quietly make body text unreadable.
 *
 * Usage: npm run check:contrast
 */
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import process from 'node:process'

const CSS_PATH = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'assets', 'main.css')

/**
 * Pairings the design actually uses, with the threshold each one must meet.
 *
 * 4.5 = WCAG AA for body text and meaningful UI colour.
 * 3.0 = AA for large text (>= 24px), icons and component boundaries (1.4.11).
 * 7.0 = AAA, held for primary body text because it costs nothing here.
 */
const REQUIREMENTS = [
  { fg: 'fg', bg: 'canvas', min: 7, note: 'body text on the page' },
  { fg: 'fg', bg: 'surface', min: 7, note: 'body text on cards' },
  { fg: 'fg-muted', bg: 'canvas', min: 4.5, note: 'secondary text on the page' },
  { fg: 'fg-muted', bg: 'surface', min: 4.5, note: 'secondary text on cards' },
  { fg: 'fg-subtle', bg: 'canvas', min: 3, note: 'large/decorative text only' },
  { fg: 'accent', bg: 'canvas', min: 4.5, note: 'links on the page' },
  { fg: 'accent', bg: 'surface', min: 4.5, note: 'links on cards' },
  { fg: 'on-accent', bg: 'accent', min: 4.5, note: 'primary button label' },
  { fg: 'danger', bg: 'canvas', min: 4.5, note: 'form error text' },
  { fg: 'on-danger', bg: 'danger', min: 4.5, note: 'text on danger fill' },
  { fg: 'success', bg: 'canvas', min: 4.5, note: 'success message text' },
  { fg: 'line-strong', bg: 'canvas', min: 3, note: 'component boundaries' },
  { fg: 'ring', bg: 'canvas', min: 3, note: 'focus indicator on the page' },
  { fg: 'ring', bg: 'surface', min: 3, note: 'focus indicator on cards' },
]

/** Extract `--token: oklch(...)` declarations from one CSS block. */
function parseTokens(css, blockStart) {
  const start = css.indexOf(blockStart)
  if (start === -1) throw new Error(`block not found in main.css: ${blockStart}`)

  const open = css.indexOf('{', start)
  let depth = 0
  let end = open
  for (let i = open; i < css.length; i += 1) {
    if (css[i] === '{') depth += 1
    if (css[i] === '}') {
      depth -= 1
      if (depth === 0) {
        end = i
        break
      }
    }
  }

  const block = css.slice(open, end)
  const tokens = {}
  const pattern = /--([\w-]+):\s*oklch\(([^)]+)\)/g
  let match
  while ((match = pattern.exec(block)) !== null) {
    const [lightness, chroma, hue] = match[2].trim().split(/\s+/).map(Number)
    tokens[match[1]] = { l: lightness, c: chroma, h: hue ?? 0 }
  }
  return tokens
}

/** OKLCH -> linear sRGB. Coefficients from the Oklab specification. */
function oklchToLinearRgb({ l: lightness, c: chroma, h: hue }) {
  const hueRad = (hue * Math.PI) / 180
  const a = chroma * Math.cos(hueRad)
  const b = chroma * Math.sin(hueRad)

  const lCone = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
  const mCone = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
  const sCone = (lightness - 0.0894841775 * a - 1.291485548 * b) ** 3

  return [
    4.0767416621 * lCone - 3.3077115913 * mCone + 0.2309699292 * sCone,
    -1.2684380046 * lCone + 2.6097574011 * mCone - 0.3413193965 * sCone,
    -0.0041960863 * lCone - 0.7034186147 * mCone + 1.707614701 * sCone,
  ].map((channel) => Math.min(1, Math.max(0, channel)))
}

/** WCAG relative luminance, computed from linear-light values. */
function relativeLuminance(token) {
  const [r, g, b] = oklchToLinearRgb(token)
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function contrastRatio(foreground, background) {
  const a = relativeLuminance(foreground)
  const b = relativeLuminance(background)
  const [lighter, darker] = a > b ? [a, b] : [b, a]
  return (lighter + 0.05) / (darker + 0.05)
}

const css = readFileSync(CSS_PATH, 'utf8')
const themes = {
  light: parseTokens(css, ':root {'),
  dark: parseTokens(css, ":root[data-theme='dark'] {"),
}

const bold = (text) => `\x1b[1m${text}\x1b[0m`
const green = (text) => `\x1b[32m${text}\x1b[0m`
const red = (text) => `\x1b[31m${text}\x1b[0m`
const dim = (text) => `\x1b[2m${text}\x1b[0m`

let failures = 0

for (const [themeName, tokens] of Object.entries(themes)) {
  console.log(`\n${bold(themeName)}`)

  for (const { fg, bg, min, note } of REQUIREMENTS) {
    const foreground = tokens[fg]
    const background = tokens[bg]
    if (!foreground || !background) {
      console.log(`  ${red('MISSING')} --${fg} on --${bg}`)
      failures += 1
      continue
    }

    const ratio = contrastRatio(foreground, background)
    const passed = ratio >= min
    if (!passed) failures += 1

    const label = `${fg} on ${bg}`.padEnd(30)
    const value = `${ratio.toFixed(2)}:1`.padStart(8)
    const marker = passed ? green('PASS') : red('FAIL')
    console.log(`  ${marker} ${label}${value}  ${dim(`min ${min}  ${note}`)}`)
  }
}

// The dark theme is duplicated into a prefers-color-scheme block for users who have not
// chosen explicitly. If the two ever drift, half the audience gets an unverified palette.
const systemDark = parseTokens(css, ":root:not([data-theme='light'])")
const drifted = Object.keys(themes.dark).filter((token) => {
  const explicit = themes.dark[token]
  const system = systemDark[token]
  return !system || system.l !== explicit.l || system.c !== explicit.c || system.h !== explicit.h
})

if (drifted.length > 0) {
  console.log(`\n${red('FAIL')} dark tokens differ from the prefers-color-scheme block:`)
  for (const token of drifted) console.log(`  --${token}`)
  failures += drifted.length
} else {
  console.log(`\n${green('PASS')} dark theme and system-preference block are identical`)
}

if (failures > 0) {
  console.error(`\n${red(`${failures} contrast requirement(s) not met`)}`)
  process.exit(1)
}

console.log(`\n${green('All contrast requirements met in both themes.')}`)
