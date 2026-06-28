# Handoff Report

## 1. Observation
- **Remote Fallback Failure**:
  Running the installation script from a directory without `SKILL.md` via stdin:
  ```bash
  cat /Users/uchebnick/projects/gunch-skill/install.py | python3
  ```
  resulting in the terminal output:
  ```
  [INFO] Local SKILL.md not found. Fetching from https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md...
  ERROR: Failed to download SKILL.md: HTTP Error 404: Not Found
  ```
- **Git Repository State**:
  Running `git remote -v` in `/Users/uchebnick/projects/gunch-skill` returned:
  ```
  origin  https://github.com/global-unch/gunch-skill (fetch)
  origin  https://github.com/global-unch/gunch-skill (push)
  ```
  Running `git status` returned:
  ```
  On branch main
  Your branch is based on 'origin/main', but the upstream is gone.
  ```
- **Hermes YAML parser corruption**:
  Running the stress test script `stress_test.py` with an adversarial YAML string containing `skills:` inside a description block:
  ```yaml
  description: |
    This is a description of my agent.
    skills:
    - math
    - coding
  ```
  resulted in the following corrupted output in `~/.hermes/config.yaml`:
  ```yaml
  description: |
    This is a description of my agent.
    skills:
      external_dirs:
        - /var/folders/1b/dgwzzm7n7pgfzsxhch55nw3h0000gn/T/tmpklkfvxd9/.agents/skills
    - math
    - coding
  ```
- **Successful local installation**:
  Running `python3 install.py` from the project directory completed successfully and created the expected symlinks and files:
  - Global: `~/.agents/skills/gunch/SKILL.md` and `~/.agents/.skill-lock.json`
  - Claude Code: `~/.claude/skills/gunch` (symlink)
  - Codex: `~/.codex/commands/gunch.toml` (TOML format)
  - Opencode: `~/.config/opencode/skills/gunch` (symlink)
  - OpenClaw: `~/.openclaw/workspace/skills/gunch/SKILL.md` (frontmatter merged)
  - Hermes Agent: `~/.hermes/config.yaml` updated successfully to include the path `~/.agents/skills`.
- **CLI loading check**:
  Running `hermes skills list` showed:
  ```
  │ gunch                   │                      │ local   │ local   │ enabled │
  ```

## 2. Logic Chain
1. Since the git remote upstream is gone (`git status`) and the repository has not been published to GitHub yet, requesting `https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md` returns a `404 Not Found` error.
2. In `install.py` line 36, the url is hardcoded to `https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md`. When run from stdin or a location without local `SKILL.md`, it falls back to this URL. Because of the 404, the installation fails immediately and exits with code 1.
3. In `install.py` line 226, the script searches for the YAML skills section via `line.strip().startswith("skills:")`. When an adversarial `config.yaml` includes `skills:` inside a multi-line string block (such as `description:`), this naïve check matches the line and injects the `external_dirs` entry directly under it, violating the YAML indentation structure and corrupting the config file.
4. When `SKILL.md` is locally available and the config is well-formed, all copy and symlink operations execute successfully across all 6 environments, and the Gunch skill is correctly loaded and listed as enabled in the Hermes CLI list.

## 3. Caveats
- We did not verify the dynamic loading of skills in Opencode, OpenClaw, and Claude Code CLIs because they do not have active list/chat verification commands in the current environment context. However, the file presence and symlinks were fully verified.
- We did not test behavior under multi-user access permissions or strict read-only filesystems.

## 4. Conclusion
The local installation script works correctly and configures all 6 environments when a local `SKILL.md` is present. However, it fails with a **Critical bug** (HTTP 404) when trying to install via stdin/fallback because the remote repository is not published yet. It also contains a **High risk bug** where naïve YAML parsing corrupts `~/.hermes/config.yaml` if the string `skills:` is present inside other block literals.

## 5. Verification Method
To reproduce the findings:
1. **Fallback download failure**: Run `cd /tmp && cat /Users/uchebnick/projects/gunch-skill/install.py | python3`. Observe the `HTTP Error 404: Not Found` traceback and script exit.
2. **YAML corruption**: Run `python3 /Users/uchebnick/projects/gunch-skill/stress_test.py`. Note the failure in `test_hermes_skills_in_block_string` and the corrupted config layout printed in stdout.
3. **Hermes loading check**: Run `hermes skills list` and verify `gunch` is in the list of installed and enabled skills.
