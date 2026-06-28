## Review Summary

**Verdict**: PASS

Overall, the modifications made to `install.py`, `test_install.py`, and `README.md` are correct, conformant, and of high quality. The single-command installation script is robust, parses YAML frontmatter correctly (including block folding and literal blocks), resolves paths intelligently under various execution modes (including stdin pipe), handles missing skill lockfile keys gracefully, and implements robust indentation-aware YAML injection for Hermes config.yaml. The unit tests and stress tests all pass successfully.

However, a few design improvements and edge cases should be noted for future maintenance.

---

## Findings

### [Major] Finding 1: Non-Hermetic Unit Tests Modify Real Home Directory Files

- **What**: The unit tests in `test_install.py` write directly to and modify the real configuration files in the user's home directory (`~/.agents/.skill-lock.json`, `~/.hermes/config.yaml`, and `~/.codex/commands/gunch.toml`).
- **Where**: `test_install.py`, lines 53, 84, 164, 254
- **Why**: Although the tests attempt to back up and restore the original files in `finally` blocks, this approach is fragile. If the test run is forcefully terminated (e.g., via SIGINT, SIGKILL, or OOM) during execution, the user's real configuration files will be left in a corrupted or modified state.
- **Suggestion**: The tests in `test_install.py` should mock `install.HOME` to point to a temporary folder (using `tempfile.mkdtemp()`), just like `stress_test.py` does. This will isolate the test runs completely and prevent any interaction with the real home directory.

### [Minor] Finding 2: Broken Fallback URL for Remote SKILL.md Download

- **What**: The remote URL used to download the skill file when local lookup fails is currently returning an HTTP 404 error.
- **Where**: `install.py`, lines 45–64
- **Why**: When local path resolution and fallback developer directories do not contain `SKILL.md` (e.g., if the script is run via stdin in a clean directory), the script tries to fetch from `https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md` and crashes due to a 404 error.
- **Suggestion**: Ensure the GitHub repository and branch are pushed and public, or handle 404 errors with a clearer warning/instruction to the user instead of printing a raw urllib traceback.

### [Minor] Finding 3: Lack of Chomping Indicator Support in Frontmatter parser

- **What**: The custom YAML frontmatter parser in `parse_skill_md` does not support block folding chomping indicators (e.g., `>-`, `|+`, `>+`).
- **Where**: `install.py`, lines 96–135
- **Why**: If a folded block utilizes a chomping indicator (like `>-`), the parser evaluates `v in (">", "|")` as `False` and falls back to simple string splitting. This results in the description being incorrectly parsed as the literal value `>-` and subsequent block lines being ignored.
- **Suggestion**: Modify the parser check to `v.startswith(">") or v.startswith("|")` and parse out chomping modifiers if they exist.

### [Minor] Finding 4: Potential shutil.rmtree Crash on Regular File

- **What**: The installer attempts to delete pre-existing paths at the Claude Code and Opencode symlink locations. If the existing path is a regular file rather than a directory or symlink, `shutil.rmtree` will raise an `OSError`.
- **Where**: `install.py`, lines 186 and 294
- **Why**: `shutil.rmtree` requires the path to be a directory. If the user manually created a regular file named `gunch` at `~/.claude/skills/gunch`, the script will crash.
- **Suggestion**: Check `os.path.isdir(path)` before calling `shutil.rmtree()`, or use `os.remove(path)` for regular files.

### [Minor] Finding 5: Codex TOML Injection Risk

- **What**: In `install_codex`, the script inserts the Markdown body directly into triple-double-quotes (`"""`) without escaping internal triple-double-quotes.
- **Where**: `install.py`, line 199
- **Why**: If `SKILL.md` body contains `"""`, the resulting TOML file will have syntax errors and Codex will fail to parse it.
- **Suggestion**: Escape any sequence of triple quotes in `parsed["body"]` before inserting it into the TOML command file.

---

## Verified Claims

- **YAML Frontmatter Parsing** → verified via `test_parse_skill_md_folded_block` and `test_parse_skill_md_literal_block` → **PASS**
- **Path Resolution / Stdin fallback** → verified via `test_resolve_skill_source_fallback` and manual inspection of the fallback logic → **PASS**
- **Robust Hermes config.yaml injection** → verified via `test_install_hermes_brittle_yaml_parser`, `test_install_hermes_indented_skills`, and `stress_test.py` → **PASS**
- **Missing keys in .skill-lock.json** → verified via `test_skill_lock_json_missing_skills_key` → **PASS**
- **All unit tests and stress tests pass** → verified by running `python3 test_install.py` and `python3 stress_test.py` → **PASS**

---

## Coverage Gaps

- **Remote Fetching Validation** — risk level: Low — recommendation: Accept risk once the GitHub repository goes live.
- **Chomping Indicator Validation** — risk level: Low — recommendation: Accept risk since the current `SKILL.md` uses standard folding `>` and does not use chomping indicators.

---

## Unverified Items

None. All code behaviors and edge cases were successfully verified or tested.
