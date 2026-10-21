**Goal.** Write `/root/Tokenizer.scala`, a single Scala 2.13 source file. It must compile and behave like `/root/Tokenizer.py`. It must define these names exactly: `TokenType`, `Token`, `BaseTokenizer`, `StringTokenizer`, `NumericTokenizer`, `TemporalTokenizer`, `UniversalTokenizer`, `WhitespaceTokenizer`, `TokenizerBuilder`, and the methods `tokenize`, `tokenizeBatch`, `toToken`, `withMetadata`. Use only the standard library: no circe, cats or logging libraries, because they will not be on the classpath. Avoid a `package` line unless the Python file or the tests suggest one. Keep the file self-contained.

**Inspect cheaply first.**
- `wc -l /root/Tokenizer.py`
- `grep -nE "^class|def |Enum|raise|except|Optional|None|isinstance|datetime|re\.|@" /root/Tokenizer.py | head -80`
- Then read sections with `sed -n 'A,Bp'`, one class at a time.
- `ls /root; ls /root/tests 2>/dev/null` to look for hidden-test hints such as an sbt project or a test spec.
- `which scalac scala sbt scala-cli; scala -version 2>&1`
- Note the enum values (the strings), the dataclass fields with their defaults, the abstract methods, how each tokenizer dispatches on input type, the error cases (`raise`), and the builder chain methods.

**Translation conventions (from the skills).**
- **Enum.** Use a sealed trait with UPPERCASE case objects. Do not use PascalCase members. Add a lookup that returns an `Option`:
  ```scala
  sealed trait TokenType { def value: String }
  object TokenType {
    case object STRING extends TokenType { val value = "string" }
    case object NUMERIC extends TokenType { val value = "numeric" }
    // ...one per Python member, same string values
    val values: List[TokenType] = List(STRING, NUMERIC /*...*/)
    def fromString(s: String): Option[TokenType] = values.find(_.value == s)
  }
  ```
- **Dataclass to case class.** Use an immutable case class with defaults. A Python `Optional[...]` field becomes `Option[...] = None`. A `dict` becomes `Map[String, Any]` or a narrower type.
  ```scala
  final case class Token(value: String, tokenType: TokenType,
      metadata: Map[String, Any] = Map.empty /* other fields */) {
    def withMetadata(kv: (String, Any)*): Token = copy(metadata = metadata ++ kv)
  }
  ```
  Use `copy` rather than mutating. If Python's `with_metadata` takes `**kwargs`, use varargs pairs or a `Map`. Use camelCase for fields (`token_type` becomes `tokenType`).
- **ABC to trait.** Use `trait BaseTokenizer` (or an abstract class) with abstract `def tokenize(...)`. Put concrete shared logic in the trait, for example `def tokenizeBatch(inputs: Seq[A]): Seq[...] = inputs.map(tokenize)`. If Python's batch skips or collects failures, mirror that with `flatMap`, `Option` or `Either`.
- **`toToken`.** Implement it on the tokenizer, or as a helper, as in the Python. It converts a raw value to a `Token`.
- **Type dispatch.** Replace `isinstance` chains with pattern matching:
  ```scala
  value match {
    case null | None => ...NULL token...
    case s: String => ...
    case n: Int => ...; case d: Double => ...; case b: BigDecimal => ...
    case t: java.time.temporal.TemporalAccessor => ...
    case other => ...
  }
  ```
  Handle `null` from callers by wrapping with `Option(x)`. Never return `null`.
