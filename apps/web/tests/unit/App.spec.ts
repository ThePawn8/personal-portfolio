import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'

import App from '@/App.vue'
import { router } from '@/router'

async function mountApp() {
  const wrapper = mount(App, { global: { plugins: [router] } })
  await router.isReady()
  await wrapper.vm.$nextTick()
  return wrapper
}

describe('App shell', () => {
  beforeEach(async () => {
    await router.replace('/')
  })

  it('renders the landmark structure a screen reader navigates by', async () => {
    const wrapper = await mountApp()

    expect(wrapper.find('header').exists()).toBe(true)
    expect(wrapper.find('main#main-content').exists()).toBe(true)
    expect(wrapper.find('footer').exists()).toBe(true)
    expect(wrapper.findAll('nav[aria-label="Main"]').length).toBeGreaterThan(0)
  })

  it('puts a skip link first, targeting the main landmark', async () => {
    const wrapper = await mountApp()

    // First focusable element on the page, or a keyboard user tabs the whole nav on
    // every single route.
    const skipLink = wrapper.find('a.skip-link')
    expect(skipLink.exists()).toBe(true)
    expect(skipLink.attributes('href')).toBe('#main-content')
    expect(wrapper.find(skipLink.attributes('href') as string).exists()).toBe(true)
  })

  it('renders exactly one level-1 heading per route', async () => {
    const wrapper = await mountApp()

    expect(wrapper.findAll('h1')).toHaveLength(1)
  })

  it('swaps the view on navigation', async () => {
    const wrapper = await mountApp()
    expect(wrapper.find('h1').text()).toBe('Andrés M')

    await router.push({ name: 'contact' })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('h1').text()).toBe('Contact')
  })
})
