# Estimate station clock offsets from P picks

Inputs under `/root/work` are `stations.csv`, `events.csv`, and `picks.csv`. Station coordinates `x_km,y_km` are local Cartesian kilometers; stations are at depth zero. Each catalog event specifies its origin `time_s` and source `x_km,y_km,depth_km`. A pick has a station ID, observed `time_s`, probability `prob`, and a channel name. All times are seconds after recording start.

Use a straight-line P-wave velocity of 6 km/s. For each pick, calculate its residual against every catalog event: observed arrival minus event origin time minus source-to-station travel time. Associate the pick with the event having the smallest absolute residual; break an exact tie using the lexicographically smaller `event_id`. Reject it if its probability is below 0.8 or its associated absolute residual exceeds 2 seconds.

Multiple channels can produce picks for one station and event. Keep only the pick with the highest probability for each `(station_id,event_id)` pair; if probabilities tie, keep the earlier observed pick. For each station, take the median residual of its remaining picks as its clock offset.

Write exactly `/root/work/clock_offsets.json`: a JSON array sorted by `station_id`. Each object has exactly `station_id`, `offset_s`, and `count`. `offset_s` is the median in seconds rounded to three decimal places; `count` is the number of retained station-event pairs. Include every station, even one with no retained picks; for that case use `null` offset and zero count.
