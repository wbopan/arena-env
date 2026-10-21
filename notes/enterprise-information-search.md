**Goal.** Answer every question in /root/question.txt using only artifacts under /root/DATA. Write /root/answer.json as a Python-readable dict:
`{"q1": {"answer": [...], "tokens": "<number>"}, "q2": {...}, ...}`

Output rules:
- Use the exact keys from question.txt (q1, q2, ...).
- "answer" is always a list, even when there is one item (e.g. `["eid_abc123"]`).
- "tokens" is your estimate of tokens consumed for that question, as a string or int. A reasonable value is a rough count of characters read and written divided by 4. Never leave it empty.
- Write the file with `json.dump` so it is valid JSON. That means double quotes and no trailing commas, even though the example in task.md shows a trailing comma.

**Inspect cheaply (never cat whole files).**
- `cat /root/question.txt` (small). Note the target product and the entity type each question asks for (employee IDs, names, doc IDs, etc.).
- `ls -R /root/DATA | head -50`, then `du -sh /root/DATA/*`.
- Expect `/root/DATA/products/<Product>.json` (one file per product) and metadata such as employee or customer directories.
- Look at structure, not content:
  `python3 -c "import json;d=json.load(open('/root/DATA/products/X.json'));print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))"`
- Then print the keys of one element of each top-level list, for example slack, documents, meeting_transcripts, meeting_chats, pull_requests, urls. Print values truncated, e.g. `str(v)[:200]`.
- Locate mentions: `grep -o -i "market research report" -r /root/DATA | sort | uniq -c | head`, and `grep -l` for the product name.

**Search procedure (from the skill).**

1. **Parse each question.** Identify:
   - the target product, e.g. CoachForce;
   - the artifact type, e.g. "Market Research Report";
   - the roles wanted, e.g. authors and key reviewers.

2. **Build a wide candidate set.**
   - Start in products/<Product>.json.
   - Then grep the other product files for the product name.
   - Follow links such as `/archives/docs/<doc_id>`, meeting IDs and PR mentions.
   - Candidates are docs whose type/document_type/title contains the artifact type (case-insensitive), plus slack messages and meetings that reference them.

3. **Apply the hard product-grounding gate.** Accept a candidate only if at least 2 of these signals hold:
   - it sits inside the correct product file;
   - its title or content names the target product (or an alias proven in artifacts);
   - it was shared in a product-named channel or meeting series (e.g. planning-CoachForce, CoachForce_planning_*);
   - its doc id or link contains the product identifier;
   - a discussing meeting carries the product context.

   **Distractors are deliberate.** A doc of the same type that repeatedly names another product (e.g. CoFoAIX) is a DISTRACTOR, even if it sits in the same file. Reject it. "First hit wins" is the classic failure.

4. **Pick the version** using this precedence:
   - an explicit "latest" marker in the id, title or link;
   - an explicit "final" marker;
   - the most recent `date`;
   - otherwise the version most referenced in follow-ups.

5. **Find authors** in this order:
   - doc fields `author`, `authors`, `created_by`, `owner`;
   - PR `author` or `created_by`;
   - the slack user who posted "here is the report" with a link to that doc id.

   Convert names to `eid_*` through the employee directory.

6. **Find key reviewers. Participants are NOT reviewers.** Use this order:
   - explicit `reviewers`, `key_reviewers`, `approvers`, `requested_reviewers` fields (doc or PR);
   - attributed feedback entries in the doc, or transcript turns with concrete suggestions;
   - slack replies to the share message that give substantive feedback.

   Exclude pure "looks good/thanks" replies unless nothing else exists. Exclude the author unless the question says to include them.

7. **Validate the IDs.** Each must match `eid_...` and exist in the employee directory. De-duplicate while keeping order: authors first, then reviewers. If a question asks for "authors and key reviewers" as one answer, return the union list.

8. **Other question types.** For names, dates, URLs or PR ids, apply the same grounding: right product, right artifact, latest version, and evidence-based extraction. Never use fields named like ground_truth, answer or label as shortcuts.

**Plan within ~30 commands.**
1. Read question.txt and list DATA (2–3 commands).
2. Run schema probes on one product JSON and the directory files (3–4 commands).
3. Write one script `/root/solve.py` that:
   - loads the JSON files;
   - has a helper `find(obj, pattern)` that walks dicts and lists recursively and yields (path, short snippet) wherever a string matches a regex;
   - prints compact candidate lists per question: doc id, title, date, author, reviewers, and the product-name count in the content (target vs. other products).
4. Run the script and inspect its truncated output. Refine with targeted prints (slack replies to the share message, transcript turns), at most about 10 commands.
5. Hard-code the final answers into a small writer:
```python
import json
ans={"q1":{"answer":["eid_..."],"tokens":"12000"}, ...}
json.dump(ans,open('/root/answer.json','w'),indent=2)
```
6. Verify:
   `python3 -c "import json;d=json.load(open('/root/answer.json'));print({k:(type(v['answer']).__name__,len(v['answer']),v['tokens']) for k,v in d.items()})"`

   Check that every key from question.txt is present, every answer is a list, and every tokens value is set.
