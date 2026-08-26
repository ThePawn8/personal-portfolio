/*
 * Creates the least-privilege application user, mirroring production (T-402).
 *
 * The API never connects as root: if the service is compromised, the blast radius should
 * be read/write on one database, not administrative access to the server. Developing
 * against the same permission set is how permission bugs get caught locally instead of
 * on the first deploy.
 *
 * Runs once, against an empty data volume. To re-run it:
 *   npm run db:down && docker volume rm portfolio-mongo-data && npm run db:up
 */

db.createUser({
  user: 'portfolio',
  pwd: 'local-dev-only',
  roles: [{ role: 'readWrite', db: 'portfolio' }],
})

print('created application user: portfolio (readWrite on portfolio)')
