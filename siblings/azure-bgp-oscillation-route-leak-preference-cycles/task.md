In an Azure Virtual WAN-style deployment, every BGP speaker (virtual hub, gateway or VNet ASN) has one preferred next-hop ASN for a contested prefix. A cycle in this preference graph means the speakers keep switching their best path, which is BGP oscillation. Classify every speaker.

Input: `/root/work/preferences.json` is a JSON object.
- Each key is an ASN, written as a string.
- Each value is the ASN that speaker prefers to route via (an integer), or `null` if the speaker has no preference and uses its own direct route.
- A preferred ASN that is not itself a key is an external speaker with no preference. It ends a chain.

Compute:
- `cycles`: every preference cycle, as a list of lists. Write each cycle in preference order: each AS prefers the next one, and the last AS prefers the first. Rotate each cycle so its numerically smallest ASN comes first. Sort the cycles by their first ASN.
- `oscillating_ases`: every ASN that belongs to any cycle, in ascending order.
- `affected_ases`: every key ASN whose chain of prefer-via links eventually reaches a cycle member. Include the cycle members themselves. Ascending order.
- `stable_ases`: all remaining key ASNs, in ascending order.
- `oscillation_detected`: `true` if and only if at least one cycle exists.

Write `/root/work/oscillation_report.json` in this form:

```json
{"oscillation_detected": true, "cycles": [[65003, 65017]], "oscillating_ases": [65003, 65017], "affected_ases": [65003, 65010, 65017], "stable_ases": [65001, 65002]}
```

Write every ASN as a JSON integer. Every key ASN must appear in exactly one of `affected_ases` and `stable_ases`.
