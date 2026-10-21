# Match an npm lockfile against an offline advisory database

You are auditing an npm project offline. You have two inputs:

- `/root/work/package-lock.json`: a lockfile in v3 format. Installed packages are the entries of the `packages` object.
  - Skip the root entry, whose key is `""`.
  - The package name is the part of the key after the last `node_modules/`. For example, `node_modules/a/node_modules/@x/y` is package `@x/y`.
  - The version is the entry's `version` field.
  - The same name and version may appear at several paths. Count each name/version pair only once.
- `/root/work/advisories.json`: an object with an `advisories` list. Each advisory has `id`, `package`, `ranges`, `cvss_v3` and `cvss_v2`. The scores may be null.

An installed name/version pair is affected by an advisory when the package names match and the version falls in at least one range. A range covers versions where `introduced <= version < fixed`. If `fixed` is null, the range has no upper bound. Compare versions numerically as major.minor.patch.

The score of an advisory is `cvss_v3` if it is not null, otherwise `cvss_v2`, otherwise null. Map scores to severity with the CVSS v3 bands:

| Score | Severity |
|---|---|
| 0.1-3.9 | LOW |
| 4.0-6.9 | MEDIUM |
| 7.0-8.9 | HIGH |
| 9.0-10.0 | CRITICAL |
| null | UNKNOWN |

Write `/root/work/audit.json` with these keys:

- `findings`: a list of `{"package", "version", "advisory", "score", "severity"}`, one per affected pair and advisory. Sort by package (plain string order), then version (numeric), then advisory id.
- `summary`: an object counting findings under the keys `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` and `UNKNOWN`. Include every key, even when its count is 0.
- `affected_packages`: the number of distinct package names in `findings`.
