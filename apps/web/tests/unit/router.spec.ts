import { describe, expect, it } from 'vitest'

import { router } from '@/router'

describe('router', () => {
  it('resolves every named route', () => {
    const names = ['home', 'projects', 'project', 'about', 'contact', 'not-found']

    for (const name of names) {
      expect(router.hasRoute(name), `missing route: ${name}`).toBe(true)
    }
  })

  it('code-splits every route except home', () => {
    // Home is eager because it is the entry point for most visits and a round trip for its
    // chunk would delay the largest paint. Everything else must be lazy.
    const records = router.getRoutes()
    const home = records.find((record) => record.name === 'home')
    const others = records.filter((record) => record.name !== 'home')

    expect(typeof home?.components?.['default']).toBe('object')
    for (const record of others) {
      expect(typeof record.components?.['default'], `${String(record.name)} is not lazy`).toBe(
        'function',
      )
    }
  })

  it('sends unknown paths to the 404 view rather than a blank page', () => {
    const resolved = router.resolve('/no/such/page')

    expect(resolved.name).toBe('not-found')
  })

  it('passes the slug to the project detail view as a prop', () => {
    const resolved = router.resolve('/projects/checkout-revamp')

    expect(resolved.name).toBe('project')
    expect(resolved.params['slug']).toBe('checkout-revamp')
  })

  it('gives every route a title', () => {
    for (const record of router.getRoutes()) {
      expect(record.meta.title, `${String(record.name)} has no title`).toBeTruthy()
    }
  })

  it('sets the document title on navigation', async () => {
    await router.push({ name: 'about' })

    expect(document.title).toBe('About · Andrés M')
  })
})
