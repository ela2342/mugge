# Tracking Data Integrity

## Topic: split-monoliths.py already lost a decision record (2026-10-24)

**Context:** Reviewing PR #41 (tracking re-sync), technical-writer and advocatus-diaboli independently.
**Learning:** `scripts/split-monoliths.py` keeps only the LAST `## D-NNN` section per ID. `decisions.md` has both "D-032: Web UI requires HTTPS for AudioWorklet secure context" (line 524) and a later "D-032 Amendment" section, so `decisions/D-032.md` contains only the amendment and the original decision exists only in the monolith. Per-item files are the source of truth since the split; never run the script (F-297). When an ID shows an empty or odd index row, check the monolith for a lost section.
**Source:** technical-writer + advocatus-diaboli, PR #41 review.
**Tags:** split-monoliths, F-297, decisions, D-032, tracking, data-loss, index

## Topic: Local protocol copy drifted from canonical (2026-10-24)

**Learning:** `.claude/team/protocol/state-format.md` differs from the canonical `~/mobile/gabriela-bogk/team-protocol/project-state/format.md` only in the story table (lines 91-93): the local copy dropped the Phase column, while `status.md` still uses Phase. Owner decision O-25 decides which is authoritative. Diff local protocol copies against canonical before relying on them.
**Source:** advocatus-diaboli, verified by technical-writer.
**Tags:** protocol, state-format, drift, O-25, Phase
