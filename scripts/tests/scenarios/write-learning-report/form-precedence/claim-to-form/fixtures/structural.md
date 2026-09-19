# Source notes — a document approval contract

An editor found that a draft was being published directly after an author marked it complete.
The team specified a small approval protocol to prevent that bypass. Its states are Draft,
Reviewed, Published. The initial state is Draft. The only permitted transitions are:
Draft --review--> Reviewed; Reviewed --publish--> Published; Reviewed --revise--> Draft.
All other state/event pairs are rejected and leave the state unchanged. Published is terminal.

The author requests review; the reviewer supplies the review event. Publication is a separate
event available only from Reviewed. The contract intentionally does not judge whether a review
was insightful; it enforces the recorded sequence only. A prior direct Draft/publish attempt was
the triggering example and violates the new protocol. Reviewed/publish is a permitted case, and
Reviewed/revise returns the document to Draft so another review is needed. These are stipulated
rules, not evidence that the process improves writing quality. No program was run in the source.
