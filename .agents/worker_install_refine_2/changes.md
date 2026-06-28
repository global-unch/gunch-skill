# Changes Report — 2026-06-28T09:52:30Z

## Summary of Changes

### 1. Symlink Cleanup Fix in `install.py`
- In `install_claude()` and `install_opencode()`, added checks using `os.path.islink(path)`, `os.path.isdir(path)` and fallback `os.remove(path)`.
- If the path is a symlink, `os.unlink` is used.
- If it is a directory (and not a symlink), `shutil.rmtree` is used.
- If it is a regular file (not a symlink or directory), `os.remove` is used.
- This prevents `NotADirectoryError` when cleaning up a file in place of a symlink directory.

### 2. Embedded SKILL.md Fallback in `install.py`
- In `resolve_skill_source()`, wrapped the remote urlopen block in a nested `try-except` structure.
- Upon any connection failure or HTTP exception, the installer catches the exception, logs a warning using `log_warn()`, and dumps the embedded copy of `SKILL.md` (the exact content of `SKILL.md` in the repo) to the temporary file path.
- This ensures sandboxed or offline environments can resolve the skill source without network access.

### 3. Hermetic Unit Tests in `test_install.py`
- Added `setUp` and `tearDown` methods to sandboxed `install.HOME` in a temporary directory unique to each test run.
- Refactored all unit tests in `test_install.py` to use `install.HOME` instead of hardcoding `os.path.expanduser("~")`.
- Removed dangerous manual backup and restore sequences inside the test cases, which could leave user files corrupted if the test suite crashed midway.
- Added test case `test_resolve_skill_source_http_failure_fallback` verifying that `resolve_skill_source()` falls back to the embedded SKILL.md and logs a warning on remote connection failure.
- Added `test_install_claude_cleanup_modes` and `test_install_opencode_cleanup_modes` to fully verify the symlink, file, and directory deletion logic under different cleanup scenarios.
