import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import App from '@/App.vue'

describe('App', () => {
  it('renders a single top-level landmark', () => {
    const wrapper = mount(App)

    expect(wrapper.find('main').exists()).toBe(true)
  })

  it('renders exactly one level-1 heading', () => {
    const wrapper = mount(App)

    const headings = wrapper.findAll('h1')

    expect(headings).toHaveLength(1)
    expect(headings[0]?.text()).toBe('Portfolio')
  })
})
