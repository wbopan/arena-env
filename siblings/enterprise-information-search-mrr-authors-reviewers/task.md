# Latest Market Research Report: authors and key reviewers

The enterprise artifact dump is in /root/work/DATA:

- /root/work/DATA/products/<Product>.json: one file per product container. Each file holds `documents` (fields: id, type, title, date, authors, reviewers, content) and `meetings` (fields: id, doc_id, participants, transcript). Each transcript turn has speaker, kind and text.
- /root/work/DATA/employees.json: the employee directory.

Question: who are the authors and key reviewers of the latest Market Research Report for the product **CoachForce**?

Conventions:

- A document is about a product only if its `title` contains that product's exact name. The container a document is filed in does not matter. Containers can hold documents about other products, and a product's documents can sit in another product's container.
- Only documents whose `type` is exactly "Market Research Report" qualify. The latest one is the qualifying document with the greatest `date` (ISO YYYY-MM-DD).
- Authors are the entries of that document's `authors` field.
- Key reviewers are the union of two groups:
  - (a) the entries of the document's `reviewers` field;
  - (b) every speaker of a transcript turn with kind "feedback" in any meeting, in any container, whose doc_id equals that document's id.
- Meeting participants who gave no feedback turn are not reviewers. An author is never a reviewer.

Write /root/work/answer.json as a JSON object:

{"report_doc_id": "<doc id>", "author_ids": [...], "reviewer_ids": [...]}

Both lists contain employee IDs (eid_...). They must have no duplicates and be sorted in ascending order.
