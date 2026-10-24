## Reference notes

Use Python’s standard-library `json` and `pathlib`; the data is JSON, not a table. Inspect one product file and `employees.json` briefly to confirm their shapes, then process **every** `products/*.json` file. A document’s container is not evidence of which product it concerns.

```python
from pathlib import Path
import json

root = Path("/root/work/DATA")
for path in root.glob("products/*.json"):
    data = json.loads(path.read_text())
    for doc in data.get("documents", []):
        ...
    for meeting in data.get("meetings", []):
        ...
```

- Qualifying document: `doc["type"] == "Market Research Report"` **and** `"CoachForce" in doc["title"]` (exact product-name substring, case-sensitive). Do not substitute content mentions, aliases, or the container filename for the title rule.
- Choose the qualifying document with greatest `date`. ISO `YYYY-MM-DD` dates compare correctly as strings; neither “final” nor “latest” wording overrides the date.
- Authors: the chosen document’s `authors` entries only.
- Reviewers: the chosen document’s `reviewers` entries **plus** speakers of turns where `turn["kind"] == "feedback"` in meetings across **all** containers with `meeting["doc_id"] == chosen_doc["id"]`. Do not add participants merely for attending; do not require a particular quality or wording of a feedback turn.
- Remove every author from reviewers, deduplicate both lists, and sort each ascending. The output entries must be `eid_...` employee IDs. Consult `employees.json` if the inspected fields require ID resolution; do not assume its internal schema without looking.
- Write a JSON object to `/root/work/answer.json` with exactly `report_doc_id`, `author_ids`, and `reviewer_ids`. After running the script, read that file back and check its shape, ID formats, uniqueness, ordering, and author/reviewer disjointness.
