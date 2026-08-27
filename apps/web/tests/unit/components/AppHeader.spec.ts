import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'

import AppHeader from '@/components/layout/AppHeader.vue'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { router } from '@/router'

async function mountHeader() {
  const wrapper = mount(AppHeader, { global: { plugins: [router] } })
  await router.isReady()
  return wrapper
}

describe('AppHeader', () => {
  beforeEach(async () => {
    await router.replace('/')
  })

  it('marks the current route for assistive technology', async () => {
    await router.push({ name: 'about' })
    const wrapper = await mountHeader()

    const current = wrapper.findAll('a[aria-current="page"]')
    expect(current.length).toBeGreaterThan(0)
    expect(current[0]?.text()).toBe('About')
  })

  it('starts with the mobile menu closed and reports its state', async () => {
    const wrapper = await mountHeader()
    const toggle = wrapper.get('button[aria-controls="mobile-navigation"]')

    expect(toggle.attributes('aria-expanded')).toBe('false')
    expect(wrapper.find('#mobile-navigation').exists()).toBe(false)
  })

  it('opens the mobile menu', async () => {
    const wrapper = await mountHeader()

    await wrapper.get('button[aria-controls="mobile-navigation"]').trigger('click')

    expect(
      wrapper.get('button[aria-controls="mobile-navigation"]').attributes('aria-expanded'),
    ).toBe('true')
    expect(wrapper.find('#mobile-navigation').exists()).toBe(true)
  })

  it('closes the mobile menu on navigation', async () => {
    // Leaving it open hides the page the visitor just asked for.
    const wrapper = await mountHeader()
    await wrapper.get('button[aria-controls="mobile-navigation"]').trigger('click')
    expect(wrapper.find('#mobile-navigation').exists()).toBe(true)

    await router.push({ name: 'contact' })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('#mobile-navigation').exists()).toBe(false)
  })

  it('closes the mobile menu on Escape', async () => {
    const wrapper = await mountHeader()
    await wrapper.get('button[aria-controls="mobile-navigation"]').trigger('click')

    await wrapper.get('header').trigger('keydown.escape')

    expect(wrapper.find('#mobile-navigation').exists()).toBe(false)
  })

  it('includes the theme control', async () => {
    const wrapper = await mountHeader()

    expect(wrapper.findComponent(ThemeToggle).exists()).toBe(true)
  })
})

describe('ThemeToggle', () => {
  it('exposes three real radio inputs in a labelled group', () => {
    // Native radios give arrow-key navigation and group semantics for free; rebuilding
    // that with ARIA is more code that works less well.
    const wrapper = mount(ThemeToggle)

    expect(wrapper.find('fieldset').exists()).toBe(true)
    expect(wrapper.find('legend').text()).toBe('Colour theme')

    const radios = wrapper.findAll('input[type="radio"]')
    expect(radios).toHaveLength(3)
    expect(radios.map((radio) => radio.attributes('value'))).toEqual(['light', 'dark', 'system'])
  })

  it('labels every option in text, not only by icon', () => {
    const wrapper = mount(ThemeToggle)

    const labels = wrapper.findAll('label span.sr-only').map((span) => span.text())
    expect(labels).toEqual(['Light', 'Dark', 'System'])
  })
})
