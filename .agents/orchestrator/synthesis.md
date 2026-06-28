# Exploration Synthesis: Gunch Skill Installation Analysis

## Consensus
All three explorers agree on the following:
1. **Requirements Coverage**:
   - **R1 (Instructions)**: Covered in `README.md`, but there is a small discrepancy with Hermes installation path.
   - **R2 (One-command script)**: Implemented in `install.py` but fails under piped execution via `stdin` (curl to python pipeline) due to path resolution of `SKILL.md`.
   - **R3 (CLI Verification)**: Successfully testable. CLI binaries for `hermes`, `codex`, `claude`, and `opencode` are available locally. `antigravity` and `openclaw` are folder-based and require file check verifications.
2. **YAML parsing bug (Critical)**:
   - `parse_skill_md` splits YAML frontmatter line-by-line using `:` and fails to handle multiline block scalars (specifically `description: >` in `SKILL.md`). This results in generating a Codex TOML command configuration (`~/.codex/commands/gunch.toml`) with `description = ">"`.

## Resolved Conflicts
- **Stdin/Pipeline Fetching**: Explorer 1 proposed fetching `SKILL.md` from raw GitHub URL when local `SKILL.md` is not present (like in a piped installation). Explorer 3 provided a path-resolution workaround. Both are valuable: we should check local relative and absolute paths first, and if missing, fetch from GitHub raw repository as a robust fallback.
- **Robustness in .skill-lock.json and Hermes Config**: Explorer 2 identified that `.skill-lock.json` might throw `KeyError` if `"skills"` key is missing, and that blank lines/comments in `~/.hermes/config.yaml` can break the lightweight YAML parser. We will include robust checks for both.

## Dissenting Views
None.

## Gaps
None.
