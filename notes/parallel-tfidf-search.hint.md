1. Grep `/root/workspace/*.py` for classes and functions; read only the tokenizer, the index builder, the search function, and the `TFIDFIndex`/`SearchResult`/`ParallelIndexingResult` definitions.
2. Write `/root/workspace/parallel_solution.py` with `ProcessPoolExecutor` and top-level workers:
   - indexing: chunk-tokenize and count in workers, merge df and build IDF/vectors/postings in global doc order using the original formulas;
   - search: query chunks run the original search, with the index passed once via the pool initializer, using `map` to preserve order.
3. Verify exact equality of index fields and search results against the sequential code, and check speedups at 4 workers (≥1.5x build, ≥2x search) under `if __name__ == "__main__"`.
