import { expect, test } from '@playwright/test'

test.describe('smoke', () => {
  test('serves the application shell', async ({ page }) => {
    const response = await page.goto('/')

    expect(response?.status()).toBe(200)
    await expect(page).toHaveTitle(/portfolio/i)
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Portfolio')
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
})
