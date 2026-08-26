import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import SectionHeading from '@/components/base/SectionHeading.vue'

describe('SectionHeading', () => {
  it('renders an h2 by default', () => {
    const wrapper = mount(SectionHeading, { props: { title: 'Selected work' } })

    expect(wrapper.find('h2').text()).toBe('Selected work')
  })

  it.each([1, 2, 3] as const)('renders the requested heading level %i', (level) => {
    const wrapper = mount(SectionHeading, { props: { title: 'Title', level } })

    expect(wrapper.find(`h${level}`).exists()).toBe(true)
  })

  it('omits the eyebrow and description when not provided', () => {
    const wrapper = mount(SectionHeading, { props: { title: 'Title' } })

    expect(wrapper.findAll('p')).toHaveLength(0)
  })

  it('renders the eyebrow and description when provided', () => {
    const wrapper = mount(SectionHeading, {
      props: { title: 'Title', eyebrow: 'Case study', description: 'What I built and why.' },
    })

    const paragraphs = wrapper.findAll('p')
    expect(paragraphs).toHaveLength(2)
    expect(paragraphs[0]?.text()).toBe('Case study')
    expect(paragraphs[1]?.text()).toBe('What I built and why.')
  })

  it('separates heading level from visual size', () => {
    // An h3 that looks like a title keeps the document outline correct while the design
    // stays free — the whole reason level and size are independent props.
    const wrapper = mount(SectionHeading, {
      props: { title: 'Title', level: 3, size: 'display' },
    })

    expect(wrapper.find('h3').classes()).toContain('text-display')
  })
})
