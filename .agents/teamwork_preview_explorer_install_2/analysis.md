# Analysis of Gunch Skill Installation Project

This report provides a detailed analysis of the requirements, current code implementation, documentation, and the local system environment for the Gunch Skill installation project.

---

## 1. Summary of Findings

1. **Successful Execution**: The single-command installer (`python3 install.py`) runs successfully and creates all expected directories, configuration files, and symlinks.
2. **Major Bug in YAML Parsing (Frontmatter)**: A parser bug in `install.py` causes folded YAML multiline string values (specifically the `description: >` block in `SKILL.md`) to be parsed incorrectly as just `">"`. As a result, the generated Codex configuration `~/.codex/commands/gunch.toml` has `description = ">"`, breaking command description display in Codex TUI/CLI.
3. **Robustness Gaps in `install.py`**:
   - **`.skill-lock.json` Handling**: Overwriting `.skill-lock.json` will raise a `KeyError` if the loaded JSON file does not contain a `"skills"` key.
   - **Hermes YAML parser robustness**: If a blank line is present between `skills:` and `external_dirs:` in `~/.hermes/config.yaml`, the lightweight parser gets confused and writes duplicate `external_dirs` blocks, corrupting the YAML structure.
4. **Documentation Discrepancy**: The README lists the local path for Hermes Agent as `~/.hermes/skills/gunch/SKILL.md`, but the installer registers the global `~/.agents/skills/gunch/SKILL.md` under `external_dirs` instead.
5. **Local Environment Presence**:
   - **Installed CLIs**: `codex`, `claude`, `hermes`, and `opencode` are present and functional in the local environment.
   - **Missing CLIs**: `antigravity` and `openclaw` are not present on the system path as standalone executables. However, their configurations and directories (like `~/.agents` and `~/.openclaw`) are successfully targeted and populated.

---

## 2. Requirement Analysis

### R1. Installation Instructions
- **Requirement**: Provide clear step-by-step instructions or command table for installing Gunch Skill into the 6 supported agent IDEs/CLIs.
- **Status**: **Fully Met (with minor doc discrepancy)**.
- **Details**: `README.md` provides a summary table mapping each environment to its local path, file format, and installation notes. However, the path listed for `Hermes Agent` (`~/.hermes/skills/gunch/SKILL.md`) is technically not where the file is installed; instead, it uses the global path `~/.agents/skills/gunch/SKILL.md` via `external_dirs` in `config.yaml`.

### R2. One-command installation script
- **Requirement**: Create a simple script/tool that allows installing Gunch Skill into all supported environments in a single command.
- **Status**: **Fully Met**.
- **Details**: `install.py` automates the installation process for all 6 target environments with single-command execution.

### R3. Verification via CLI
- **Requirement**: Verify successful installation and local availability of the skill via the CLI of all listed environments.
- **Status**: **Partially Met / Testable**.
- **Details**:
  - We verified `hermes` CLI dynamically loads the skill using:
    `hermes -s gunch chat -q "Проверь загрузку скилла gunch" --yolo`
    which successfully outputted that the skill is loaded and functional.
  - We verified `codex` command TOML is created under `~/.codex/commands/gunch.toml`, but because of the parser bug, description is incorrect.
  - For `claude` and `opencode`, they load symlinks, which were successfully verified.
  - For `antigravity` and `openclaw`, the CLIs are not installed globally, so verification consists of verifying file existence under `~/.agents/skills/gunch/SKILL.md` and `~/.openclaw/workspace/skills/gunch/SKILL.md`.

---

## 3. Code Investigation (Bugs & Gaps)

### Bug 1: Naive Frontmatter YAML Parsing of Multiline Blocks
In `install.py` lines 34-38:
```python
        fm = {}
        for line in fm_content.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip().lower()] = v.strip().strip("'\"")
```
When parsing the frontmatter in `SKILL.md`:
```yaml
description: >
  Integration with the Gunch platform. Use when searching for solutions,
  conducting research on obscure topics, or when publishing new instructions/posts.
```
The line `description: >` contains `:` and is split into `k="description"` and `v=">"`. Subsequent lines have no `:` and are ignored.
As a result, `parsed["description"]` is evaluated as `">"`, and the resulting Codex command TOML contains:
```toml
description = ">"
```
Instead of the folded multi-line description.

