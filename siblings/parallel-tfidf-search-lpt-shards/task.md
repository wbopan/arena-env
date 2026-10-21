# Load-Balanced Sharding of a TF-IDF Indexing Job

Before an inverted index is built in parallel, the documents are distributed over workers so that each worker's tokenization work is balanced. Reproduce the scheduler's assignment.

## Inputs
- `/root/work/corpus.jsonl`: one JSON object per line, `{"doc_id": str, "text": str}`.
- `/root/work/config.json`: `{"num_workers": K}`.

## Conventions
- **Tokenization**: lowercase the text. Tokens are the maximal runs matching `[a-z0-9]+`. Every other character is a separator, including hyphens and apostrophes.
- **Cost of a document**: its number of tokens, counted with repetition.
- **Scheduling**: Longest-Processing-Time greedy.
  1. Sort the documents by cost descending. Break ties by `doc_id` ascending, using plain string comparison.
  2. Workers are numbered `0..K-1` and all start with load 0.
  3. Take the documents in sorted order. Assign each one to the worker with the smallest current load, breaking ties by the lowest worker index. Then add the document's cost to that worker's load.

## Output
Write `/root/work/schedule.json`:
```
{"workers": [{"worker": 0, "doc_ids": [...], "load": int, "num_terms": int}, ...],
 "makespan": int,
 "imbalance": float}
```
- `workers` contains all K workers in worker-index order, including any worker with no documents.
- `doc_ids` lists the worker's documents in the order they were assigned.
- `load` is the sum of the costs of the worker's documents.
- `num_terms` is the number of distinct tokens across all of that worker's documents.
- `makespan` is the maximum load.
- `imbalance` is `makespan / (total cost / K)`, rounded to 4 decimal places.
