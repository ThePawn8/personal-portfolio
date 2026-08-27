import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import BaseButton from '@/components/base/BaseButton.vue'
import { router } from '@/router'

describe('BaseButton', () => {
  it('renders a button element by default', () => {
    const wrapper = mount(BaseButton, { slots: { default: 'Send' } })

    expect(wrapper.element.tagName).toBe('BUTTON')
    expect(wrapper.attributes('type')).toBe('button')
    expect(wrapper.text()).toBe('Send')
  })

  it('renders an anchor when given href, so navigation behaves like navigation', () => {
    const wrapper = mount(BaseButton, {
      props: { href: 'https://example.com' },
      slots: { default: 'Open' },
    })

    expect(wrapper.element.tagName).toBe('A')
    expect(wrapper.attributes('href')).toBe('https://example.com')
    // A `type` attribute on an anchor is meaningless and misleads assistive technology.
    expect(wrapper.attributes('type')).toBeUndefined()
  })

  it('renders a router link with a real href when given `to`', async () => {
    // Regression guard: binding an undefined `href` alongside `to` used to fall through
    // onto RouterLink's anchor and erase the href it had just computed, leaving an <a>
    // with no link role at all.
    const wrapper = mount(BaseButton, {
      props: { to: { name: 'home' } },
      slots: { default: 'Back to home' },
      global: { plugins: [router] },
    })
    await router.isReady()

    expect(wrapper.element.tagName).toBe('A')
    expect(wrapper.attributes('href')).toBe('/')
  })

  it('disables the button when disabled', () => {
    const wrapper = mount(BaseButton, { props: { disabled: true } })

    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('treats loading as disabled and announces the busy state', () => {
    const wrapper = mount(BaseButton, { props: { loading: true } })

    expect(wrapper.attributes('disabled')).toBeDefined()
    expect(wrapper.attributes('aria-busy')).toBe('true')
    expect(wrapper.find('svg[aria-hidden="true"]').exists()).toBe(true)
  })

  it('marks an inactive link with aria-disabled, since anchors ignore disabled', () => {
    const wrapper = mount(BaseButton, { props: { href: '/x', disabled: true } })

    expect(wrapper.attributes('disabled')).toBeUndefined()
    expect(wrapper.attributes('aria-disabled')).toBe('true')
  })

  it.each([
    ['primary', 'bg-accent'],
    ['secondary', 'border-line-strong'],
    ['ghost', 'hover:bg-surface-raised'],
  ] as const)('applies the %s variant', (variant, expectedClass) => {
    const wrapper = mount(BaseButton, { props: { variant } })

    expect(wrapper.classes().join(' ')).toContain(expectedClass)
  })

  it('applies size classes', () => {
    const small = mount(BaseButton, { props: { size: 'sm' } })
    const medium = mount(BaseButton, { props: { size: 'md' } })

    expect(small.classes()).toContain('h-9')
    expect(medium.classes()).toContain('h-11')
  })

  it('emits a click when active and not when disabled', async () => {
    const active = mount(BaseButton)
    await active.trigger('click')
    expect(active.emitted('click')).toHaveLength(1)

    const inactive = mount(BaseButton, { props: { disabled: true } })
    await inactive.trigger('click')
    expect(inactive.emitted('click')).toBeUndefined()
  })
})
