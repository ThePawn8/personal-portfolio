import { computed, toValue, watch, type MaybeRefOrGetter } from 'vue'

import { getFallbackProjects } from '@/data/fallback'
import { api } from '@/lib/api'
import type { Profile, Project, ProjectSummary } from '@/types/api'

import { useAsyncResource } from './useAsyncResource'

/**
 * The project list, with the build-time snapshot as its safety net.
 *
 * This is the one resource where staleness beats emptiness: a recruiter who opens the site
 * during an API outage should see the work, with a quiet note that it may be out of date.
 */
export function useProjects() {
  const resource = useAsyncResource<ProjectSummary[]>((signal) => api.getProjects({ signal }), {
    fallback: () => getFallbackProjects()?.projects ?? null,
  })

  const projects = computed<ProjectSummary[]>(() => resource.data.value ?? [])
  const featured = computed(() => projects.value.filter((project) => project.featured))

  const allTags = computed(() => {
    const tags = new Set<string>()
    for (const project of projects.value) {
      for (const tag of project.tags) tags.add(tag)
    }
    return [...tags].sort()
  })

  return { ...resource, projects, featured, allTags }
}

/**
 * A single project.
 *
 * No fallback: showing a stale case study under a URL that may no longer exist is worse
 * than saying so. `notFound` is a first-class outcome rather than an error, because an
 * unpublished or mistyped slug is an ordinary thing for a visitor to hit.
 */
export function useProject(slug: MaybeRefOrGetter<string>) {
  const resource = useAsyncResource<Project>((signal) => api.getProject(toValue(slug), { signal }))

  watch(
    () => toValue(slug),
    () => {
      void resource.reload()
    },
  )

  return resource
}

export function useProfile() {
  return useAsyncResource<Profile>((signal) => api.getProfile({ signal }))
}
