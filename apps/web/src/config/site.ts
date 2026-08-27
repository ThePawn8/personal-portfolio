/**
 * Site-level constants that are not content.
 *
 * Anything that belongs to the person rather than the site — bio, experience, links,
 * skills — lives in `content/profile.yml` and arrives through the API (T-104/T-302). This
 * file holds only what the shell itself needs before any data has loaded.
 */
export const site = {
  /** Displayed in the header and footer until the profile API is wired up (T-203). */
  name: 'Andrés M',
  role: 'Software Developer',
  repositoryUrl: 'https://github.com/ThePawn8/personal-portfolio',
  githubUrl: 'https://github.com/ThePawn8',
} as const

export const navigation = [
  { label: 'Work', routeName: 'projects' },
  { label: 'About', routeName: 'about' },
  { label: 'Contact', routeName: 'contact' },
] as const
