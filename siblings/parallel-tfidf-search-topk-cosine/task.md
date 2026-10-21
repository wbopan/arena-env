# TF-IDF Top-k Cosine Search (Reference Results)

A document search engine has to be reproduced exactly so that a parallel version can later be validated against it. Compute the reference search results.

## Inputs
- `/root/work/corpus.jsonl`: one JSON object per line, `{"doc_id": str, "text": str}`.
- `/root/work/queries.json`: a JSON list of `{"qid": str, "text": str}`.

## Conventions
- **Tokenization**: lowercase the text. Tokens are the maximal runs matching `[a-z0-9]+`. Every other character is a separator.
- `N` is the number of documents. `df(t)` is the number of documents that contain term `t`.
- `idf(t) = ln((1 + N) / (1 + df(t))) + 1`, using the natural log.
- `tf(t, d) = (count of t in d) / (total number of tokens in d)`.
- **Document vector**: `w(t, d) = tf(t, d) * idf(t)`, then L2-normalized.
- **Query vector**: built the same way, using:
  - the query's own token counts and token length;
  - the corpus idf.
- Query terms that are absent from the corpus vocabulary get weight 0. L2-normalize the query vector as well.
- **Score**: the dot product of the normalized query vector and the normalized document vector.

## Task
For each query, return the top 5 documents with score > 0.
- Order them by score descending. Break ties by `doc_id` ascending.
- If fewer than 5 documents score above 0, return only those. This may be zero documents.

## Output
Write `/root/work/results.json`.
- It is a JSON object that maps **every** qid to a list of `{"doc_id": str, "score": float}`.
- Each list is in rank order.
- Round `score` to 6 decimal places.