#### Proposed Fix:
Replace the parsing loop in `parse_skill_md` with a loop that recognizes block indicators (`>` and `|`) and parses subsequent indented lines:
```python
        fm = {}
        lines = fm_content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip()
                
                if v in (">", "|"):
                    multiline_val = []
                    i += 1
                    while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t") or not lines[i].strip()):
                        multiline_val.append(lines[i])
                        i += 1
                    
                    non_empty_indents = [len(l) - len(l.lstrip()) for l in multiline_val if l.strip()]
                    min_indent = min(non_empty_indents) if non_empty_indents else 0
                    cleaned_lines = [l[min_indent:] if len(l) >= min_indent else l.lstrip() for l in multiline_val]
                    
                    if v == ">":
                        joined = " ".join([l.strip() for l in cleaned_lines])
                        fm[k] = re.sub(r'\s+', ' ', joined).strip()
                    else:
                        fm[k] = "\n".join(cleaned_lines).rstrip()
                    continue
                else:
                    fm[k] = v.strip("'\"")
            i += 1
```

### Bug 2: Potential `KeyError` in `.skill-lock.json` Update
In `install.py` lines 51-67:
```python
    lock_path = os.path.join(HOME, ".agents", ".skill-lock.json")
    lock_data = {"version": 3, "skills": {}, "dismissed": {"findSkillsPrompt": True}}
    if os.path.exists(lock_path):
        try:
            with open(lock_path, "r") as f:
                lock_data = json.load(f)
        except Exception:
            pass

    lock_data["skills"]["gunch"] = { ... }
```
If `.skill-lock.json` exists but is structured without a `"skills"` key, `lock_data["skills"]` will throw a `KeyError`.

#### Proposed Fix:
Ensure the `"skills"` key exists before writing:
```python
    if not isinstance(lock_data, dict):
        lock_data = {}
    if "skills" not in lock_data:
        lock_data["skills"] = {}
```

### Bug 3: Fragile YAML Parser for Hermes Config
If the user's `~/.hermes/config.yaml` has blank lines inside the `skills:` section before `external_dirs:` (e.g. standard spacing/formatting), the state variable `in_skills` will transition to `False` on the blank line, preventing it from detecting `external_dirs:` and creating duplicate blocks.

#### Proposed Fix:
Instead of `else: in_skills = False` on non-indented lines, only transition `in_skills` to `False` if the line contains a non-indented key other than comments/empty lines (e.g., matching `^[a-zA-Z_-]+:` where indentation is zero).

---

## 4. Local CLI Verification Methods

Here is how each CLI environment can be verified on the system:

1. **Antigravity**:
   Verify file exists at `~/.agents/skills/gunch/SKILL.md`. (CLI is implicit in agent run).
   ```bash
   ls -la ~/.agents/skills/gunch/SKILL.md
   ```
2. **Claude Code**:
   Verify symlink exists at `~/.claude/skills/gunch/SKILL.md`.
   ```bash
   ls -la ~/.claude/skills/gunch/SKILL.md
   ```
3. **Codex**:
   Verify dynamically loaded custom command TOML exists and has correct syntax:
   ```bash
   cat ~/.codex/commands/gunch.toml
   ```
4. **Hermes Agent**:
   Verify the CLI successfully imports and registers the skill:
   ```bash
   hermes -s gunch chat -q "Проверь загрузку скилла gunch" --yolo
   ```
5. **Opencode**:
   Verify symlink exists:
   ```bash
   ls -la ~/.config/opencode/skills/gunch/SKILL.md
   ```
6. **OpenClaw**:
   Verify custom skill exists with version metadata in frontmatter:
   ```bash
   cat ~/.openclaw/workspace/skills/gunch/SKILL.md
   ```
