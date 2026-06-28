## 2026-06-28T09:54:14Z
You are teamwork_preview_worker (instance 3), working in directory: /Users/uchebnick/projects/gunch-skill/.agents/worker_install_refine_3.
Your task is to implement the following critical robustness and security fixes in `install.py` and `test_install.py`:

1. Flow-style YAML bug in `install_hermes()`:
   If `external_dirs` in `~/.hermes/config.yaml` is defined in flow style (e.g., contains square brackets like `external_dirs: []` or `external_dirs: [/some/path]`), modify the line to insert the Gunch skill path inside the brackets (appending with a comma if elements exist) instead of appending a block-style item on the next line.
   Example logic:
   ```python
   if "[" in line and "]" in line:
       parts = line.split("[", 1)
       prefix = parts[0] + "["
       suffix = parts[1].rstrip().rstrip("]")
       if suffix.strip():
           new_val = f"{prefix}{suffix}, {target_dir}]\n"
       else:
           new_val = f"{prefix}{target_dir}]\n"
       new_lines[-1] = new_val
   else:
       # Block style appending
       ind_str = ' ' * (skills_indent + 4)
       new_lines.append(f"{ind_str}- {target_dir}\n")
   ```

2. TOML triple-quote syntax break in `install_codex()`:
   To prevent unescaped triple-quotes in the markdown body from breaking the Codex command TOML syntax, replace any occurrences of `"""` in `parsed["body"]` with `\"\"\"` before inserting it into the triple-quoted string.
   Example:
   ```python
   body = parsed["body"].replace('"""', '\\"\\"\\"')
   ```

3. Missing Encoding in `open()`:
   Ensure all `open()` calls reading or writing text files (like `.skill-lock.json` and config files) explicitly specify `encoding="utf-8"`.

4. Unit Tests:
   Add tests in `test_install.py` to cover:
   - Updating a Hermes `config.yaml` that has empty flow-style `external_dirs: []`.
   - Updating a Hermes `config.yaml` that has pre-populated flow-style `external_dirs: [/some/path]`.
   - Codex TOML command generation with a skill body containing `"""` (verifying it is escaped).

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please run the test suite (`python3 test_install.py` and `python3 stress_test.py`) to verify your changes.
Write your changes report to `changes.md` and handoff report to `handoff.md` in your working directory, and report your status/verdict to me via send_message.
