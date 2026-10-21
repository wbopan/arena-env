**Inputs and first look (keep it cheap)**

All inputs are in `/app/data/`. Expect `route.json`, `preferences.json`, `local_pref.json` and `possible_solutions.json`. There may also be `topology.json`, `relationships.json` or `route_leaks.json`. Never print whole files. Inspect each one with:
- `ls /app/data`
- `wc -c /app/data/*`
- `python3 -c "import json;d=json.load(open('/app/data/X.json'));print(type(d).__name__, list(d)[:10] if isinstance(d,dict) else d[:3])"`
- Then print individual keys or the first entries.

What to learn from each file:
- **route.json**: the prefix and the origin AS (the vnet). It may also contain the AS_PATH or advertisement chain, i.e. who advertised to whom.
- **preferences.json**: which hub prefers a route via which neighbor, giving ASN → preferred next-hop ASN. Keys may be strings or names such as `vhubvnet1`. Map names to ASNs and cast to `int`.
- **local_pref.json**: a weight per relationship type (customer/peer/provider). It may also give the relationship of each neighbor pair.
- **possible_solutions.json**: a list or dict of solution strings. Its exact strings become the keys of the output.

Use only the Python stdlib (`json`). No other libraries are needed.

**Oscillation detection (preference cycle)**

1. Build `pref = {int(asn): int(preferred_next_hop)}`.
2. Walk from each node until a repeat appears. A 2-node cycle is enough to conclude oscillation.

```python
def find_cycle(pref):
    for s in pref:
        path, seen, cur = [], {}, s
        while cur in pref:
            if cur in seen: return path[seen[cur]:]
            seen[cur] = len(path); path.append(cur); cur = pref[cur]
    return None
```

- `oscillation_detected` = cycle is not None.
- `oscillation_cycle` = list of ASNs in the cycle (ints, e.g. sorted or in walk order starting at the smallest).
- `affected_ases` = ASNs in the cycle, plus any others the data marks as impacted.

If preferences are expressed as local-pref numbers per neighbor, the preferred next hop is the neighbor with the highest value.

**Route leak detection (valley-free, Gao–Rexford)**

Export rules:
- A route learned from a customer may be exported to anyone.
- A route learned from a peer or a provider may be exported to customers only.

A leak is any AS X that learned the route from S (S's relationship to X is provider or peer) and exported it to D (D's relationship to X is peer or provider).

Typical vWAN layout: Virtual WAN 65001 sits above the hubs (65002 and 65003), and the hubs are peers of each other. Derive the actual relationships from the data, never from memory.

Walk the advertisement chain from `route.json` (consecutive triples S→X→D). Alternatively, check every hub that has a learned route and re-advertises it to a peer or provider.

Record each leak with exactly these keys and types:
`{"leaker_as": X, "source_as": S, "destination_as": D, "source_type": "provider"|"peer"|"customer", "destination_type": "peer"|"provider"|"customer"}`
- ASNs are ints.
- The type strings describe the relationship as seen from the leaker (S is X's provider, D is X's peer).

`route_leak_detected` = `len(route_leaks) > 0`.

**Solution classification**

For each solution string, decide two booleans:
- **oscillation_resolved**: true only if the fix breaks the preference cycle, or makes forwarding deterministic regardless of the cycle.
- **route_leak_resolved**: true only if the fix stops hub1 and hub2 from advertising or using each other's routes via Virtual WAN, i.e. it enforces valley-free behaviour.

Rules from the skill:
- **Virtual WAN routing intent / routing policy** (forces hub-to-hub traffic through 65001): oscillation true, leak true.
- **UDR (static next hop, e.g. to the Virtual WAN hub or firewall)**: oscillation true, leak true. It is a data-plane override that supersedes BGP and leaked routes.
- **Export/route filter: a hub filters routes learned from the other hub before re-advertising**: oscillation true (it removes one leg of the cycle). Leak is true if it stops that hub re-advertising peer- or provider-learned routes to the other hub. Check the wording against the leak criterion.
- **Enforce valley-free export, no-export community, or stop advertising provider/peer routes to peers**: leak true. Oscillation is true only if it also removes a cycle edge.
- **Changing preferences / local-pref so one hub no longer prefers the other**: oscillation true. Leak is true only if it also stops the cross-hub advertisement.
- **Ingress filtering only / accept fewer prefixes / max-prefix**: leak false (pitfall), and oscillation false unless it explicitly removes the cycle edge.
- **RPKI origin validation**: listed in the skill as a leak tool, but judge it by the task criterion. It does not stop hubs advertising a validly-originated route to each other.
- **Timer tuning (keepalive/holdtime), route dampening, restart/reset gateway, shut down gateways**: oscillation false, leak false.
- **Disable BGP, disable or remove hub peering, delete connections, remove connectivity**: prohibited in Azure, so false and false.

Implement this as keyword rules in the script, then print each solution with its verdict and eyeball every one. Adjust any solution whose wording does not fit a rule. Every solution in the file must appear, using its exact original string as the key.

**Output requirements**

Write `/app/output/oscillation_report.json` (create the directory with `os.makedirs(..., exist_ok=True)`) using `json.dump(..., indent=2)`. Required keys:
- `oscillation_detected` (bool)
- `oscillation_cycle` (list of int)
- `affected_ases` (list of int)
- `route_leak_detected` (bool)
- `route_leaks` (list of dicts as above)
- `solution_results`: a dict mapping each solution string to `{"oscillation_resolved": bool, "route_leak_resolved": bool}`

Use JSON booleans, not strings. If nothing is detected, use empty lists and still evaluate every solution.

**Plan (about 8–12 commands)**

1. `ls` and `wc` on the data files, then structure one-liners for each file.
2. Print `preferences.json`, `route.json` and `local_pref.json` (they are small), plus only the solution strings: `python3 -c "...;[print(i,s) for i,s in enumerate(sols)]"`.
3. Write `/app/solve.py`: load files → find cycle → find leaks → classify solutions → dump the report.
4. Run it, then `python3 -c` to reload the output and assert the key set, the types, and that the number of solutions matches the input.
5. Review the printed verdict table, fix any misclassified rules, and rerun.
