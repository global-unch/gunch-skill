# Gunch Skill Installation Analysis

## 1. Executive Summary
An analysis of the Gunch Skill installation project was conducted, reviewing the requirements in `ORIGINAL_REQUEST.md`, the documentation in `README.md`, the Python installer `install.py`, and the local system environment.

The installation script is functional when executed directly from the cloned repository, but it contains **two critical bugs** that will cause failure or incorrect configuration for end-users:
1. **Stdin / Pipeline Execution Failure**: The installer script fails with exit code `1` when run from outside the repository directory or when piped directly to python via stdin (e.g. `curl ... | python3`) because of brittle path resolution of `SKILL.md`.
2. **Naive YAML Frontmatter Parsing Bug**: The custom frontmatter parser in `install.py` splits properties line-by-line using colons. It fails to parse multiline block scalars (specifically `description: >` in `SKILL.md`), resulting in Codex command `gunch.toml` being generated with `description = ">"`.

---

## 2. Requirements Coverage Analysis (R1, R2, R3)

| Requirement | Description | Status | Verification & Gaps |
| :--- | :--- | :--- | :--- |
| **R1. Инструкции по установке** | Provide step-by-step instructions or command tables for all 6 agent IDEs. | **Fully Met** | Supported by the table in `README.md` listing the local installation paths and formats for all 6 platforms. |
| **R2. Скрипт установки в одну команду** | Create a simple script/tool allowing single-command installation across all platforms. | **Partially Met (Bugs Identified)** | `install.py` provides this, but fails when executed via the recommended `curl` pipeline from arbitrary directories. |
| **R3. Проверка через CLI** | Verify successful installation and availability locally through the CLIs of all environments. | **Fully Met (Pending Fixes)** | Detailed in `README.md` with CLI commands like `head`, `ls`, and `hermes -s gunch`. Verified functioning on the local system for existing CLIs. |

---

## 3. Detailed Code Analysis & Identified Bugs

### Bug A: Path Resolution & Pipeline Installation Failure
- **Location**: `install.py` lines 8-9 and 215-218.
- **Problem**: When `install.py` is executed via the `curl ... | python3` pipeline, `__file__` becomes `"<stdin>"`. Its directory name becomes empty, resolving the path of `SKILL.md` relative to the user's current directory. If run outside the `gunch-skill` repository (e.g. the home directory `~`), the script prints:
  `ERROR: SKILL.md not found at /Users/uchebnick/SKILL.md` and exits.
- **Code Reference**:
  ```python
  8: HOME = os.path.expanduser("~")
  9: SKILL_SOURCE = os.path.abspath(os.path.join(os.path.dirname(__file__), "SKILL.md"))
  ...
  216:     if not os.path.exists(SKILL_SOURCE):
  217:         print(f"ERROR: SKILL.md not found at {SKILL_SOURCE}")
  218:         sys.exit(1)
  ```

### Bug B: Naive Frontmatter YAML Parsing Bug (Codex)
- **Location**: `install.py` lines 20-41 (specifically line 34-38).
- **Problem**: The parser loops through lines of the frontmatter and splits by `:` on each line. It does not handle multiline folded (`>`) block scalars:
  ```python
  34:         for line in fm_content.split("\n"):
  35:             if ":" in line:
  36:                 k, v = line.split(":", 1)
  37:                 fm[k.strip().lower()] = v.strip().strip("'\"")
  ```
  In `SKILL.md`, the description is a multiline block scalar:
  ```yaml
  description: >
    Integration with the Gunch platform. Use when searching for solutions,
    conducting research on obscure topics, or when publishing new instructions/posts.
  ```
  Because the description text itself has no colon, it is ignored by the parser. Only `description: >` is caught, meaning the key `description` gets the value `">"`. As a result, the generated Codex TOML command (`~/.codex/commands/gunch.toml`) receives:
  `description = ">"`
- **Code Reference**:
  ```toml
  description = ">"
  prompt = """
  # GUNCH KNOWLEDGE BASE SKILL
  ...
  """
  ```

### Risk C: Brittle Hermes YAML Config Update
- **Location**: `install.py` lines 126-147.
- **Problem**: The script parses `~/.hermes/config.yaml` line-by-line using a state machine that relies heavily on strict line sequence and indentation. If there is an empty line or a comment in the middle of the `skills:` section before `external_dirs:` is reached, the state machine sets `in_skills = False`, fails to detect `external_dirs`, and appends a duplicate `external_dirs:` block.

---

## 4. Local Environment Analysis

The environment of the macOS machine was investigated, yielding the following status for the 6 agent environments:

1. **Antigravity**:
   - CLI Binary: Not found on PATH.
   - Installation Folder: `~/.agents/` exists.
   - Skill Path: `~/.agents/skills/gunch/SKILL.md` (Successfully created).
