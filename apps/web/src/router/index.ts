import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import HomeView from '@/views/HomeView.vue'

declare module 'vue-router' {
  interface RouteMeta {
    /** Page title, composed with the site name in the afterEach hook below. */
    title: string
  }
}

/**
 * Home is imported eagerly — it is the entry point for most visits, and a round trip for
 * its chunk would delay the largest paint. Every other route is split out.
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { title: 'Software Developer' },
  },
  {
    path: '/projects',
    name: 'projects',
    component: () => import('@/views/ProjectsView.vue'),
    meta: { title: 'Work' },
  },
  {
    path: '/projects/:slug',
    name: 'project',
    component: () => import('@/views/ProjectDetailView.vue'),
    props: true,
    meta: { title: 'Project' },
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/AboutView.vue'),
    meta: { title: 'About' },
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('@/views/ContactView.vue'),
    meta: { title: 'Contact' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: 'Page not found' },
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,

  scrollBehavior(to, _from, savedPosition) {
    // Back and forward must restore where the reader was, or long pages become unusable.
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

export const RELOAD_FLAG = 'portfolio-chunk-reload'

/**
 * A deploy replaces the hashed chunks, so a tab left open overnight asks for files that no
 * longer exist. Reloading recovers; a `sessionStorage` flag stops that from becoming a
 * reload loop when the failure is something else entirely.
 *
 * Exported so the recovery path can be tested directly — it only ever runs after a real
 * deploy, which is the worst possible time to discover it is wrong.
 */
export function handleNavigationError(error: Error, fullPath: string): boolean {
  const isStaleChunk = /dynamically imported module|Importing a module script failed/i.test(
    error.message,
  )
  if (!isStaleChunk) return false

  try {
    if (sessionStorage.getItem(RELOAD_FLAG)) return false
    sessionStorage.setItem(RELOAD_FLAG, '1')
  } catch {
    return false
  }

  window.location.assign(fullPath)
  return true
}

router.onError((error, to) => {
  handleNavigationError(error, to.fullPath)
})

router.afterEach((to) => {
  try {
    sessionStorage.removeItem(RELOAD_FLAG)
  } catch {
    // Nothing to clean up when storage is unavailable.
  }

  // Full per-route metadata (description, canonical, Open Graph) arrives in T-209; the
  // title is set here because a wrong browser-tab title is a shell bug, not an SEO one.
  document.title = `${to.meta.title} · Andrés M`
})
