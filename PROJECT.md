# Project: Gunch Skill Installation and Verification

## Architecture
This project consists of an installation script (`install.py`) that deploys Gunch Skill (`SKILL.md`) to 6 different agent IDEs/CLIs: Antigravity, Claude Code, Codex, Hermes Agent, Opencode, and OpenClaw.
- The installation parses frontmatter from `SKILL.md` and copies/symlinks it, or converts it into specialized formats (like TOML for Codex) under the user's home directory.
- The script checks and modifies configurations (like `~/.agents/.skill-lock.json` and `~/.hermes/config.yaml`) if necessary.
- Verification commands check if the skills are loaded correctly by testing using CLI or verifying the existence and contents of the target paths.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Exploration | Analyze current installation script and requirements | none | DONE |
| 2 | Implementation | Refine installation script to correctly handle all 6 environments | M1 | DONE |
| 3 | Review & Challenge | Verify correctness, robustness, and layout compliance | M2 | IN_PROGRESS (24e1d010-da72-4f34-86d5-4b2aa1644403, 6d439f61-190c-41d9-a983-3e1a1f4fa14d, baba9ab2-2204-41c3-8543-efa94dffdcbe, d9e1e880-f35e-4003-b9b5-67c5dbdc86b6) |
| 4 | Integrity Audit | Verify integrity and authenticity of implementation via Forensic Auditor | M3 | IN_PROGRESS (e3b06917-ef8f-4f65-a369-4a97a815f121) |

## Code Layout
- `/Users/uchebnick/projects/gunch-skill/install.py` - Single-command installer script
- `/Users/uchebnick/projects/gunch-skill/README.md` - Documentation and command table
- `/Users/uchebnick/projects/gunch-skill/SKILL.md` - Global skill source
