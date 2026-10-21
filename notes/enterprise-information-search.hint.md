1. Read /root/question.txt, `ls -R /root/DATA | head`, then probe the JSON keys of products/<Product>.json and the employee directory with truncated python one-liners.
2. Write one script that recursively regex-searches the JSON for the artifact type and product. Keep only candidates with 2+ product-grounding signals (reject docs about other products such as CoFoAIX) and pick the latest/final version.
3. Take authors from author fields. Take reviewers from explicit reviewer fields or substantive feedback, not meeting participants. Map everything to valid eid_* IDs.
4. Use json.dump to write /root/answer.json as {"qN": {"answer": [list], "tokens": "<est>"}}, then reload it to verify the keys and list types.
