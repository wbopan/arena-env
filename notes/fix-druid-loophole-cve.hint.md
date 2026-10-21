1. `grep -rn "druid/indexer/v1/sampler"` in `indexing-service/src/main/java` and view the `SamplerResource` `post`/constructor region; also open `core/.../guice/GuiceAnnotationIntrospector.java`.
2. In `GuiceAnnotationIntrospector`, override `findPropertyIgnorals` to ignore `""` unless the parameter has `@JsonProperty`. In `SamplerResource` (and `OverlordResource` `taskPost` if feasible), read the raw body with `jsonMapper.readTree`, reject any empty key recursively with a 400, then `treeToValue`.
3. `git diff > /root/patches/CVE-2021-25646.patch`.
4. Run the given mvn command (`tail` the log for `BUILD SUCCESS`) and confirm `indexing-service/target/*.jar` exists.
5. If possible, POST the exploit (expect 4xx) and a clean sampler spec (expect success).
