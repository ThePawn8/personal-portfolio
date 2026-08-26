#!/usr/bin/env node
/**
 * First-run setup: creates .env from .env.example and generates the secrets that must
 * never be shared between machines.
 *
 * Idempotent — running it again reports what already exists and changes nothing.
 */
import { randomBytes } from 'node:crypto'
import { copyFileSync, existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import process from 'node:process'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const envPath = resolve(root, '.env')
const examplePath = resolve(root, '.env.example')

const green = (text) => `\x1b[32m${text}\x1b[0m`
const yellow = (text) => `\x1b[33m${text}\x1b[0m`
const dim = (text) => `\x1b[2m${text}\x1b[0m`

if (existsSync(envPath)) {
  console.log(`${yellow('kept')}    .env already exists — not touching it`)
} else {
  copyFileSync(examplePath, envPath)
  console.log(`${green('created')} .env from .env.example`)
}

// A predictable salt would make the hashed IPs in the rate limiter reversible by anyone
// who read this repository, which is the whole reason they are hashed.
const contents = readFileSync(envPath, 'utf8')
if (contents.includes('change-me-to-a-random-64-char-hex-string')) {
  const salt = randomBytes(32).toString('hex')
  writeFileSync(envPath, contents.replace('change-me-to-a-random-64-char-hex-string', salt))
  console.log(`${green('created')} IP_HASH_SALT (random, 64 hex characters)`)
} else {
  console.log(`${yellow('kept')}    IP_HASH_SALT already set`)
}

console.log(`
Next steps:
  ${dim('1.')} npm run install:all   ${dim('# web + api dependencies')}
  ${dim('2.')} npm run db:up         ${dim('# MongoDB in Docker')}
  ${dim('3.')} npm run dev           ${dim('# api :8000 + web :5173')}

Optional, only needed when the contact form is wired up (T-106):
  RESEND_API_KEY, CONTACT_TO_EMAIL, CONTACT_FROM_EMAIL in .env
`)
