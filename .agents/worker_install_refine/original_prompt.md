You are teamwork_preview_worker, working in directory: /Users/uchebnick/projects/gunch-skill/.agents/worker_install_refine.
Your mission is to apply crucial refinement fixes to `install.py` based on Challenger and Reviewer feedback:

1. **Top-Level 'skills:' Key Matching**:
   In `install_hermes()`, do not match indented lines containing `skills:`. Ensure `skills:` matching is restricted to top-level keys (i.e., lines with no leading spaces/tabs: `not line.startswith(" ") and not line.startswith("\t") and line.strip().startswith("skills:")`). This prevents corruption of `~/.hermes/config.yaml` when a multiline block string (like a description) contains the word `skills:`.

2. **Local Testing/Developer Fallback for Stdin/Pipeline**:
   In `resolve_skill_source()`, if the remote URL fetch fails or before it, add a developer/testing fallback check for absolute local paths:
   - `/Users/uchebnick/projects/gunch-skill/SKILL.md`
   - `/Users/uchebnick/projects/gunch/skills/gunch/SKILL.md`
   This ensures that running `cat install.py | python3` from `/tmp` or arbitrary directories in the offline/local test environment succeeds rather than crashing with a 404 Error.

3. **TOML Escaping and Maxsplit Rules**:
   - In `install_codex()`, escape double quotes in the description string (e.g. `desc.replace('"', '\\"')`) to avoid syntax errors in the generated TOML.
   - In `parse_skill_md()`, use `maxsplit=2` in `re.split(r'^---\s*$', ...)` to ensure that any horizontal rule (`---`) inside the Markdown body does not split the content incorrectly.

4. **Tests Validation**:
   - Run the unit tests (`python3 test_install.py`) and ensure they all pass.
   - Add new tests in `test_install.py` or update existing ones (such as `TestInstallStress`) to verify that the config is not corrupted by indented `skills:` and that developer fallback paths resolve correctly.

MANDATORY INTEGRITY WARNING:
> DO NOT CHEAT. All implementations must be genuine. DO NOT
> hardcode test results, create dummy/facade implementations, or
> circumvent the intended task. A Forensic Auditor will independently
> verify your work. Integrity violations WILL be detected and your
> work WILL be rejected.

Please write a detailed report of the changes and verification results to `changes.md` and `handoff.md` in your working directory, and notify me with your completion message via send_message.

## 2026-06-28T09:46:19Z
Implement refined installer fixes in install.py and test_install.py, as described in /Users/uchebnick/projects/gunch-skill/.agents/worker_install_refine/original_prompt.md
