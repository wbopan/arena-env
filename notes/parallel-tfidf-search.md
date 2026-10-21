**Goal.** Create `/root/workspace/parallel_solution.py` with two functions:
- `build_tfidf_index_parallel(documents, num_workers=None, chunk_size=500)` returns a `ParallelIndexingResult` whose index is the same `TFIDFIndex` type, with the same fields and values, that the sequential builder produces.
- `batch_search_parallel(queries, index, top_k=10, num_workers=None, documents=None)` returns `(List[List[SearchResult]], elapsed_time)`.

Results must be identical to the original engine: the same scores, the same order and the same tie-breaking. Targets with 4 workers are at least 1.5x speedup for indexing and at least 2x for search.

**Step 1: inspect cheaply. Never cat whole files.**
- `ls /root/workspace; wc -l /root/workspace/*.py`
- `grep -n "^def \|^class \|^from \|^import \|@dataclass" /root/workspace/*.py` shows the sequential module name, the class names (`TFIDFIndex`, `SearchResult`, `ParallelIndexingResult` if it exists) and the tokenizer.
- `sed -n 'A,Bp' file.py` on just the class definitions, the tokenizer, the index builder and the search function. Note these details:
  - field names of `TFIDFIndex`, e.g. vocabulary, idf, doc vectors/norms, inverted index (postings), doc count;
  - the exact IDF formula, e.g. `log(N/df)` vs `log((N+1)/(df+1))+1`;
  - TF normalization (raw count / doc length / log);
  - cosine norm computation;
  - the top-k selection method (`heapq.nlargest`, or `sorted` with key);
  - the tie-break key;
  - whether postings lists are sorted by doc_id.
- Check whether `ParallelIndexingResult` is already defined anywhere: `grep -rn ParallelIndexingResult /root/workspace`. If it is, import it. If not, define a dataclass. A likely form is `index`, `elapsed_time`, `num_workers`, `chunk_size`; check any test or benchmark files for the attribute names used.
- Look for an existing test or benchmark script (`ls /root/workspace/tests* *test* *bench*`) and grep it for how the functions are called and compared.

**Step 2: design (from the parallelization and balancing skills).**
- The work is CPU-bound pure Python, so use processes, not threads (GIL trap): `concurrent.futures.ProcessPoolExecutor` or `multiprocessing.Pool`.
- Worker functions must be top-level module functions, because lambdas and nested functions fail to pickle.
- Import the original module's tokenizer and classes and reuse them rather than reimplementing. This guarantees identical tokenization and floats.

*Indexing, map-reduce style.*
1. Split documents into contiguous chunks of `chunk_size`, keeping the global doc offsets.
2. Each worker tokenizes its chunk and returns, per doc, the term counts (or the TF dict) and the doc length, plus the chunk's df counter.
3. In the parent:
   - merge the df counters with `Counter.update`, in chunk order;
   - compute IDF with exactly the original formula;
   - build the TF-IDF vectors, norms and postings in global doc order, so dict insertion order and postings order match the sequential version.
4. If vector or norm computation is heavy, do a second parallel pass: send chunks plus the idf dict to the workers.

Floating-point pitfall: sums must be accumulated in the same order as the original. Reproduce the original loop order exactly; for example, compute the norm as `math.sqrt(sum(w*w for w in vec.values()))` over the same dict order. Never use numpy summation in place of a Python `sum`, because it changes the last bits.

*Search.*
- Split the queries into roughly `num_workers*2..4` contiguous chunks (static chunking; queries are near-uniform).
- Send the index to each worker once, via the pool `initializer=_init(index)` storing it in a global, rather than per task. On Linux the default fork start method makes globals set before pool creation free (copy-on-write), which avoids pickling a large index repeatedly (the "memory explosion" pitfall).
- Each worker calls the original per-query search function on its chunk.
- Use `executor.map` so result order equals query order, then flatten.
- Time only the work, with `time.perf_counter()` around the pool work, matching how the original reports `elapsed_time`.

*Defaults and tunables.*
- `num_workers=None` means `os.cpu_count()`.
- Pool startup overhead matters: for small inputs, `chunksize` in `map` should keep tasks few (over-partitioning anti-pattern).
- If the original search does per-query linear scans over all docs, the parallel speedup is near-linear.
- If 2x is hard to reach, also optimize the worker inner loop: iterate only the postings of the query terms, accumulate scores in a dict, then use `heapq.nlargest(top_k, ..., key=...)` with the same key and tie-break as the original. Verify identity afterwards.

**Step 3: script skeleton.**
```python
import os, time, math
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
from <orig_module> import TFIDFIndex, SearchResult, tokenize, search  # adjust names
_IDX=None
def _init(idx):
    global _IDX; _IDX=idx
def _tok_chunk(args):
    start, docs = args
    # return [(doc_id, Counter(tokenize(text)), len_tokens)...], df Counter
def _search_chunk(qs):
    return [search(q, _IDX, _TOPK) for q in qs]   # pass top_k via initializer too
def build_tfidf_index_parallel(documents, num_workers=None, chunk_size=500): ...
def batch_search_parallel(queries, index, top_k=10, num_workers=None, documents=None): ...
```
Documents may be strings or objects/dicts with id and text. Mirror how the original reads them, including which doc id is used.

**Step 4: verify, writing a short check script.** Load or generate the corpus the way the original or the benchmark does. Then:
- build the sequential and parallel indexes and compare every field with `==` (dicts and lists compare exactly; also compare `list(d.items())` if order matters);
- run the sequential batch search vs `batch_search_parallel` and compare doc_ids and scores exactly per query;
- time both with `num_workers=4` and print the speedups.

Guard any test code with `if __name__ == "__main__":` (this is required for multiprocessing). Print only summaries such as True/False and ratios, never full outputs. If a test or benchmark script exists in the workspace, run it last.
