# Quality Review & Adversarial Challenge Report

## Review Summary

**Verdict**: APPROVE

The refined changes implemented in `install.py` and `test_install.py` are robust, correct, and logically complete. They successfully address all target review dimensions:
1. **Symlink cleanup issues** are resolved by checking `os.path.islink`, `os.path.isdir` and using the corresponding unlinking/removal functions, preventing `NotADirectoryError` crashes.
2. **The HTTP download failure handler fallback** catches exceptions cleanly, logs a warning, and writes the correct embedded `SKILL.md` template content to the temp directory.
3. **The unit tests** are hermetic and sandbox `install.HOME` to a temporary directory in `setUp` and `tearDown`, and do not modify the runner's real home directory.

---

## Findings

### Minor Finding 1

- **What**: Potential write failures in fallback path if the temp directory is read-only or full.
- **Where**: `install.py`, lines 51-53, 114-115
- **Why**: If `/tmp` or the directory returned by `tempfile.gettempdir()` is not writable, writing the fallback embedded `SKILL.md` to `temp_path` will raise an `OSError`.
- **Suggestion**: This is an acceptable limitation of local install scripts. The outer try-except block in `resolve_skill_source` (lines 117-119) will catch this and exit gracefully with an error code and exit status of 1 rather than dumping a stack trace.

---

## Verified Claims

- **Symlink cleanup fix** → verified via inspecting `install.py` lines 237-243 and 347-353, and running `test_install.py::test_install_claude_cleanup_modes` and `test_install_opencode_cleanup_modes` → **PASS**
  - *Details*: Conflicting files, directories, symlinks, and broken symlinks are all handled and cleanly deleted before symlinking.
- **Embedded SKILL.md fallback** → verified via inspecting `install.py` lines 50-116, and running `test_install.py::test_resolve_skill_source_http_failure_fallback` and `stress_test.py` → **PASS**
  - *Details*: When the URL download raises an exception, the installer catches the exception, logs a warning, and successfully writes the embedded default content to `temp_path`.
- **Hermetic unit tests** → verified via inspecting `test_install.py` and `stress_test.py` `setUp`/`tearDown` methods, and checking that all test methods use `install.HOME` instead of `os.path.expanduser` or `~` → **PASS**
  - *Details*: The sandbox is created in `setUp`, assigned to `install.HOME`, and deleted in `tearDown`. No real home files are affected.
- **YAML Frontmatter Parsing** → verified via `test_parse_skill_md_folded_block` and `test_parse_skill_md_literal_block` → **PASS**
  - *Details*: Handles folded (`>`) and literal (`|`) blocks robustly, matching the YAML specification format.
- **Lockfile missing keys** → verified via `test_skill_lock_json_missing_skills_key` → **PASS**
  - *Details*: Safely handles missing `"skills"` keys inside `.skill-lock.json`.
- **Hermes YAML Config Injection** → verified via `test_install_hermes_brittle_yaml_parser`, `test_install_hermes_indented_skills`, and `test_hermes_skills_in_block_string` → **PASS**
  - *Details*: Ensures no duplication, and prevents injecting inside description blocks or lists nested under other keys.

---

## Coverage Gaps

- **None** — The current test suite has comprehensive test cases for all functionality implemented.

---

## Unverified Items

- **None** — All items identified in the scope of review have been verified.

---

# Adversarial Challenge Report

**Overall risk assessment**: LOW

## Challenges

### [Low] Challenge 1: Temp directory write permission failure

- **Assumption challenged**: The system's temp directory is always writable.
- **Attack scenario**: The installer runs on a system where `/tmp` (or equivalent returned by `tempfile.gettempdir()`) is read-only or full.
- **Blast radius**: The installation fails with an unhandled exception inside `resolve_skill_source()`'s fallback path (since the fallback also writes to `/tmp`), which is caught at the top level of `main()`, printing `ERROR: Failed to handle SKILL.md resolution: [Errno 30] Read-only file system` and exiting with 1.
- **Mitigation**: This is acceptable as a fallback failure mode.

### [Low] Challenge 2: Name collision in user's home folder

- **Assumption challenged**: Paths like `~/.agents`, `~/.claude`, etc., are either directories or do not exist.
- **Attack scenario**: An adversarial or corrupted user environment has a regular file named `~/.agents`.
- **Blast radius**: `os.makedirs` in `install_global_agents` raises `FileExistsError`, terminating the installation.
- **Mitigation**: The top-level try-except blocks this and exits cleanly.

---

## Stress Test Results

- **Hermes config with indented 'skills:' in block string** → Tested via `stress_test.py::TestInstallStress::test_hermes_skills_in_block_string` → **PASS**
  - *Result*: The parser ignores indented matches and appends the top-level `skills:` section correctly.
- **Hermes config without existing 'skills:' section** → Tested via `stress_test.py::TestInstallStress::test_hermes_no_skills_section` → **PASS**
  - *Result*: Appends the config section cleanly at the end.
