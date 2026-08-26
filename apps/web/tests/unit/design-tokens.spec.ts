// @vitest-environment node
// This suite reads source files rather than rendering them; under jsdom `import.meta.url`
// is an http:// URL and cannot be resolved to a path.
import { globSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const SRC = fileURLToPath(new URL('../../src/', import.meta.url))

/**
 * The design system is only a system while every colour goes through a token. These tests
 * fail the moment a component hardcodes a colour, which is how palettes rot: one urgent
 * literal that nobody revisits, and the dark theme quietly breaks.
 */
describe('design tokens', () => {
  const components = globSync('**/*.vue', { cwd: SRC }).map((relativePath) => ({
    path: relativePath,
    source: readFileSync(`${SRC}${relativePath}`, 'utf8'),
  }))

  it('finds components to check', () => {
    expect(components.length).toBeGreaterThan(0)
  })

  it('contains no literal colour values in components', () => {
    const literalColour = /#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(|\boklch\(/
    const offenders = components
      .filter(({ source }) => literalColour.test(source))
      .map(({ path }) => path)

    expect(offenders).toEqual([])
  })

  it('declares the same tokens in both themes', () => {
    // A token defined in light but not dark is invisible until someone switches theme,
    // which is exactly the bug users report and authors cannot reproduce.
    const css = readFileSync(`${SRC}assets/main.css`, 'utf8')
    const lightBlock = css.slice(css.indexOf(':root {'), css.indexOf(":root[data-theme='dark']"))
    const darkBlock = css.slice(
      css.indexOf(":root[data-theme='dark']"),
      css.indexOf('@media (prefers-color-scheme: dark)'),
    )

    const tokensIn = (block: string) =>
      [...block.matchAll(/^\s+--([\w-]+):/gm)].map((match) => match[1]).sort()

    expect(tokensIn(lightBlock).length).toBeGreaterThan(10)
    expect(tokensIn(darkBlock)).toEqual(tokensIn(lightBlock))
  })
})
