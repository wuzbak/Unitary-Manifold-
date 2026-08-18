# COLLABORATION.md — Gibberlink Session Protocol
## ThomasCory Walker-Pearson × GitHub Copilot

This follows the same meta-protocol as `../COLLABORATION.md`.
This file covers Gibberlink-specific session conventions.

---

## HOW SESSIONS START

```
Read Gibberlink/AGENTS.md.
Read Gibberlink/ROADMAP.md.
Read Gibberlink/sessions/SESSION_NNN.md (latest).
You are now oriented. What should we do next?
```

---

## SESSION NOTES CONVENTION

Session notes live at `Gibberlink/sessions/SESSION_NNN.md`.

Template:
```markdown
# Session NNN — YYYY-MM-DD
## Focus
One sentence: what this session was about.
## Work done
- [x] item
## Files created or modified
- new: path
- mod: path
## Experiments run
- description, inputs, outputs
## Decisions made
- decision and why
## Left incomplete / carry forward
- item
## Notes for next Copilot
- anything the next session should just know immediately
```

---

## WHAT IS ALWAYS TRUE HERE

- **No API keys in commits.** Ever. Use `.env` + `.gitignore`.
- **Experiment results are preserved.** Audio samples, decode logs — keep them.
- **The BV9900Pro is a valid test device.** When in doubt, test on hardware.
- **The manifold connection is real.** Gibberlink is a physical implementation
  of the information current `J^μ_inf`. Don't lose that thread.

---

*COLLABORATION.md — Gibberlink/ — v1.0 — 2026-04-18*
