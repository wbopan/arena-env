**Goal.** Migrate the Maven project in `/workspace/` (find it with `find /workspace -name pom.xml -maxdepth 3`) in place. It must end on Java 21 and Spring Boot 3.2.x, with jakarta namespaces, Hibernate 6, Spring Security 6, and RestClient instead of RestTemplate. Success means two things:

- `mvn clean compile` produces no errors.
- `mvn test` passes all tests.

Hidden checks will probably grep for the following, so make sure each condition holds:
- parent version `3.2.x` and `<java.version>21</java.version>`
- no `javax.persistence|validation|servlet` imports, and `jakarta.persistence` imports present in the entities
- no `jaxb-api`, no `javax.xml.bind`, no `jjwt` 0.9.1 in pom.xml
- no `WebSecurityConfigurerAdapter`, `@EnableGlobalMethodSecurity`, `.antMatchers(` or `.authorizeRequests(`
- `@EnableMethodSecurity`, `SecurityFilterChain` and `.requestMatchers(` present
- `RestClient` used in place of `RestTemplate`

**1. Inspect cheaply first**
- Run `java -version; mvn -v | head -3` to confirm JDK 21.
- Run `ls ~/.m2/repository 2>/dev/null | head` to see the cache. If the network may be off, try `mvn -o` later.
- List the sources with `find . -name "*.java" | head -50`. Check `wc -l` on pom.xml and `application.properties` (or `.yml`).
- Grep the hot spots, never cat whole files:
  ```
  grep -rn "import javax\.\|RestTemplate\|WebSecurityConfigurerAdapter\|EnableGlobalMethodSecurity\|antMatchers\|authorizeRequests\|Jwts\.\|@Type\|update from\|createCriteria" --include=*.java src
  grep -n "<version>\|artifactId\|java.version\|source>\|target>" pom.xml
  ```
- Look at the tests (`src/test`). See what they mock (RestTemplate? RestClient? JwtTokenProvider methods?) so your public method signatures stay compatible.

**2. pom.xml**
- Set the parent `spring-boot-starter-parent` to `3.2.0` (any 3.2.x works).
- Set `<java.version>21</java.version>`. Fix any explicit maven-compiler-plugin `<source>`/`<target>` of 1.8 to 21, or delete them.
- Delete these dependencies: `javax.xml.bind:jaxb-api`, `com.sun.xml.bind:jaxb-impl` and `jaxb-core`, `javax.activation:*`.
  - Add `jakarta.xml.bind-api` only if the code really uses JAXB.
- Replace `io.jsonwebtoken:jjwt:0.9.1` with three artifacts at `0.12.3`:
  - `jjwt-api` (compile scope)
  - `jjwt-impl` (runtime scope)
  - `jjwt-jackson` (runtime scope)
- Remove explicit versions on Boot-managed dependencies (lombok, h2, hibernate, jackson, mockito) so the parent manages them. Old Lombok fails on Java 21; it needs 1.18.30 or later.
- Replace springfox, if present, with `org.springdoc:springdoc-openapi-starter-webmvc-ui:2.3.0`.
- Use Python or careful `sed` for edits. Multi-line removal is easiest with a small Python script using `re.sub(r'\s*<dependency>\s*<groupId>javax\.xml\.bind</groupId>.*?</dependency>', '', s, flags=re.S)`.

**3. Namespace (main and test sources)**

Run this replacement:
```
find . -name "*.java" -exec sed -i -E 's/\bjavax\.(persistence|validation|servlet|annotation\.(PostConstruct|PreDestroy|Resource)|transaction)/jakarta.\1/g' {} +
```
- Do NOT change `javax.sql`, `javax.crypto` or `javax.net`; those belong to the JDK.
- Also check `persistence.xml` and any XML configs.

**4. Hibernate 6**
- Change `update from X` to `update X` in `@Query`.
- Remove `@Type(type=..)` and `@TypeDef`; use `@JdbcTypeCode(SqlTypes.JSON)` instead.
- Replace the legacy `session.createCriteria` with JPA `CriteriaBuilder`.
- Use `@GeneratedValue(strategy = GenerationType.IDENTITY)` and `@Enumerated(EnumType.STRING)`.
- In native SQL, use `true` rather than `1` for booleans.
- The H2 dialect can stay or be removed. Remove old renamed dialects such as `H2Dialect` variants and `MySQL5Dialect`.
- In properties, change `spring.jpa.hibernate.use-new-id-generator-mappings` (removed).

