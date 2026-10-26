## Reference notes

Use Python’s standard library (`re`, `csv`); inspect the three small text files before writing the script. The planning skill describes `unified_planning` APIs, but that package is not among the allowed libraries. A small S-expression parser is sufficient for the PDDL constructs present after inspection.

```python
import re

def parse_pddl(text):
    # PDDL comments run from ; to end of line; names are case-insensitive.
    text = re.sub(r";[^\n]*", "", text).lower()
    tokens = iter(re.findall(r"[()]|[^()\s]+", text))
    def expr():
        token = next(tokens)
        if token != "(":
            return token
        result = []
        for token in tokens:
            if token == ")":
                return result
            result.append(expr_from_first(token))
        raise ValueError("unclosed expression")
    def expr_from_first(token):
        if token != "(":
            return token
        result = []
        for token in tokens:
            if token == ")":
                return result
            result.append(expr_from_first(token))
        raise ValueError("unclosed expression")
    return expr()
```

Inspect the parsed forms for the problem’s `:init` and `:goal`, and each domain `:action`’s `:parameters`, `:precondition`, and `:effect`. A ground atom can be represented as a tuple such as `("at", "truck", "place")`; keep the current state as a `set` of positive atoms. For a grounded action, substitute parameter names with its line’s arguments **by position**. In conjunctions, every positive precondition must be in the state and every `(not (...))` precondition must be absent. Collect positive effects as additions and negated effects as deletions; apply them only when all preconditions held in the *pre-action* state. Do not infer reverse roads.

Read candidate lines with `Path(...).read_text(encoding="utf-8").splitlines()`: this removes line endings but preserves the line’s other characters for the `action` column. Parse a line’s action name and arguments separately without changing the stored original. Process every line, including after an inapplicable action or a satisfied goal. Determine location, cargo, delivered goods, and whether **all goal goods** are delivered from the resulting state, using the predicates and objects actually declared in the files.

Write with `open(path, "w", encoding="utf-8", newline="")` and `csv.writer`; write exactly the specified header, then one row per candidate line. Use `";".join(sorted(goods)) or "-"` for delivered goods. Check the CSV’s row count and inspect its beginning and end after running.
