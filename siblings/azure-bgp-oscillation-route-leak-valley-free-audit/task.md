Audit observed BGP route propagations in a multi-tier Azure Virtual WAN / ExpressRoute topology for route leaks, using the valley-free (Gao-Rexford) export rules.

Inputs:
- `/root/work/relationships.csv` has the columns `as_a,as_b,relationship`. A row `A,B,customer` means B is A's customer. The `relationship` value is one of `customer`, `provider` or `peer`. Each adjacent pair appears exactly once, in either orientation. You must infer the reverse view yourself: if B is A's customer, then A is B's provider. Peer relationships are symmetric.
- `/root/work/propagations.json` is a list of objects `{"path_id": int, "prefix": str, "as_path": [int, ...]}`. `as_path` is in propagation order: `as_path[0]` originated the prefix, and `as_path[i+1]` received the route from `as_path[i]`.

Check every interior AS on every path, meaning positions 1 to len-2:
- `leaker_as` is the AS at position i.
- `source_as` is the AS at position i-1.
- `destination_as` is the AS at position i+1.
- `source_type` is what the source is to the leaker, and `destination_type` is what the destination is to the leaker. Each is `customer`, `provider` or `peer`.

An export is a route leak when `source_type` is `provider` or `peer` AND `destination_type` is `provider` or `peer`. Routes learned from customers may be exported to anyone.

Write `/root/work/route_leaks.csv` with this exact header:

`path_id,prefix,leaker_as,source_as,destination_as,source_type,destination_type`

Write one row per leak. Sort rows by `path_id` ascending, then by the leaker's position in the path. Use plain integers for ASNs and lowercase type names. If no leaks are found, the file contains only the header.
