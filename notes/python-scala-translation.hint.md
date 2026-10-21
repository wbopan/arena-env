1. Grep and `sed -n` through `/root/Tokenizer.py` class by class: enum values, Token fields, the dispatch in each tokenizer, the raises, and the builder methods. Check which of `scalac`/`scala-cli`/`sbt` is available.
2. Write `/root/Tokenizer.scala` using only the standard library. Use a sealed trait `TokenType` with UPPERCASE case objects, a `Token` case class with `withMetadata` via `copy`, and a `BaseTokenizer` trait providing `tokenize`, `tokenizeBatch` and `toToken`. Use `match` instead of `isinstance`, `Option`/`Try`/`Either` instead of None and exceptions, `java.time` for dates, and an immutable `TokenizerBuilder`.
3. Compile it with Scala 2.13 (`scalac -d /tmp/out`) and fix the errors.
4. Run a small `Check` object and compare its output with the Python on the same inputs.
5. Grep that all 13 required names are present and that there is no `var`, `null` or `asInstanceOf`.
