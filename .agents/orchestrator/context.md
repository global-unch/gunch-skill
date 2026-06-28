# Context Information

## Files in Scope
- `/Users/uchebnick/projects/gunch-skill/install.py` - Single-command installer script
- `/Users/uchebnick/projects/gunch-skill/README.md` - Documentation and installation table
- `/Users/uchebnick/projects/gunch-skill/SKILL.md` - Global skill definition
- `/Users/uchebnick/projects/gunch-skill/ORIGINAL_REQUEST.md` - Verification requirements

## Target Agent Environments & Output Paths
1. **Antigravity**: `~/.agents/skills/gunch/SKILL.md` (Markdown) and update `~/.agents/.skill-lock.json`
2. **Claude Code**: `~/.claude/skills/gunch/SKILL.md` (Markdown/Symlink)
3. **Codex**: `~/.codex/commands/gunch.toml` (TOML with description & prompt)
4. **Hermes Agent**: `~/.hermes/skills/gunch/SKILL.md` (Markdown) and update `~/.hermes/config.yaml` with external directory
5. **Opencode**: `~/.config/opencode/skills/gunch/SKILL.md` (Markdown/Symlink)
6. **OpenClaw**: `~/.openclaw/workspace/skills/gunch/SKILL.md` (Markdown with version and always in frontmatter)