2. **Claude Code**:
   - CLI Binary: Present at `/opt/homebrew/bin/claude`.
   - Installation Folder: `~/.claude/` exists.
   - Skill Path: `~/.claude/skills/gunch` (Symlinked to global agents folder, verified working).
3. **Codex**:
   - CLI Binary: Present at `/opt/homebrew/bin/codex`.
   - Installation Folder: `~/.codex/` exists.
   - Skill Path: `~/.codex/commands/gunch.toml` (Created, but suffers from the `description = ">"` parsing bug).
4. **Hermes Agent**:
   - CLI Binary: Present at `/Users/uchebnick/.local/bin/hermes`.
   - Installation Folder: `~/.hermes/` exists.
   - Config file: `~/.hermes/config.yaml` exists.
   - Skill Path: Configured to load from `~/.agents/skills` (Verified `gunch` is active in `hermes skills list`).
5. **Opencode**:
   - CLI Binary: Present at `/Users/uchebnick/.opencode/bin/opencode`.
   - Installation Folder: `~/.config/opencode/` exists.
   - Skill Path: `~/.config/opencode/skills/gunch` (Symlinked to global agents folder, verified working).
6. **OpenClaw**:
   - CLI Binary: Not found on PATH.
   - Installation Folder: `~/.openclaw/` exists.
   - Skill Path: `~/.openclaw/workspace/skills/gunch/SKILL.md` (Successfully created with OpenClaw-specific frontmatter tags).

---

## 5. CLI Verification Commands

Here is the strategy to verify the skill loading locally across the 6 environments:

1. **Hermes Agent**:
   - Command: `hermes skills list`
   - Output: Checks if `gunch` is listed under local skills with status `enabled`.
   - Preload command test: `hermes -s gunch chat -q "hello" --yolo` (verifies startup loading).
2. **Codex**:
   - Command: `head -n 5 ~/.codex/commands/gunch.toml`
   - Output: Verify description and start of the prompt. Currently outputs `description = ">"`, which highlights the parser bug.
3. **Claude Code**:
   - Command: `ls -la ~/.claude/skills/gunch`
   - Output: Verifies symlink resolves to `/Users/uchebnick/.agents/skills/gunch`.
4. **Opencode**:
   - Command: `ls -la ~/.config/opencode/skills/gunch`
   - Output: Verifies symlink resolves to `/Users/uchebnick/.agents/skills/gunch`.
5. **OpenClaw / Antigravity**:
   - Command: `cat ~/.openclaw/workspace/skills/gunch/SKILL.md | grep -E 'always|version'`
   - Output: Verify the custom metadata is properly formatted.

---

## 6. Recommendations & Proposed Fixes

### Fix for Stdin / Pipeline Installation Bug
To support remote execution via `curl`, modify `install.py` to check if `SKILL.md` is missing locally or if `__file__` indicates stdin. If so, download the file from the remote GitHub raw repository using the built-in `urllib.request` module:

```python
import urllib.request

def get_skill_content():
    if os.path.exists(SKILL_SOURCE):
        with open(SKILL_SOURCE, "r", encoding="utf-8") as f:
            return f.read()
    else:
        log_info("Local SKILL.md not found. Fetching from remote repository...")
        url = "https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md"
        try:
            with urllib.request.urlopen(url) as response:
                return response.read().decode("utf-8")
        except Exception as e:
            print(f"ERROR: Failed to download SKILL.md from remote: {e}")
            sys.exit(1)
```

### Fix for Naive Frontmatter YAML Parser
Implement an indentation-aware parser in `parse_skill_md` to correctly parse multiline values and store them in the `parsed` dictionary:

```python
def parse_skill_md(content):
    if not (content.startswith("---\n") or content.startswith("---\r\n")):
        return {"name": "gunch", "description": "", "body": content}
        
    parts = re.split(r'^---\s*$', content, flags=re.MULTILINE)
    if len(parts) >= 3:
        fm_content = parts[1].strip()
        body = parts[2].strip()
        
        fm = {}
        current_key = None
        current_val = []
        
        for line in fm_content.split("\n"):
            if line.startswith(" ") and current_key:
                current_val.append(line.strip())
            else:
                if current_key:
                    fm[current_key] = " ".join(current_val).strip()
                    current_val = []
                if ":" in line:
                    k, v = line.split(":", 1)
                    current_key = k.strip().lower()
                    v_strip = v.strip().strip("'\"")
                    if v_strip in (">", "|"):
                        pass
                    else:
                        fm[current_key] = v_strip
                        current_key = None
        if current_key:
            fm[current_key] = " ".join(current_val).strip()
            
        return {
            "name": fm.get("name", "gunch"),
            "description": fm.get("description", ""),
            "body": body,
            "raw_fm": fm_content
        }
    return {"name": "gunch", "description": "", "body": content}
```
