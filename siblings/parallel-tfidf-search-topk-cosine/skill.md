## Reference notes

Use Python’s standard-library `json`, `re`, `collections.Counter`, and `math`; no parallelism is needed for the reference computation.

```python
TOKEN_RE = re.compile(r"[a-z0-9]+")
tokens = TOKEN_RE.findall(text.lower())
counts = Counter(tokens)
```

- Read JSONL **one line at a time** with `json.loads(line)`; read the queries file with `json.load(f)`, since it is a single JSON array.
- Count `df` once per term **per document** (`for term in counts`, not once per occurrence). `N` includes empty documents.
- Use `math.log((1 + N) / (1 + df[term])) + 1` for corpus terms. Ignore out-of-vocabulary query terms; do not add them to `df`.
- For a nonempty text, divide each term count by the text’s **full token count** before multiplying by IDF. Then divide all weights by `math.sqrt(sum(w*w for w in weights.values()))`. An empty document or a query with no corpus terms has a zero vector and produces no positive matches.
- Score with the dot product of normalized vectors. Sort **unrounded** positive scores by `(-score, doc_id)`, take at most five, and only then apply `round(score, 6)`. Rounding before ranking can create false ties.
- Sparse dictionaries of nonzero term weights avoid a dense document-by-vocabulary matrix. Process queries individually and retain only the results needed for output.
- Write one JSON object containing every `qid`, including those whose result is `[]`, using `json.dump(...)`. JSON numbers should be Python floats, not formatted strings.
