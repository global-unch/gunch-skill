You are teamwork_preview_worker, working in directory: /Users/uchebnick/projects/gunch-skill/.agents/worker_install.
Your mission is to modify `install.py` to fix all identified bugs:
1. Fix path resolution and stdin/pipeline execution: When run via `curl ... | python3`, the local `SKILL.md` is not present and `__file__` might not be defined or be `"<stdin>"`. Correct this by handling NameError for `__file__`, checking for local `SKILL.md` (relative to the script and CWD), and fetching it from the raw GitHub repository URL (`https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md`) as a robust fallback.
2. Fix YAML Frontmatter Parsing for multiline folded blocks: The custom frontmatter parser in `parse_skill_md` splits lines by colons and does not support multiline values. Update it to properly handle folded/literal block indicators (`>` and `|`) and read subsequent indented lines. This ensures the description in Codex TOML command configuration `~/.codex/commands/gunch.toml` is correctly populated rather than just `">"`.
3. Fix potential KeyError in `.skill-lock.json` when the `"skills"` key is missing.
4. Fix brittle Hermes config YAML parser: When updating `~/.hermes/config.yaml`, ensure that blank lines or comments in the `skills:` section do not prematurely terminate key lookup and cause duplicate/corrupted `external_dirs` entries.

Additionally:
- Update `README.md` to ensure the manual installation path for Hermes Agent is consistent with the automated script setup or correctly documented.
- After implementing, execute the script and verify that the Gunch Skill is successfully installed to all 6 target environments (Antigravity, Codex, Claude Code, Hermes Agent, Opencode, Openclaw) and that the CLI checks succeed.

MANDATORY INTEGRITY WARNING:
> DO NOT CHEAT. All implementations must be genuine. DO NOT
> hardcode test results, create dummy/facade implementations, or
> circumvent the intended task. A Forensic Auditor will independently
> verify your work. Integrity violations WILL be detected and your
> work WILL be rejected.

Please write a detailed report of the changes and verification results to `changes.md` and `handoff.md` in your working directory, and notify me with your completion message via send_message.

## 2026-06-28T09:42:29Z
Implement installation fixes in install.py and README.md, as described in /Users/uchebnick/projects/gunch-skill/.agents/worker_install/original_prompt.md
