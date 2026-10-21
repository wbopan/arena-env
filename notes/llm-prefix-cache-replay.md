**Inputs**
- `/root/trace.jsonl` holds one JSON object per line: `timestamp`, `input_length`, `output_length`, `hash_ids` (a list of ints, already block-level, so do not re-hash).
- `timestamp` and `output_length` do not affect the replay.
- `/root/config.json` holds `block_size`, `cache_capacity_blocks`, `policy` (S3FIFO), and `s3fifo.small_ratio` and `s3fifo.max_freq`.

Inspect cheaply:
```
cat /root/config.json
wc -l /root/trace.jsonl; head -c 400 /root/trace.jsonl
python3 -c "import json;r=[json.loads(l) for l in open('/root/trace.jsonl')];print(len(r),sum(len(x['hash_ids']) for x in r))"
```
Use only the standard library (`json`, `collections.OrderedDict`).

**Per-request semantics**
1. Before any side effects, compute `k` = the length of the longest run `h_0..h_{k-1}` that is all resident. Resident means in S or M; the ghost does NOT count. Stop the scan at the first miss.
2. `prompt_tokens = input_length`.
3. `hit_tokens = min(k*block_size, input_length)`. The clamp is mandatory.
4. Then, for EVERY `h` in `hash_ids` in order (not just the prefix part), apply the S3FIFO access rule.

**S3FIFO sizes**
- `small_cap = round(capacity*small_ratio)`. Use `round`, not `int`.
- `main_cap = capacity - small_cap`.
- `ghost_cap = main_cap`.

**S3FIFO data structures**
- S and M are OrderedDicts mapping hash to freq. The head is the oldest entry; the tail is the newest.
- G is an OrderedDict of hashes only.

**Access rule for `h`**
- If `h` is in S or M: `freq = min(freq+1, max_freq)`. Position does not change.
- Elif `h` is in G: delete it from G, then `admit_M(h, 0)`.
- Else: `admit_S(h)`.

**`admit_S(h)`**
- While `len(S) >= small_cap`, pop the head `(v, f)`:
  - if `f >= 1`, call `admit_M(v, f)`, keeping `f` (do NOT reset it);
  - otherwise insert `v` into the ghost.
- Then `S[h] = 0`.

**`admit_M(h, f)`**
- While `len(M) >= main_cap`, pop the head `(v, vf)`:
  - if `vf >= 1`, re-append `v` at the tail with `vf-1` and continue;
  - otherwise insert `v` into the ghost and break (exactly one real eviction).
- Then `M[h] = f`.

**`ghost_insert(h)`**
- If `h` is in G, delete it.
- Elif `len(G) >= ghost_cap`, pop the head.
- Then `G[h] = None`.

**Guards**
- If `small_cap == 0` or `main_cap == 0`, guard the loops so they cannot run on an empty queue. Breaking when the queue is empty is fine.

**Script core**
```python
import json
from collections import OrderedDict
c=json.load(open('/root/config.json')); B=c['block_size']; C=c['cache_capacity_blocks']
sr=c['s3fifo']['small_ratio']; MF=c['s3fifo']['max_freq']
SC=round(C*sr); MC=C-SC; GC=MC
S,M,G=OrderedDict(),OrderedDict(),OrderedDict()
def gins(h):
    if h in G: del G[h]
    elif len(G)>=GC and G: G.popitem(last=False)
    if GC>0: G[h]=None
def admM(h,f):
    while M and len(M)>=MC:
        v,vf=M.popitem(last=False)
        if vf>=1: M[v]=vf-1
        else: gins(v); break
    M[h]=f
def admS(h):
    while S and len(S)>=SC:
        v,vf=S.popitem(last=False)
        if vf>=1: admM(v,vf)
        else: gins(v)
    S[h]=0
def access(h):
    if h in S: S[h]=min(S[h]+1,MF)
    elif h in M: M[h]=min(M[h]+1,MF)
    elif h in G: del G[h]; admM(h,0)
    else: admS(h)
per=[];TP=TH=0
for i,l in enumerate(open('/root/trace.jsonl')):
    if not l.strip(): continue
    r=json.loads(l); hs=r['hash_ids']; L=r['input_length']
    k=0
    for h in hs:
        if h in S or h in M: k+=1
        else: break
    hit=min(k*B,L)
    for h in hs: access(h)
    per.append({"idx":len(per),"prompt_tokens":L,"hit_tokens":hit}); TP+=L; TH+=hit
json.dump({"total_requests":len(per),"total_prompt_tokens":TP,"total_hit_tokens":TH,
 "overall_hit_rate":TH/TP if TP else 0.0,"final_cache_blocks":len(S)+len(M),
 "per_request":per},open('/root/report.json','w'),indent=1)
```

Duplicate hashes inside one request are handled naturally: the second access sees the block as resident and increments its freq. The `M[v]=vf-1` line runs after the pop, so the entry is appended at the tail (OrderedDict assignment of a new key appends).

**Pitfalls**
- Do not use LRU.
- Do not count ghost entries as hits or as residency.
- Do not use set intersection instead of the longest prefix.
- Do not update freq only on prefix blocks.
- Do not leave freq unclamped.
- Do not reset freq on S→M promotion.
- Do not include the ghost in `final_cache_blocks`.
- Do not use `int()` for `small_cap`.
- Do not requeue at the head.

**Output: `/root/report.json`**
- `total_requests` (int).
- `total_prompt_tokens` = sum of `input_length` (int).
- `total_hit_tokens` (int).
- `overall_hit_rate` = `total_hit_tokens/total_prompt_tokens` (float).
- `final_cache_blocks` = `|S|+|M|` (int).
- `per_request`: a list of `{idx, prompt_tokens, hit_tokens}` in trace order, with `idx` running from 0.

**Plan**
1. Inspect the config and trace head.
2. Write `/root/sim.py` with the core above.
3. Run it.
4. Verify with a one-liner:
   - the sum of `per_request` hit tokens equals `total_hit_tokens`, and likewise for prompt tokens;
   - the rate equals the ratio;
   - `final_cache_blocks <= capacity`;
   - the length of `per_request` equals the line count;
   - the first request has 0 hits.
5. Print only the top-level fields, never the whole `per_request` array.
