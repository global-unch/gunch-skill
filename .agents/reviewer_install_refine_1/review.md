# Review Report - install.py, test_install.py, and README.md

## Review Summary

**Verdict**: APPROVE

We are issuing an **APPROVE** verdict. The implementation is correct, complete, and robust. It covers all 6 target environments (Antigravity, Claude Code, Codex, Hermes Agent, Opencode, and OpenClaw) as requested, successfully parsing Markdown YAML frontmatter (with folded/literal blocks), maintaining `.skill-lock.json` integrity, and safely injecting external skill paths into Hermes' YAML configuration. The documentation in `README.md` is clear and contains a concise table and verification instructions.

We did identify a few minor robustness improvement areas (findings/challenges) that could be addressed in future maintenance but do not block the approval of the current state.

---

## Quality Review

### Findings

#### [Minor] Finding 1: Potential crash if target path is a regular file in symlink creation
- **What**: In `install_claude()` and `install_opencode()`, the script attempts to remove existing targets using `shutil.rmtree()` if they are not symlinks.
- **Where**: `install.py` lines 186 and 294.
- **Why**: If a regular file (not a symlink or directory) exists at the target path, `shutil.rmtree()` will raise a `NotADirectoryError` or `OSError`, crashing the installer.
- **Suggestion**: Use `os.path.isdir()` check or wrap with try-except to delete files using `os.remove()` and directories using `shutil.rmtree()`.

#### [Minor] Finding 2: Codex TOML multiline prompt escaping
- **What**: The script embeds the parsed Markdown body inside a TOML multiline basic string `"""..."""`.
- **Where**: `install.py` line 199.
- **Why**: If the body of the skill contains triple quotes `"""` (which is common in python code blocks or docstrings), the TOML structure will be malformed.
- **Suggestion**: Escape any triple quotes inside the body or use single-quote multiline strings if no single-quote blocks are present, or use a YAML/TOML library for escaping.

#### [Minor] Finding 3: Broad matching for YAML key prefix in Hermes config
- **What**: In `install_hermes()`, `is_skills` is computed as `line.strip().startswith("skills:")`.
- **Where**: `install.py` line 238 and line 273.
- **Why**: If the file contains a key like `skills_are_cool:` at the top-level, it will match the check.
- **Suggestion**: Check `line.strip() == "skills:"` or match with space/comment indicators, e.g., `re.match(r"^skills:\s*(?:#.*)?$", line.strip())`.

### Verified Claims

- **YAML Frontmatter parsing** → verified via `test_parse_skill_md_folded_block` and `test_parse_skill_md_literal_block` → **PASS**
- **Fallback path resolution and stdin execution compatibility** → verified via `test_resolve_skill_source_fallback` and `test_resolve_skill_source_developer_fallback` → **PASS**
- **Missing skills key in .skill-lock.json** → verified via `test_skill_lock_json_missing_skills_key` → **PASS**
- **Robust Hermes YAML injection** → verified via `test_install_hermes_brittle_yaml_parser` and `test_install_hermes_indented_skills` → **PASS**

### Coverage Gaps

- No coverage gaps identified. The test suite covers all major components of `install.py` including frontmatter parsing, file writing, symlinking logic (via system calls or mocks), and YAML injection.

---

## Adversarial Review (Critic)

### Challenge Summary

**Overall risk assessment**: LOW

The overall risk of the installation script is very low. It does not run with elevated root privileges (operates inside user's home directory `~`), uses standard libraries, and avoids destructive commands except on targets it created.

### Challenges

#### [Low] Challenge 1: Single-line YAML inline lists in Hermes config
- **Assumption challenged**: Assumes `external_dirs` in `config.yaml` is either multiline or empty `[]`.
- **Attack scenario**: If a user's pre-existing `config.yaml` has `external_dirs: [/some/path]`, the script will append `    - ~/.agents/skills` after it on a new line, creating invalid YAML.
- **Blast radius**: The user's Hermes configuration becomes malformed, preventing Hermes from launching.
- **Mitigation**: Detect if `external_dirs` matches an inline list format and convert it to multiline first, or warn the user.

#### [Low] Challenge 2: Network-blocked environments and remote fetch fallback
- **Assumption challenged**: Assumes that if local `SKILL.md` is missing, network access is available to download it.
- **Attack scenario**: Under air-gapped or network-restricted environment (like `CODE_ONLY` mode), if the user runs the script via piping stdin from outside the repo, the remote download fails with an unhandled network error, exiting the script.
- **Blast radius**: Clean failure, script terminates without side effects.
- **Mitigation**: Gracefully handle network exceptions and report that `SKILL.md` could not be located locally or downloaded.

### Stress Test Results

- **skills: key inside block string** → verified that it does not falsely match indented skills inside text descriptions → **PASS**
- **Missing skills section** → verified that the skills section is correctly appended if completely missing → **PASS**
