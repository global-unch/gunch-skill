# Quality & Adversarial Review Report — Gunch Skill Installation and Verification

## Review Summary

**Verdict**: APPROVE

We reviewed the latest changes in `install.py`, `test_install.py`, and `README.md`. The implementation is highly robust, correct, and conforms to all specified requirements. All 17 tests (15 unit tests in `test_install.py` and 2 stress tests in `stress_test.py`) run and pass successfully.

---

## Findings

No critical or major findings were discovered during this review. Below is a minor suggestion:

### Minor Finding 1: Potential raw fallback URL mismatch if repository changes
- **What**: The script falls back to a hardcoded URL (`https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md`) if the local `SKILL.md` is missing.
- **Where**: `install.py`, line 45.
- **Why**: If the repository is renamed or moved to another branch, this hardcoded URL might fail.
- **Suggestion**: The script already includes a robust embedded fallback for this exact case (lines 62-113), so the risk is extremely low. If this becomes a common deployment template, parameterizing the repository URL or branch could be considered.

---

## Verified Claims

- **Flow-style YAML Handling** → Verified via tracing `install_hermes()` in `install.py` (lines 309-317) and executing `test_install_hermes_flow_style_empty` and `test_install_hermes_flow_style_pre_populated` in `test_install.py` → **PASS**
  - Traced that `external_dirs: []` is correctly transformed to `external_dirs: [<target_dir>]`.
  - Traced that `external_dirs: [/some/path]` is correctly transformed to `external_dirs: [/some/path, <target_dir>]`.
- **TOML Escaping for Codex** → Verified via tracing `install_codex()` in `install.py` (lines 255-257) and executing `test_install_codex_triple_quote_escaping` in `test_install.py` → **PASS**
  - Traced that triple-quotes `"""` in the skill body are escaped to `\"\"\"` to avoid premature termination of TOML multi-line strings.
- **UTF-8 Encoding for open() calls** → Verified by inspecting all `open()` calls in `install.py`, `test_install.py`, and `stress_test.py` → **PASS**
  - All text-mode `open()` calls specify `encoding="utf-8"`. Only binary mode (`"wb"`) opens omit it, which is correct and necessary.
- **Unit and Stress Test Execution** → Verified by running `python3 test_install.py` and `python3 stress_test.py` → **PASS**
  - 15 unit tests inside `test_install.py` and 2 stress tests inside `stress_test.py` all completed successfully with status `OK`.

---

## Coverage Gaps

- **Real Hermes Config load validation** — risk level: Low — recommendation: accept risk. The unit and stress tests simulate Hermes `config.yaml` using mocking and temporary files, which is standard and safe.

---

## Unverified Items

- **Real agent binary loading and execution** — reason not verified: Agent binaries (e.g. Claude Code, Opencode CLI, OpenClaw runner) are not pre-installed or active in the sandbox environment. However, file layouts and symlinks conform exactly to the CLI/IDE requirements.

---

## Adversarial Challenge Report

### Challenge Summary

**Overall risk assessment**: LOW

The installation script demonstrates high resilience against common configuration anomalies, structural variations, and encoding differences.

### Challenges

#### [Low] Challenge 1: Line-by-line YAML parsing in Hermes config.yaml
- **Assumption challenged**: Assumes `skills:` block and `external_dirs:` are cleanly indented and structured without complex comments or nested multiline strings that could confuse a regex/line-based parser.
- **Attack scenario**: If a user has a complex YAML description block that contains the string `skills:` or `external_dirs:` in a multiline block text style (which is syntactically valid YAML but semantically just text), the script might incorrectly target and modify it.
- **Blast radius**: Potentially corrupted/modified description blocks in `~/.hermes/config.yaml`.
- **Mitigation**: The stress test `test_hermes_skills_in_block_string` already validates that if `skills:` is indented inside a block string, it is ignored and a new top-level `skills:` block is correctly appended to the config. Furthermore, the parser restricts top-level matching to lines where `skills:` has no indentation. This reduces the blast radius to zero for most realistic scenarios.

#### [Low] Challenge 2: Codex command description length and newlines
- **Assumption challenged**: Assumes the `description` field in frontmatter contains simple single-line text.
- **Attack scenario**: A frontmatter description that has raw newlines could cause malformed TOML formatting in `gunch.toml`.
- **Blast radius**: Syntax error in `gunch.toml` leading to Codex failing to parse the command.
- **Mitigation**: The code replaces all newlines in the description with spaces (`desc = parsed["description"].replace("\n", " ").strip().replace('"', '\\"')`). This ensures the description field remains a single line and matches TOML specification.

---

### Stress Test Results

- **Empty Flow-style lists for Hermes** → `skills: \n  external_dirs: []` → transformed to `  external_dirs: [/Users/uchebnick/.agents/skills]` → **PASS**
- **Pre-populated Flow-style lists for Hermes** → `skills: \n  external_dirs: [/some/path]` → transformed to `  external_dirs: [/some/path, /Users/uchebnick/.agents/skills]` → **PASS**
- **Triple Quotes in Codex body** → `prompt = """\n... """ ..."""` → escaped to `\"\"\"` inside the multi-line string block → **PASS**
- **Adversarial nested skills section in Hermes config** → `description: |\n  skills:\n  - math` → ignores inner `skills:` and appends top-level `skills:` block at end → **PASS**

---

### Unchallenged Areas

- **System-level path permissions / write restrictions** — reason not challenged: The script operates in the user's home directory (`~`), where write permissions are normally present. Standard system-level file locks or read-only home directories are out of scope for general installations.
