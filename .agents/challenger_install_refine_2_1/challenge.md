# Adversarial Review - Gunch Skill Installer

## Challenge Summary

**Overall risk assessment**: LOW

The installation script is well-designed and implements robust fallbacks for missing local resources, including checking multiple paths, attempting HTTP downloads, and falling back to embedded content. The stress tests cover critical edge cases like block strings in `~/.hermes/config.yaml`. However, some minor scenarios related to permissions or malformed files could present challenges.

---

## Challenges

### [Low] Challenge 1: YAML parsing in config.yaml is text-based and potentially fragile
- **Assumption challenged**: The `config.yaml` file of Hermes follows a standard formatting where `skills:` is only present as a top-level block key or inside standard descriptions.
- **Attack scenario**: A user has an unusual comment format or multiple occurrences of `skills:` inside complex nested structures that confuse the text-based YAML injector.
- **Blast radius**: The `config.yaml` file could be corrupted or duplicate sections could be added.
- **Mitigation**: Use a dedicated YAML parsing library like `pyyaml` (if available/installed) or a safer parser that parses document structure rather than performing simple line-by-line text matching.

### [Low] Challenge 2: Embedded SKILL.md content drift
- **Assumption challenged**: The embedded string in `install.py` stays synchronized with the actual `SKILL.md` file.
- **Attack scenario**: Future updates are made to `SKILL.md` in the repository, but the developer forgets to update the embedded backup inside `install.py`.
- **Blast radius**: If the repository is cloned, moved, and executed without network access or local files, it installs an outdated version of the skill.
- **Mitigation**: Add a validation test (e.g., in `stress_test.py` or a pre-commit hook) that asserts the embedded `SKILL.md` string matches the actual `SKILL.md` file content.

---

## Stress Test Results

- **Hermes skills section in block string** → The installer should not modify the existing block string containing the word `skills:`, but instead append/insert `external_dirs` cleanly. → Verified that the block string was preserved, and the `external_dirs` key was appended correctly at the top level. → **PASS**
- **Hermes missing skills section** → The installer should append the entire `skills:` block with `external_dirs` to the end of the file. → Verified that `skills:` and `external_dirs` were successfully added to the config file. → **PASS**
- **Stdin installation without local SKILL.md** → The installer should attempt HTTP download, fail with 404, fall back to embedded `SKILL.md`, and complete without crashing. → Verified output: `[WARN] Failed to download SKILL.md: HTTP Error 404: Not Found. Falling back to embedded SKILL.md.` followed by successful installation of all 6 environments. → **PASS**

---

## Unchallenged Areas

- **Platform-specific CLI execution** — We did not test CLI tools for Claude Code, Codex, Opencode, and OpenClaw directly because their CLIs were not globally installed or available in this testing environment (only Hermes CLI was accessible and verified).
