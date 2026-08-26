#!/usr/bin/env node
/**
 * Runs the API and the web app side by side with prefixed, colourised output.
 *
 * Exists because `make` is not available on Windows, where this project is developed.
 * The Makefile stays the canonical entry point for CI and for Unix contributors; this
 * script is the cross-platform equivalent of `make dev`.
 */
import { spawn } from 'node:child_process'
import process from 'node:process'

const COLORS = { api: '\x1b[36m', web: '\x1b[35m', reset: '\x1b[0m', dim: '\x1b[2m' }

const services = [
  { name: 'api', command: 'npm', args: ['run', 'dev:api'] },
  { name: 'web', command: 'npm', args: ['run', 'dev:web'] },
]

const children = []
let shuttingDown = false

function prefix(name, chunk) {
  const tag = `${COLORS[name]}[${name}]${COLORS.reset} `
  return chunk
    .toString()
    .split('\n')
    .filter((line) => line.trim().length > 0)
    .map((line) => tag + line)
    .join('\n')
}

function shutdown(code) {
  if (shuttingDown) return
  shuttingDown = true
  for (const child of children) {
    if (child.exitCode === null) child.kill('SIGTERM')
  }
  process.exit(code)
}

for (const service of services) {
  // shell:true so npm resolves through npm.cmd on Windows
  const child = spawn(service.command, service.args, { shell: true, stdio: ['ignore', 'pipe', 'pipe'] })
  child.stdout.on('data', (chunk) => console.log(prefix(service.name, chunk)))
  child.stderr.on('data', (chunk) => console.error(prefix(service.name, chunk)))
  child.on('exit', (code) => {
    console.log(`${COLORS.dim}[${service.name}] exited with code ${code}${COLORS.reset}`)
    shutdown(code ?? 0)
  })
  children.push(child)
}

process.on('SIGINT', () => shutdown(0))
process.on('SIGTERM', () => shutdown(0))

console.log(`${COLORS.api}[api]${COLORS.reset} http://localhost:8000/docs`)
console.log(`${COLORS.web}[web]${COLORS.reset} http://localhost:5173`)
