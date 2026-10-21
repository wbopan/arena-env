1. Find the repo under `/home/travis/build/failed/`. Check `.travis.yml`, `pom.xml`, any log, and `java -version`.
2. Run `mvn -B -o test-compile 2>&1 | grep ERROR | head` and decide whether the first error is in code or in the POM (deps, versions, plugins, JDK).
3. Write the cause and plan to `/home/travis/build/failed/failed_reasons.txt`.
4. Make a minimal fix, save it with `git diff -- . ':!patch_*' > <repo>/<id>/patch_1.diff`, and make sure it is applied (`git stash; git apply patch_1.diff`).
5. Re-run `mvn -B clean test | tail` and confirm BUILD SUCCESS.
