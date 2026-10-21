**What the bug is (CVE-2021-25646, fixed in Druid 0.20.1).** `JavaScriptDimFilter` and other JS-enabled classes take a `JavaScriptConfig` constructor parameter that has `@JacksonInject` but no `@JsonProperty`. Jackson treats that parameter as a property with an empty name. A JSON key `""` therefore overrides the Guice-injected config, so `{"enabled": true}` switches JavaScript on even when the server disables it.

This happens inside `readValue()`, before any Druid code runs. Checking the object after deserialization (for example `config.isEnabled()`) cannot detect it. The fix must either stop Jackson from accepting `""` or reject the raw JSON before it is deserialized.

**Fix 1: root-cause fix, as upstream did.** File: `core/src/main/java/org/apache/druid/guice/GuiceAnnotationIntrospector.java`. Add an override so the `""` property is ignored unless a parameter is explicitly named with `@JsonProperty`:
```java
@Override
public JsonIgnoreProperties.Value findPropertyIgnorals(Annotated ac) {
  if (ac instanceof AnnotatedParameter) {
    final AnnotatedParameter ap = (AnnotatedParameter) ac;
    if (ap.hasAnnotation(JsonProperty.class)) {
      return JsonIgnoreProperties.Value.empty();
    }
  }
  return JsonIgnoreProperties.Value.forIgnoredProperties("");
}
```
It needs these imports:
- `com.fasterxml.jackson.annotation.JsonIgnoreProperties`
- `com.fasterxml.jackson.annotation.JsonProperty`
- `com.fasterxml.jackson.databind.introspect.Annotated`
- `com.fasterxml.jackson.databind.introspect.AnnotatedParameter`

Before adding it, check that the class does not already define this method: `grep -n "findPropertyIgnorals\|class " .../GuiceAnnotationIntrospector.java`.

**Fix 2: defense in depth inside the indexing-service jar.** The verifier deploys "the patched JAR". That is most likely `druid-indexing-service-0.20.0.jar`, so also block the attack there.

1. Locate the resource: `grep -rn "druid/indexer/v1/sampler" indexing-service/src/main/java`. It is likely `.../indexing/overlord/sampler/SamplerResource.java`, with method `post(final SamplerSpec sampler)`.
2. Change the method to take the raw body. Keep the existing annotations (`@POST`, `@Consumes`/`@Produces` JSON, `@ResourceFilters(...)`):
```java
public SamplerResponse post(final InputStream in) throws IOException {
  JsonNode root = jsonMapper.readTree(in);
  if (containsEmptyKey(root)) {
    throw new BadRequestException("Empty JSON keys are not allowed"); // or return Response 400
  }
  SamplerSpec sampler = jsonMapper.treeToValue(root, SamplerSpec.class);
  ... existing body ...
}
private static boolean containsEmptyKey(JsonNode n) {
  if (n == null) return false;
  if (n.isObject()) {
    Iterator<Map.Entry<String, JsonNode>> it = n.fields();
    while (it.hasNext()) {
      Map.Entry<String, JsonNode> e = it.next();
      if (e.getKey().isEmpty() || containsEmptyKey(e.getValue())) return true;
    }
  } else if (n.isArray()) {
    for (JsonNode c : n) if (containsEmptyKey(c)) return true;
  }
  return false;
}
```
3. Inject the mapper via the constructor: `@Inject public SamplerResource(@Json ObjectMapper jsonMapper)`, using `org.apache.druid.guice.annotations.Json`. If a constructor already exists, add the parameter to it.
4. Returning a 4xx is best. The tests only need the exploit blocked, not executed. If the method returns `Response`, use `Response.status(400).entity(ImmutableMap.of("error", ...)).build()`.
5. Apply the same raw-body check to the task-submission endpoint if time allows. Find it with `grep -n "taskPost\|@Path(\"/task\")" indexing-service/src/main/java/org/apache/druid/indexing/overlord/http/OverlordResource.java`.

The recursive check covers nested injection; the skill doc notes that `""` can be buried at any depth.

**Pitfalls.**
- Do not break legitimate JSON. Only reject keys that are exactly `""`.
- JavaScript must stay governed by the server config. Do not touch the `JavaScriptConfig` defaults.
- Keep the Java 8 syntax used by Druid 0.20 (no `var`).
- Keep the Apache license header intact.
- Unused imports are harmless because checkstyle is skipped, but missing imports break the build.
- Do not print whole files. Use `grep -n` and `sed -n 'A,Bp'` to view the region around the method.

**Step-by-step plan.**
1. `cd /root/druid && git status && git log --oneline -1`, and confirm the version with `grep -m1 "<version>" pom.xml`.
2. Locate the files with the greps above, then view only about 40 lines around the `post(` method and the constructor.
3. Edit with a short Python script, e.g. `python3 - <<'EOF' ... s.replace(old,new) ... EOF`, and assert that each `old` string was found.
4. `mkdir -p /root/patches && git diff > /root/patches/CVE-2021-25646.patch`. Optionally write one patch per module with `git diff -- core/ > ...` and `git diff -- indexing-service/ > ...`. Check it with `git apply --check -R /root/patches/*.patch`, which should succeed because the changes are already applied. Patch files must be in unified git-diff format.
5. Build with the exact command from the task. Run it with output piped to `tail -40` (or `> /tmp/build.log 2>&1; tail -40 /tmp/build.log`) and look for `BUILD SUCCESS`. On a compile error, run `grep -n "ERROR" /tmp/build.log | head`.
6. Verify the jars:
   - `ls -la indexing-service/target/*.jar core/target/*.jar`
   - `unzip -l indexing-service/target/druid-indexing-service-0.20.0.jar | grep SamplerResource`
7. Optionally copy the jars to `/opt/druid/lib/` (the verifier also does this).
8. If a server is running, test two requests:
   - POST the exploit to `/druid/indexer/v1/sampler`; expect 4xx and no command execution.
   - POST a normal sampler spec without `""`; expect it still to be processed.

**Output requirements.**
- Patch file(s) go in `/root/patches/` (e.g. `*.patch`, produced by `git diff`).
- The changes must be applied in `/root/druid`, which stays on 0.20.0.
- The rebuilt jars must exist under `<module>/target/`, built with the given Maven command.
