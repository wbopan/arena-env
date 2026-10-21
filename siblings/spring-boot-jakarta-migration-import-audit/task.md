# Jakarta namespace import audit

A legacy Spring Boot 2 codebase lives under `/root/work/src/`. It contains Java sources in nested main and test directories. Before migrating to Spring Boot 3, audit which `import` declarations must move from `javax.*` to `jakarta.*`.

Rules:
- Scan every file ending in `.java` anywhere under `/root/work/src/`, recursively. Ignore all other files.
- An import declaration is a line whose text, after stripping surrounding whitespace, starts with `import `. This includes `import static`. Commented-out lines are not imports.
- The imported name is the text after `import ` (and after `static `, if present), up to the `;`.
- A name migrates if it starts with one of these prefixes: `javax.persistence.`, `javax.validation.`, `javax.servlet.`, `javax.transaction.`, `javax.ws.rs.`, `javax.mail.`, `javax.jms.`, `javax.xml.bind.`.
- Exception: names starting with `javax.transaction.xa.` belong to the JDK and do not migrate.
- These four exact names also migrate: `javax.annotation.PostConstruct`, `javax.annotation.PreDestroy`, `javax.annotation.Resource`, `javax.annotation.Priority`.
- Every other `javax.*` name stays (e.g. `javax.sql`, `javax.crypto`, `javax.annotation.processing`).

Write `/root/work/migration_report.json`, a JSON object with these keys:
- `files_scanned`: number of `.java` files
- `files_changed`: number of `.java` files with at least one migrating import
- `total_migrated_imports`: integer
- `by_package`: maps each target package to its count, omitting zero counts. The target package is the matched prefix without its trailing dot and with `javax` replaced by `jakarta`, e.g. `jakarta.xml.bind`; the four annotation names map to `jakarta.annotation`.
- `per_file`: maps each changed file's path, relative to `/root/work/src` with forward slashes, to its migrated-import count
- `retained_javax`: sorted list of the distinct imported names that start with `javax.` and do not migrate
