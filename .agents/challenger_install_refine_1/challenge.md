# Challenge Report

## Challenge Summary

**Overall risk assessment**: HIGH

While the local installation script (`python3 install.py`) is highly robust and correctly sets up files and symlinks for all 6 target environments, the remote fallback mechanism (designed for pipeline installations like `cat install.py | python3` or `curl ... | python3`) is currently broken and fails with an HTTP 404 error.

## Challenges

### [High] Challenge 1: Broken Remote Fallback for Stdin Pipelining

- **Assumption challenged**: The script assumes that the public raw URL `https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md` is anonymously accessible.
- **Attack scenario**: When the installer is run via stdin (e.g. `cat install.py | python3`) in an environment without a local `SKILL.md` (or when fallback search paths don't match), `resolve_skill_source()` falls back to downloading the file from GitHub. Since the repository is currently private (or anonymous access is otherwise forbidden/unreachable), raw GitHub returns an `HTTP Error 404: Not Found` error, causing the entire installation process to crash with `sys.exit(1)`.
- **Blast radius**: This completely breaks the main promotional installation command shown in `README.md` (`curl -sSL ... | python3`) when executed outside of a pre-existing clone.
- **Mitigation**: 
  1. Make the repository `global-unch/gunch-skill` public on GitHub to allow anonymous HTTP GET requests.
  2. Implement an authenticated fallback in `install.py` (e.g., using `git archive` or `git show` commands using the local SSH/HTTPS keys if git is installed).

### [Low] State Pollution during Unit Testing

- **Assumption challenged**: Unit tests in `test_install.py` mock filesystem state but run on the real home directory pathing if not carefully cleaned up.
- **Attack scenario**: Running unit tests sequentially can fail (e.g. Case 2 of `test_install_hermes_brittle_yaml_parser` failing with empty file reads) if state files (`~/.hermes/config.yaml` or `~/.agents/.skill-lock.json`) are modified/truncated concurrently or are in a bad state initially.
- **Blast radius**: Spurious test failures.
- **Mitigation**: Use `unittest.mock` or a custom temporary environment (e.g., modifying `install.HOME` inside `setUp`/`tearDown` similar to `stress_test.py`) for all unit tests to avoid touching the actual `~/.hermes/config.yaml` or `~/.agents/.skill-lock.json`.

---

## Stress Test Results

- **Stress Test 1: test_hermes_skills_in_block_string**
  - **Scenario**: Verify `install_hermes` is not fooled by a nested `skills:` keyword inside a multiline description block in `config.yaml`.
  - **Expected behavior**: The nested `skills:` is ignored, and the new external skills directory is correctly added in a new top-level `skills:` section.
  - **Actual behavior**: Successfully ignored the nested `skills:` and appended the top-level section correctly.
  - **Result**: PASS

- **Stress Test 2: test_hermes_no_skills_section**
  - **Scenario**: Verify `install_hermes` appends the entire skills section if missing from `config.yaml`.
  - **Expected behavior**: Appends `skills:` and `external_dirs:` correctly at the end of the file.
  - **Actual behavior**: Appends correctly.
  - **Result**: PASS

---

## Unchallenged Areas

- **Symlink resolution on Windows** — Not tested, as our system environment is restricted to macOS. The behavior of `os.symlink` and shell/CLI integration commands on Windows target platforms remains untested.
