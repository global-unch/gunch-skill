## 2026-06-28T09:51:16Z

You are teamwork_preview_worker (instance 2), working in directory: /Users/uchebnick/projects/gunch-skill/.agents/worker_install_refine_2.
Your task is to refine the installer and test suite to address the review and challenge findings.

Please implement the following:
1. Symlink cleanup fix in `install.py`:
   In `install_claude()` and `install_opencode()`, check if the path exists. If it is a symlink or a regular file (not a directory), use `os.unlink` or `os.remove` to delete it. Only use `shutil.rmtree` if it is a directory and not a symlink. This prevents `NotADirectoryError` crashes.

2. Embedded SKILL.md fallback in `install.py`:
   In `resolve_skill_source()`, if the remote HTTP request fails (e.g. raises an exception due to network block or private repo 404), catch the exception, log a warning, and write the default contents of `SKILL.md` to the temp file path as an embedded fallback. This ensures offline and sandbox reliability.
   Use the exact content of `SKILL.md` for this fallback.

3. Hermetic unit tests in `test_install.py`:
   Add `setUp` and `tearDown` methods to `TestInstall` to mock/sandbox `install.HOME` in a temporary directory (like in `stress_test.py`).
   Update all unit tests to use `install.HOME` instead of hardcoding `os.path.expanduser("~")`. Ensure they never modify or read the user's real home directory files.
   Add a unit test verifying that `resolve_skill_source()` falls back to the embedded SKILL.md when remote fetch fails.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please run the test suite (`python3 test_install.py` and `python3 stress_test.py`) to verify your changes.
Write your changes report to `changes.md` and handoff report to `handoff.md` in your working directory, and report your status/verdict to me via send_message.
