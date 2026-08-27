/**
 * The wire contract, mirrored in TypeScript.
 *
 * The API serialises in camelCase even though the documents are stored snake_case — the
 * persistence shape and the public shape are deliberately separate (ARCHITECTURE § 6.2), so
 * this is the mapping point rather than an accident. T-103 configures Pydantic accordingly,
 * and T-108 pins the whole contract with an OpenAPI snapshot test.
 */

export type ProjectKind = 'professional' | 'personal' | 'open-source' | 'freelance'

export interface ProjectPeriod {
  start: string
  /** `null` while ongoing. */
  end: string | null
}

export interface ProjectLinks {
  live?: string
  repo?: string
  caseStudy?: string
  video?: string
}

export interface Mockup {
  src: string
  alt: string
  caption?: string
  /** Intrinsic dimensions are required so the layout can reserve space and avoid shift. */
  width: number
  height: number
}

export interface Metric {
  label: string
  value: string
}

/** What the list endpoint returns: enough to render a card, without the case study body. */
export interface ProjectSummary {
  slug: string
  title: string
  summary: string
  kind: ProjectKind
  role: string
  organisation?: string
  period: ProjectPeriod
  stack: string[]
  tags: string[]
  featured: boolean
  order: number
  confidential: boolean
  links: ProjectLinks
  metrics: Metric[]
  mockups: Mockup[]
}

/** What the detail endpoint adds: the rendered, sanitised case study. */
export interface Project extends ProjectSummary {
  bodyHtml: string
}

export interface ExperienceEntry {
  company: string
  role: string
  start: string
  end: string | null
  summary: string
  highlights: string[]
}

export interface EducationEntry {
  institution: string
  degree: string
  start: string
  end: string
}

export interface SkillGroup {
  group: string
  items: string[]
}

export interface Language {
  name: string
  level: string
}

export interface Profile {
  name: string
  headline: string
  location: string
  bio: string
  /** Optional: the author may route all contact through the form instead. */
  email?: string
  links: { github: string; linkedin: string; cv?: string }
  languages: Language[]
  skills: SkillGroup[]
  experience: ExperienceEntry[]
  education: EducationEntry[]
  certifications: string[]
}

export interface ContactSubmission {
  name: string
  email: string
  message: string
  /** Honeypot. Real people leave it empty; bots fill every field they find. */
  website?: string
}

/** RFC 9457 problem details — the single error shape the API returns (ADR-0005). */
export interface Problem {
  type: string
  title: string
  status: number
  detail: string
  instance: string
  requestId: string
}
