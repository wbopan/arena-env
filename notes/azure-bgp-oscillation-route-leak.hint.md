Inspect /app/data/*.json with small python one-liners (keys, the preference map, relationships, the list of solution strings); do not cat large files.
Write one stdlib-json script that finds the preference cycle (ASN→preferred next hop) and the valley-free leaks (provider/peer-learned route exported to a peer/provider, recorded with int ASNs and type strings).
Classify each solution: routing intent and UDR fix both; filtering peer-learned routes before re-advertising fixes oscillation; valley-free export fixes leaks; timers, dampening, restart, disabling BGP/peering and ingress-only filtering fix nothing.
Write /app/output/oscillation_report.json in the exact format, keyed by the exact solution strings, then reload it to verify keys, types and solution count.
