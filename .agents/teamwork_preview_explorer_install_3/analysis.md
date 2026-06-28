# Analysis: Gunch Skill Installation and Verification

This document contains the analysis of the Gunch Skill installation requirements, the current installer implementation, and the local system environment.

---

## 1. Requirements vs. Current Implementation

The project requirements (from `ORIGINAL_REQUEST.md`) demand the deployment of Gunch Skill into 6 agent environments: Antigravity, Codex, Claude Code, Hermes Agent, Opencode, and OpenClaw.

### Requirement Status Mapping

| Req | Requirement Description | Implementation Status | Findings / Gaps |
| :--- | :--- | :--- | :--- |
| **R1** | Step-by-step instructions or table of installation commands for all 6 IDE/CLI environments. | **Fully Met (with minor doc gaps)** | Covered in `README.md`. A summary table outlines manual install paths and formats for all environments. However, the path documented for Hermes diverges from how the automated installer configures it (see details below). |
| **R2** | Single-command installation script to deploy to all supported environments. | **Partially Met (bug found)** | Implemented in `install.py`. The script runs in a single command, but has a parser bug that breaks Codex deployment. |
| **R3** | Verification of successful installation and availability locally via CLI. | **Partially Met (environment constraints)** | The verification instructions in `README.md` are primarily file-existence checks (using `ls` or `head`), except for Hermes which uses a real CLI check. However, the local system only has some of these CLIs available (see environment details below). |

---

## 2. Discovered Bugs and Gaps

### Bug 1: YAML Frontmatter Parser Bug (Affects Codex)
* **Location**: `install.py` lines 20–41 (`parse_skill_md` function).
* **Observation**: The parser is highly naive and splits each line of the YAML frontmatter section purely by the `:` character.
* **Impact**: In `SKILL.md`, the description is defined as a folded block scalar:
  ```yaml
  description: >
    Integration with the Gunch platform. Use when searching for solutions,
    conducting research on obscure topics, or when publishing new instructions/posts.
  ```
  The parser parses `description: >` as key `description` with value `>`. The next lines (which are indented and lack colons) are ignored.
  As a result, the generated Codex TOML file (`~/.codex/commands/gunch.toml`) has:
  ```toml
  description = ">"
  ```
  The actual description of the skill is completely lost in Codex.
* **Proposed Solution**: Update `parse_skill_md` to correctly handle indented continuation lines for folded/literal multiline blocks (e.g. starting with `>` or `|`). A patch is provided in `install.py.patch`.

### Bug/Gap 2: Hermes Installation Discrepancy
* **Observation**: The `README.md` states:
  * Local path: `~/.hermes/skills/gunch/SKILL.md`
  * Action: copy/symlink and add to `external_dirs` in `config.yaml`.
* **Current Code**: `install.py`'s `install_hermes()` *only* updates `config.yaml` to point to `~/.agents/skills` under `external_dirs`. It does NOT copy/symlink the skill into `~/.hermes/skills/gunch/SKILL.md`.
* **Status**: Functional but inconsistent with the manual installation table in the documentation.

---

## 3. Environment CLI Analysis

We examined the presence of CLI tools on the local macOS system. Here are the findings:

1. **Codex**:
   * **Path**: `/opt/homebrew/bin/codex`
   * **Verification Command**: `codex debug prompt-input`
   * **Result**: Successfully displays the list of loaded skills as JSON. We verified that `gunch` is registered under `$HOME/.agents/skills/gunch/SKILL.md` since Codex monitors the global agent skills directory.
2. **Claude Code**:
   * **Path**: `/opt/homebrew/bin/claude`
   * **Verification Command**: `claude -p "any prompt"`
   * **Result**: Requires active developer/API credentials to evaluate prompts, meaning full end-to-end CLI prompt verification will fail without credentials. File verification is the fallback.
3. **Hermes Agent**:
   * **Path**: `/Users/uchebnick/.local/bin/hermes`
   * **Verification Command**: `hermes -s gunch chat -q "hello" --yolo`
   * **Result**: **Fully functional**. The command successfully spins up the agent, preloads the `gunch` skill, and outputs:
     `Hello. I am the Hermes Agent... I have the gunch skill preloaded...`
4. **Opencode**:
   * **Path**: `/Users/uchebnick/.opencode/bin/opencode`
   * **Verification Command**: Runs a interactive TUI by default. No simple CLI verification for skills exists besides verifying the file symlink `/Users/uchebnick/.config/opencode/skills/gunch` pointing to the global agents directory.
5. **Antigravity**:
   * **Path**: No binary named `antigravity` is globally installed. However, `antigravity-ide` is located at `/Users/uchebnick/.antigravity-ide/antigravity-ide/bin/antigravity-ide`.
   * **Verification**: File check for `~/.agents/skills/gunch/SKILL.md` and lock registration in `~/.agents/.skill-lock.json`.
6. **OpenClaw**:
   * **Path**: No CLI executable found on the system.
   * **Verification**: File check of `/Users/uchebnick/.openclaw/workspace/skills/gunch/SKILL.md`.

---

## 4. Verification Methods

To locally test the installer and check the skill integration across environments:

1. **Local Installer Dry-Run / Test**:
   Run `python3 install.py`.
2. **Codex Verification**:
   Inspect `~/.codex/commands/gunch.toml` and run `codex debug prompt-input | grep gunch`.
3. **Hermes Verification**:
   Run `hermes -s gunch chat -q "status" --yolo` and check if the agent reports having the skill preloaded.
4. **Symlink / File Verification**:
   Run the following file checks:
   ```bash
   test -f ~/.agents/skills/gunch/SKILL.md
   test -L ~/.claude/skills/gunch
   test -L ~/.config/opencode/skills/gunch
   test -f ~/.openclaw/workspace/skills/gunch/SKILL.md
   ```
