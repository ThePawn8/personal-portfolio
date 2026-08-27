import { expect, test } from '@playwright/test'

test.describe('shell', () => {
  test('serves the application and renders the home view', async ({ page }) => {
    const response = await page.goto('/')

    expect(response?.status()).toBe(200)
    await expect(page).toHaveTitle(/Andrés M/)
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Andrés M')
  })

  test('loads without console errors', async ({ page }) => {
    const errors: string[] = []
    page.on('console', (message) => {
      if (message.type() === 'error') errors.push(message.text())
    })
    page.on('pageerror', (error) => errors.push(error.message))

    await page.goto('/')
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()

    expect(errors).toEqual([])
  })

  test('navigates between routes without a full reload', async ({ page, isMobile }) => {
    test.skip(isMobile === true, 'the desktop navigation is hidden at this width')
    await page.goto('/')

    // A marker on the window object survives client-side routing but not a page load,
    // which is what distinguishes SPA navigation from a link that reloads the document.
    await page.evaluate(() => {
      ;(window as unknown as { __spa: boolean }).__spa = true
    })

    await page
      .getByRole('navigation', { name: 'Main' })
      .first()
      .getByRole('link', { name: 'Work' })
      .click()

    await expect(page).toHaveURL(/\/projects$/)
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Work')
    expect(await page.evaluate(() => (window as unknown as { __spa?: boolean }).__spa)).toBe(true)
  })

  test('resolves a deep link on a cold load', async ({ page }) => {
    // The SPA rewrite has to send unknown paths to index.html (T-403); without it this is
    // a 404 from the static host.
    const response = await page.goto('/about')

    expect(response?.status()).toBe(200)
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('About')
  })

  test('shows the 404 view for an unknown path', async ({ page }) => {
    await page.goto('/this/does/not/exist')

    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Page not found')
    await expect(page.getByRole('link', { name: 'Back to home' })).toBeVisible()
  })

  test('skip link is the first thing a keyboard reaches', async ({ page }) => {
    await page.goto('/')
    await page.keyboard.press('Tab')

    const focused = page.locator(':focus')
    await expect(focused).toHaveText('Skip to content')
    await expect(focused).toBeVisible()
  })
})

test.describe('theme', () => {
  test('follows the operating system by default', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'dark' })
    await page.goto('/')

    await expect(page.locator('html')).not.toHaveAttribute('data-theme')

    // Assert the resolved lightness rather than an exact colour string: the browser is
    // free to serialise oklch differently, but "dark" is not a matter of formatting.
    const background = await page.evaluate(() => getComputedStyle(document.body).backgroundColor)
    const lightness = Number(/^lab\(([\d.]+)/.exec(background)?.[1] ?? '100')
    expect(lightness).toBeLessThan(20)
  })

  test('an explicit choice overrides the system and survives a reload', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'dark' })
    await page.goto('/')

    await page.getByTitle('Light').click()
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')

    await page.reload()

    // The inline bootstrap script must apply this before the first paint, so the attribute
    // is present immediately rather than after the bundle hydrates.
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')
    await expect(page.getByRole('radio', { name: 'Light' })).toBeChecked()
  })

  test('returning to system removes the override', async ({ page }) => {
    await page.goto('/')

    await page.getByTitle('Dark').click()
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')

    await page.getByTitle('System').click()
    await expect(page.locator('html')).not.toHaveAttribute('data-theme')
  })
})

test.describe('mobile navigation', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('opens, navigates and closes', async ({ page }) => {
    await page.goto('/')

    const toggle = page.getByRole('button', { name: 'Open menu' })
    await expect(toggle).toHaveAttribute('aria-expanded', 'false')

    await toggle.click()
    const menu = page.locator('#mobile-navigation')
    await expect(menu).toBeVisible()

    await menu.getByRole('link', { name: 'Contact' }).click()

    await expect(page).toHaveURL(/\/contact$/)
    await expect(menu).toBeHidden()
  })

  test('closes on Escape', async ({ page }) => {
    await page.goto('/')

    await page.getByRole('button', { name: 'Open menu' }).click()
    await expect(page.locator('#mobile-navigation')).toBeVisible()

    await page.keyboard.press('Escape')

    await expect(page.locator('#mobile-navigation')).toBeHidden()
  })
})
