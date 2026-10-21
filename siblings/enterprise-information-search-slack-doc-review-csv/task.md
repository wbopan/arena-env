# Review activity on shared planning documents

Inputs:

- /root/work/DATA/slack.json: a list of chat messages with these fields:
  - id, channel, ts
  - user_name: a display name, not an ID
  - text
  - parent_id: null for top-level messages; otherwise the id of the top-level message being replied to
- /root/work/DATA/employees.csv: columns employee_id, name, team. Display names are not globally unique, but they are unique within a team.

Conventions:

- A channel named planning-<Product> belongs to the team <Product>.
- Anyone posting in that channel (top-level or reply) is the employee with that display name in that team.
- A doc share is a top-level message in a planning-<Product> channel whose text contains a link of the form /archives/docs/<doc_id>. A doc_id is `doc_` followed by lowercase hex.
- Messages in all other channels are ignored. Replies are never doc shares.

For each doc share, produce one row:

- product: the <Product> part of the channel name
- doc_id: the linked document id
- sharer_id: employee ID of the person who posted the share
- n_replies: number of messages whose parent_id equals the share's id
- reviewer_ids: distinct employee IDs of reply authors whose reply has at least 6 whitespace-separated words, excluding the sharer. Sort them ascending and join with ";". Leave the field empty if there are none.

Write /root/work/doc_reviews.csv:

- comma-separated, with the header row `product,doc_id,sharer_id,n_replies,reviewer_ids`
- one row per doc share
- rows sorted by doc_id ascending
