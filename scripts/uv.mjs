#!/usr/bin/env node
/**
 * Thin wrapper that runs `uv` inside apps/api from anywhere, so the root npm scripts
 * work identically on Windows, macOS and Linux.
 *
 *   npm run api -- run pytest      ->  uv run pytest        (cwd: apps/api)
 *   npm run api -- sync            ->  uv sync              (cwd: apps/api)
 */
import { spawn } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
import process from 'node:process'

const apiDir = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'apps', 'api')
const args = process.argv.slice(2)

if (args.length === 0) {
  console.error('usage: npm run api -- <uv args>   e.g. npm run api -- run pytest')
  process.exit(2)
}

const child = spawn('uv', args, { cwd: apiDir, shell: true, stdio: 'inherit' })

child.on('error', (error) => {
  if (error.code === 'ENOENT') {
    console.error('uv is not installed. Install it with:  pip install uv')
    process.exit(127)
  }
  throw error
})

child.on('exit', (code) => process.exit(code ?? 0))