- **Errors.** Python `try/except ValueError` maps to `Try(s.toDouble)`, `s.toIntOption` or `s.toDoubleOption` (all in Scala 2.13). Expose failures as `Option`, `Either[String, A]` or `Try`. Where Python raises on invalid arguments, use `require(...)`, which throws `IllegalArgumentException`, or return `Either`. Keep the observable behaviour identical: if Python raises, the Scala code should throw or return `Left`, matching the Python semantics.
- **Datetime.** Use `java.time`. `LocalDateTime`, `LocalDate` and `Instant` correspond to Python `datetime`. `.isoformat()` maps to `toString`, but check the format: Python `isoformat` drops zero seconds differently. If exact strings matter, use `DateTimeFormatter.ISO_LOCAL_DATE_TIME`. `strftime("%Y-%m-%d")` maps to `DateTimeFormatter.ofPattern("yyyy-MM-dd")`. Parsing should be `Try(LocalDate.parse(s)).toOption`.
- **Regex and whitespace.** `re.split(r"\s+", s)` maps to `s.split("\\s+").toList`, or `s.trim.split("\\s+").filter(_.nonEmpty)`. `str.split()` with no argument drops empty strings, so filter them out. `re.findall` maps to `"""...""".r.findAllIn(s).toList`.
- **Numbers.** Python `str(3.0)` gives `"3.0"`, and Scala `3.0.toString` gives `"3.0"`, so they match. Python ints are unbounded; use `Long` or `BigInt` if large values matter. `round(x, n)` maps to `BigDecimal(x).setScale(n, RoundingMode.HALF_EVEN)`, because Python rounds half to even.
- **String case.** `lower()` maps to `toLowerCase`. If the Python normalises case, use `toLowerCase(Locale.ROOT)`.
- **Builder.** Translate `TokenizerBuilder` as an immutable case class. Each `with_x(...)` method returns `copy(x = ...)`, and `build()` returns the configured tokenizer. Translate it this way even if the Python mutates `self` and returns `self`. Give it a companion `object TokenizerBuilder { def apply(): TokenizerBuilder = ... }` if that is useful.
- **Universal tokenizer.** `UniversalTokenizer` likely delegates to the other tokenizers. Hold them in an immutable `List` or `Map[TokenType, BaseTokenizer]`, and select one with `find` or `collectFirst`.
- **General style.** Use `val`, immutable collections, expression-bodied `def`s, `match` instead of if/elif chains, string interpolation `s"..."`, `private` instead of a leading `_`, `final` on leaf classes, and `override` on implementations. Use camelCase for methods and fields. Do not use `var`, `null`, `asInstanceOf` or `return`. A `mutable.ListBuffer` is acceptable only if it stays local.
- **Readability.** Add short Scaladoc comments. Order the file as: TokenType, Token, BaseTokenizer, the concrete tokenizers, then the builder.

**Plan (about 30 commands).**
1. Run the inspection commands above, reading the Python class by class (about 6–8 commands).
2. Write the whole file with a single `cat > /root/Tokenizer.scala <<'EOF' ... EOF`.
3. Compile it:
   - If `scalac` exists: `mkdir -p /tmp/out && scalac -d /tmp/out /root/Tokenizer.scala 2>&1 | head -40`.
   - Otherwise try `scala-cli compile --scala 2.13 /root/Tokenizer.scala`.
   - Otherwise, if `sbt` exists, use a tiny `/tmp/proj` with `scalaVersion := "2.13.x"` and copy the file into `src/main/scala`.
   - Fix the errors and recompile. Show only the first errors (`| head`).
4. Run a behaviour check. Write `/tmp/Check.scala` with an `object Check extends App` that calls each tokenizer on the same inputs as a Python run. Print the results and compare them with `python3 -c "import sys; sys.path.insert(0,'/root'); from Tokenizer import *; ..."`. Run it with `scala -cp /tmp/out /tmp/Check.scala`, or compile both files together.
5. Do a final grep to confirm all the required names exist:
   `for n in TokenType Token BaseTokenizer StringTokenizer NumericTokenizer TemporalTokenizer UniversalTokenizer WhitespaceTokenizer TokenizerBuilder tokenize tokenizeBatch toToken withMetadata; do grep -q "$n" /root/Tokenizer.scala || echo MISSING $n; done`
   Also confirm there is no `null` returned and no `var`: `grep -nE "\bvar\b|= null|asInstanceOf" /root/Tokenizer.scala`.

**Output.** The output is `/root/Tokenizer.scala` only: one compilable Scala 2.13 file with all the classes and methods above, behaviour-equivalent to the Python, and idiomatic.
