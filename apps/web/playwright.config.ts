import process from 'node:process'

import { defineConfig, devices } from '@playwright/test'

const PORT = 4173
const baseURL = `http://localhost:${PORT}`
const isCI = Boolean(process.env.CI)

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  // A committed `test.only` is a mistake, not a workflow — never let it pass CI.
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  workers: isCI ? 1 : undefined,
  reporter: isCI ? [['github'], ['html', { open: 'never' }]] : [['list']],
  timeout: 30_000,
  expect: { timeout: 5_000 },

  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],

  // Tests run against the production build, not the dev server: dev-only behaviour
  // (unminified errors, HMR, different asset handling) hides real deployment bugs.
  webServer: {
    command: 'npm run build && npm run preview -- --port ' + PORT,
    url: baseURL,
    reuseExistingServer: !isCI,
    timeout: 120_000,
  },
})
