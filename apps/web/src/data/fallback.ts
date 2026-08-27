import snapshot from '@/assets/projects.fallback.json'
import type { ProjectSummary } from '@/types/api'

/**
 * Build-time content snapshot (ARCHITECTURE § 6.4).
 *
 * CI calls `GET /api/v1/projects` during the web build and writes the result here, so an
 * API outage degrades the site to *slightly stale content* instead of an empty page in
 * front of a recruiter. The cost is honest and small: the snapshot is as old as the last
 * deploy, and it adds a few kB to the bundle.
 *
 * Until the deployment workflow exists (T-404) the file ships empty, and an empty snapshot
 * is treated as "no fallback available" rather than "no projects" — showing an error is
 * better than claiming the portfolio has nothing in it.
 */
interface Snapshot {
  generatedAt: string | null
  projects: ProjectSummary[]
}

const typedSnapshot = snapshot as Snapshot

export interface FallbackContent {
  projects: ProjectSummary[]
  generatedAt: string | null
}

export function getFallbackProjects(): FallbackContent | null {
  if (typedSnapshot.projects.length === 0) return null

  return { projects: typedSnapshot.projects, generatedAt: typedSnapshot.generatedAt }
}
