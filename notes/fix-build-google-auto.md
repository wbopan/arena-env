**Goal and outputs**
- Analysis goes in `/home/travis/build/failed/failed_reasons.txt` as plain text. State whether each error is in code or in build configuration, which file and line, the cause, and the planned fix.
- Diffs go in `/home/travis/build/failed/<repo>/<id>/patch_1.diff`, `patch_2.diff`, … Use standard unified git format with `--- a/path` and `+++ b/path` headers and paths relative to the repo root.
- The diffs must then actually be applied to the working tree. The grader likely rebuilds the repo, so the final tree must compile and pass tests.
- Do not change files beyond what is needed. Never delete tests or skip them to "fix" a build.

**Step-by-step plan (cheap inspection)**
1. Locate the repo:
   `ls /home/travis/build/failed/; ls /home/travis/build/failed/*/`
   Then `cd` into `<repo>/<id>` and run `git status | head; git log --oneline -3`.
2. Identify the build system and the CI command:
   `ls; cat .travis.yml 2>/dev/null | head -40`
   - Look for `pom.xml` (Maven) or `build.gradle` (Gradle).
   - Note the JDK the CI asks for (`jdk:` key) versus the local one: `java -version 2>&1; mvn -v 2>&1 | head -3`.
3. Look for an existing failure log first, e.g. `ls /home/travis/build/failed/<repo>/<id>/*.log` or the parent dir. If one exists, grep it: `grep -nE "ERROR|BUILD FAILURE|cannot find symbol|does not exist" log | head -40`.
4. If there is no log, reproduce offline-friendly and keep the output short:
   `mvn -B -q -o compile 2>&1 | grep -E "ERROR|WARN.*deprecat" | head -40`
   - Drop `-o` if offline resolution fails and network exists.
   - Then run `mvn -B -o test-compile` and `mvn -B -o test 2>&1 | tail -60` to reach test-phase failures.
   - Use `-e` for stack traces only if needed. Multi-module builds: `-pl module -am` limits scope; `-rf :module` resumes.
5. Classify the error.

**Code errors** (`[ERROR] /path/File.java:[line,col] ...`):
- **"cannot find symbol" / "package X does not exist"**: a missing import, a renamed API, or a missing dependency.
  - Check whether the symbol exists in the repo: `grep -rn "class Foo\|Foo(" src | head`.
  - If it is from a library, check the version actually resolved: `mvn dependency:tree -Dincludes=group`.
- **"incompatible types" or "method does not override"**: a signature mismatch after an API change. Read only the relevant lines with `sed -n 'L-10,L+10p' File.java`.
- **Test failures**: read `target/surefire-reports/*.txt` with `head -30`.

**Build-configuration errors:**
- **Unresolvable dependency or plugin** (`Could not resolve`, `Non-resolvable parent POM`):
  - Fix the version or groupId, add a `<version>`, or add a repository.
  - SNAPSHOT versions or unavailable repos are common causes.
- **Missing dependency**: add it with the correct scope (compile, provided, runtime, test). Tests need e.g. junit or mockito with `<scope>test</scope>`.
- **Version conflicts**: Maven's "nearest definition wins" rule applies. Pin the version in `<dependencyManagement>` or add `<exclusions>`.
- **JDK mismatch**: `maven.compiler.source/target/release` versus the installed JDK. "invalid target release", or javadoc/doclint failures on newer JDKs, can be fixed with `<doclint>none</doclint>`. Removed JDK modules such as javax.xml.bind on JDK 11+ need an explicit dependency.
- **Plugin without a version**, or one too old for the JDK: pin it, e.g. maven-compiler-plugin 3.x or surefire 2.22+/3.x.
- **Enforcer, checkstyle, PMD, or license plugin failures**: fix the violating code or config. Prefer fixing the code over disabling the plugin.
- **Multi-module builds**: check the module order in `<modules>`, the parent `<version>` matching, and `<dependencyManagement>` in the parent.

6. Write `failed_reasons.txt` with `cat > ... <<'EOF'`.
7. Create the patch:
   - Edit a copy, or edit in place and let git produce the diff: `git diff > patch_1.diff`.
   - Or use `diff -u a/file b/file`, but `git diff` is safer.
   - If you edit first and capture with `git diff`, the change is already "applied". To be clean, run `git stash`, then `git apply --check patch_1.diff && git apply patch_1.diff`.
   - Make sure the patch files themselves are not included in the diff: `git diff -- . ':!patch_*.diff'`.
8. Verify:
   - `git apply --check` fails on an already-applied patch, which is expected after applying.
   - Confirm application with `git diff --stat`.
   - Rebuild with `mvn -B -o clean test 2>&1 | tail -30` (or the `.travis.yml` script command) and expect `BUILD SUCCESS`.
   - If tests take too long, run `mvn -B -o clean test-compile` first.

**Pitfalls**
- Do not print full logs or POMs. Use `grep -n`, `head`, `sed -n` ranges, and `mvn help:effective-pom | grep -A3 artifactId-of-interest`.
- Fix the root cause: the first `[ERROR]` usually causes the rest.
- Keep the patch minimal and in valid unified format. Hunk headers must be correct, which is why you should generate them with git rather than writing them by hand.
- Don't commit. Leave the changes applied in the working tree.
