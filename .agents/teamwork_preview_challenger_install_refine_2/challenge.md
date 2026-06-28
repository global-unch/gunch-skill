# Adversarial Review & Verification Report — 2026-06-28T09:50:50Z

## Challenge Summary

**Overall risk assessment**: MEDIUM

While the refined installation script successfully passes all existing tests and resolves local developer fallback paths when executed via stdin, a new vulnerability was discovered during adversarial testing regarding how the script checks for existing path configurations in the Hermes configuration file.

---

## Challenges

### [Medium] Challenge 1: Early Return in Hermes configuration check due to substring matching

- **Assumption challenged**: The installer assumes that if the target directory path (`~/.agents/skills`) exists anywhere as a substring in `config.yaml`, it must mean the Gunch skill has already been successfully configured under the `skills.external_dirs` key.
- **Attack scenario**: If the path is present inside a commented-out line, a text description block (e.g. `model.description`), or any other metadata field in `config.yaml`, the check `target_dir in config_str` will evaluate to `True`. Consequently, the script prints `"Hermes external_dirs already contains ~/.agents/skills"` and returns early, skipping the actual configuration of `skills.external_dirs`.
- **Blast radius**: The Gunch skill is not loaded by the Hermes Agent since the path is not configured under `skills.external_dirs`.
- **Mitigation**: Instead of performing a global substring search on the entire configuration file, verify specifically if the target path is declared as an element in the `external_dirs` list under the top-level `skills:` block.
- **Proof of Concept**:
  Running `install_hermes()` on a configuration where `skills.external_dirs` is empty (`[]`) but `model.description` contains the string `/Users/uchebnick/.agents/skills` results in an early exit, leaving the configuration unconfigured:
  ```yaml
  model:
    description: "I love /Users/uchebnick/.agents/skills directory"
  skills:
    external_dirs: []
  ```

### [Low] Challenge 2: Triple double-quote corruption in Codex TOML generation

- **Assumption challenged**: The installer assumes that the parsed skill markdown body does not contain triple double-quotes (`"""`).
- **Attack scenario**: If a developer adds triple double-quotes inside `SKILL.md` (e.g., inside code examples or markdown block quotes), the generated `~/.codex/commands/gunch.toml` will contain nested unescaped `"""` inside a triple-quoted multi-line string.
- **Blast radius**: The Codex command loader will fail to parse `gunch.toml` due to invalid TOML syntax.
- **Mitigation**: Escape any occurrence of `"""` or use a robust TOML serializer for python.

---

## Stress Test Results

- **Environment File/Symlink Creation** → Verify all 6 environments (Antigravity, Codex, Claude Code, Hermes Agent, Opencode, OpenClaw) are correctly configured after running `python3 install.py` → **PASS** (verified all directories, config files, and symlinks exist with correct metadata).
- **Stdin Execution Fallback** → Verify `cat install.py | python3` executed from a directory without `SKILL.md` falls back to developer paths → **PASS** (correctly resolved fallback absolute paths without fetching from remote URL or failing with 404).
- **Adversarial Config (skills: in description block string)** → Run `python3 stress_test.py` to check if `skills:` inside descriptions corrupts Hermes config → **PASS** (yaml structure is parsed and appended correctly).
- **Adversarial Config (path in description block string)** → Run `install_hermes()` when path is present in description → **FAIL** (incorrectly returns early and skips configuring Hermes config).

---

## Unchallenged Areas

- **GitHub Remote URL download** — Not fully challenged under network conditions because the primary focus of stdin testing was validating the local fallback logic on the developer machine in CODE_ONLY mode.
