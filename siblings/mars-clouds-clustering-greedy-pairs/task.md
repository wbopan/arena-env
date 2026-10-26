# Match Mars Cloud Centroids to Expert Marks

Two files in `/root/work` describe positions in pixel coordinates: `centroids.csv` has columns `file_rad,cluster_id,x,y`, and `expert.csv` has columns `file_rad,expert_id,x,y`. IDs are integers unique within their image. Consider every image appearing in either file, and never match positions from different images.

For each image, calculate standard Euclidean distances between every centroid and every expert mark. Consider only pairs at distance at most 16 pixels, including pairs exactly on the boundary. Sort eligible pairs by increasing unrounded distance, breaking ties by smaller `cluster_id` and then smaller `expert_id`. Traverse that order once, accepting a pair only if neither endpoint has already been accepted. This is greedy matching, not a minimum-cost global assignment.

Write one UTF-8 JSON file at `/root/work/matches.json`. Its top-level object has exactly one field, `images`, containing a list sorted by `file_rad`. Each image object has exactly `file_rad`, `matches`, `unmatched_clusters`, and `unmatched_experts`. Each match has exactly `cluster_id`, `expert_id`, and `distance_px`; list matches in acceptance order. Round `distance_px` to three decimal places after matching. List unmatched IDs as ascending integers. Empty lists are required where appropriate; do not omit images without centroids.