**5. Spring Security 6**

Rewrite the config class with no adapter:
```java
@Configuration @EnableWebSecurity @EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {
  @Bean PasswordEncoder passwordEncoder(){ return new BCryptPasswordEncoder(); }
  @Bean AuthenticationManager authenticationManager(AuthenticationConfiguration c) throws Exception { return c.getAuthenticationManager(); }
  @Bean SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http.csrf(c -> c.disable())
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .exceptionHandling(e -> e.authenticationEntryPoint((req,res,ex) -> res.sendError(HttpServletResponse.SC_UNAUTHORIZED, ex.getMessage())))
        .authorizeHttpRequests(a -> a.requestMatchers("/api/auth/**").permitAll() /* keep original rules, same order */ .anyRequest().authenticated())
        .headers(h -> h.frameOptions(f -> f.disable()))
        .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
    return http.build();
  }
}
```
- Keep the original matchers, using `requestMatchers(HttpMethod.X, ...)`.
- `UserDetailsService` and `PasswordEncoder` beans are auto-detected.
- If a `DaoAuthenticationProvider` is used, declare it as a `@Bean`.
- Beware circular dependencies: inject the JWT filter as a method parameter of `securityFilterChain` rather than a field.
- Filters extend `OncePerRequestFilter` with `jakarta.servlet.*`.

**6. JJWT 0.12 API**
- Key: `SecretKey key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));`. The secret must be at least 32 bytes for HS256. Lengthen it in `application.properties` (main and test) if needed, or derive it via SHA-256.
- Build a token:
  ```java
  Jwts.builder().subject(u).issuedAt(now).expiration(exp).claim("roles", r).signWith(key).compact()
  ```
- Parse a token:
  ```java
  Jwts.parser().verifyWith(key).build().parseSignedClaims(token).getPayload()
  ```
- Removed calls: `setSigningKey`, `parseClaimsJws` and `SignatureAlgorithm.HS512` with a String.
- Exceptions: catch `JwtException | IllegalArgumentException`. `SignatureException` is now `io.jsonwebtoken.security.SignatureException`.

**7. RestTemplate to RestClient (Spring 6.1)**
- Build the client with `RestClient.create()` or `RestClient.builder().baseUrl(baseUrl).build()`. Optionally provide a `@Bean RestClient`, and delete any `RestTemplate` bean.
- GET:
  ```java
  restClient.get().uri(baseUrl + "/users/{id}", id).accept(MediaType.APPLICATION_JSON).retrieve()
            .body(new ParameterizedTypeReference<Map<String,Object>>() {});
  ```
- POST: `restClient.post().uri(...).contentType(MediaType.APPLICATION_JSON).body(payload).retrieve().toBodilessEntity();`
- DELETE: `restClient.delete().uri(...).retrieve().toBodilessEntity();`
- Errors: `.onStatus(HttpStatusCode::is4xxClientError, (req,res) -> { throw ...; })`.
- Keep the existing try/catch, fallback return values and null checks (`response != null && ...`). Keep public method signatures unchanged.
- If tests mock `RestTemplate`, update them to match the new design, or construct the service with a `RestClient` so tests can stub it. Don't break test intent.

**8. Other Boot 3 breakages**
- `ResponseEntity.getStatusCode()` now returns `HttpStatusCode`.
- `ResponseEntityExceptionHandler` overrides take `HttpStatusCode` instead of `HttpStatus`.
- `WebMvcConfigurerAdapter` is gone; use `WebMvcConfigurer`.
- `spring.redis.*` became `spring.data.redis.*`.
- Trailing-slash matching is off by default.
- `@MockBean` still works in 3.2.

**9. Verify in a loop**
- Run `mvn -q clean compile 2>&1 | grep -E "ERROR|error:" | head -30` and fix, then repeat.
- Then run `mvn test 2>&1 | grep -E "Tests run|FAIL|ERROR|Caused by" | head -40`.
- For a failing test, read `target/surefire-reports/*.txt` with `head -60`.
- Finish by re-running the verification greps listed under Goal.
