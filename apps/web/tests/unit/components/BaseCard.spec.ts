import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import BaseBadge from '@/components/base/BaseBadge.vue'
import BaseCard from '@/components/base/BaseCard.vue'
import AppContainer from '@/components/base/AppContainer.vue'

describe('BaseCard', () => {
  it('renders a div with default padding', () => {
    const wrapper = mount(BaseCard, { slots: { default: 'Body' } })

    expect(wrapper.element.tagName).toBe('DIV')
    expect(wrapper.classes()).toContain('p-6')
    expect(wrapper.text()).toBe('Body')
  })

  it('renders the requested element, so cards can be semantic', () => {
    const wrapper = mount(BaseCard, { props: { as: 'article' } })

    expect(wrapper.element.tagName).toBe('ARTICLE')
  })

  it('adds hover and focus-within styling only when interactive', () => {
    const plain = mount(BaseCard)
    const interactive = mount(BaseCard, { props: { interactive: true } })

    expect(plain.classes().join(' ')).not.toContain('hover:border-line-strong')
    expect(interactive.classes().join(' ')).toContain('hover:border-line-strong')
  })

  it('never becomes focusable itself', () => {
    // The link inside the card owns focus; a focusable card would duplicate every card
    // in the tab order.
    const wrapper = mount(BaseCard, { props: { interactive: true } })

    expect(wrapper.attributes('tabindex')).toBeUndefined()
    expect(wrapper.attributes('role')).toBeUndefined()
  })
})

describe('BaseBadge', () => {
  it('renders its content in a non-interactive element', () => {
    const wrapper = mount(BaseBadge, { slots: { default: 'vue' } })

    expect(wrapper.element.tagName).toBe('SPAN')
    expect(wrapper.text()).toBe('vue')
    expect(wrapper.attributes('tabindex')).toBeUndefined()
  })

  it.each([
    ['neutral', 'bg-surface-raised'],
    ['accent', 'text-accent'],
    ['outline', 'border-line'],
  ] as const)('applies the %s tone', (tone, expectedClass) => {
    const wrapper = mount(BaseBadge, { props: { tone } })

    expect(wrapper.classes().join(' ')).toContain(expectedClass)
  })
})

describe('AppContainer', () => {
  it('applies one shared gutter and max width', () => {
    const wrapper = mount(AppContainer)

    expect(wrapper.classes()).toContain('mx-auto')
    expect(wrapper.classes()).toContain('max-w-5xl')
  })

  it.each([
    ['prose', 'max-w-2xl'],
    ['wide', 'max-w-7xl'],
  ] as const)('supports the %s width', (width, expectedClass) => {
    const wrapper = mount(AppContainer, { props: { width } })

    expect(wrapper.classes()).toContain(expectedClass)
  })

  it('renders the requested element', () => {
    const wrapper = mount(AppContainer, { props: { as: 'section' } })

    expect(wrapper.element.tagName).toBe('SECTION')
  })
})
