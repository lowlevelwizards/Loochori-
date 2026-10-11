# Today Shortlist contract

v0.18.1 adds an explicit human-intent layer above Adaptive Today.

- Choosing **Today** adds an unresolved loop, routine/checklist item, deferred checklist item, or today's time block to the shortlist.
- Hard commitments still outrank explicit intent; explicit intent outranks ordinary optional suggestions.
- **Later** keeps the item on the shortlist but removes it from adaptive ranking for 90 minutes.
- **Remove** removes only the Today choice, not the underlying item.
- Completing the underlying item resolves its shortlist entry automatically.
- Unfinished non-time-block choices from yesterday are offered as carryover; they are never silently made overdue.
- Time blocks do not carry across dates.
- Today intent is local managed data and participates in Loochori backup/restore.

The browser release gate exercises persistence, Later, carryover, and adaptive-ranking integration.