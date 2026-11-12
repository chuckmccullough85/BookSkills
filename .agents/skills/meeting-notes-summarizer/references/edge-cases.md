# Edge cases (load on demand)

Load when data quality is poor or output confidence is low.

## Common edge cases

1. Missing owners for action items
   - Rule: set owner to `unknown`; do not guess.

2. Missing due dates
   - Rule: set due date to `unknown`; include in Open Questions.

3. Conflicting decisions in the same meeting
   - Rule: list both and flag conflict under Risks.

4. Ambiguous pronouns
   - Rule: preserve literal phrasing and flag ambiguity in Open Questions.

5. Very long meetings
   - Rule: cap Summary to `max_summary_bullets`; keep full detail in Action Items and Risks.

6. Duplicate action items
   - Rule: merge duplicates and preserve all referenced owners as a comma-separated list.

