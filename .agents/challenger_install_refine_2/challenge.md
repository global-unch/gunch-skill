# Challenge Report — Gunch Skill Installation Verification

## Challenge Summary

**Overall risk assessment**: HIGH

The installation script (`install.py`) is generally well-structured and handles most mock environments correctly. However, a critical issue with the raw GitHub remote fallback URL prevents the quick-install feature from working on clean environments (resulting in a 404 error). Additionally, a potential edge-case bug in symlink cleanup could cause `NotADirectoryError` crashes.

---

## Challenges

### [High] Challenge 1: Broken Quick-Install Remote Fallback URL (404 Not Found)

- **Assumption challenged**: The remote URL `https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md` is publicly accessible and contains the current skill definition.
- **Attack scenario**: A user runs the quick installation command:
  ```bash
  curl -sSL https://raw.githubusercontent.com/global-unch/gunch-skill/main/install.py | python3
  ```
  on a system where the repository has not been cloned locally (or from a directory without `SKILL.md`). The script checks local and developer fallback paths, fails to find them, and attempts to fetch `SKILL.md` from the remote repository. It fails with `HTTP Error 404: Not Found` because the upstream repository is either missing or private.
- **Blast radius**: Complete failure of the quick-install flow for new users, preventing installation.
- **Mitigation**:
  1. Ensure the `global-unch/gunch-skill` repository is created and set to public on GitHub.
  2. Push `SKILL.md` to the `main` branch.
  3. Alternatively, embed the `SKILL.md` contents inside `install.py` as a fallback text block to guarantee offline installation reliability.

### [Medium] Challenge 2: NotADirectoryError when Symlink Path exists as a Regular File

- **Assumption challenged**: Any pre-existing item at `~/.claude/skills/gunch` or `~/.config/opencode/skills/gunch` is either a directory or a symlink.
- **Attack scenario**: If a regular file exists at `~/.claude/skills/gunch` (e.g. from user configuration or conflict), `os.path.exists(symlink_path)` evaluates to `True`, but `os.path.islink(symlink_path)` evaluates to `False`. The script then calls `shutil.rmtree(symlink_path)`. Since the path is a file, `shutil.rmtree` raises a `NotADirectoryError` and crashes the installer.
- **Blast radius**: The installation fails and terminates abruptly.
- **Mitigation**: Update the cleanup block in `install_claude()` and `install_opencode()` to handle regular files using `os.remove` or `os.unlink`:
  ```python
  if os.path.exists(symlink_path) or os.path.islink(symlink_path):
      if os.path.islink(symlink_path) or os.path.isfile(symlink_path):
          os.unlink(symlink_path)
      else:
          shutil.rmtree(symlink_path)
  ```

---

## Stress Test Results

- **Hermes config skills key inside block string** → The installer successfully avoids matching indented `skills:` keys in description block strings, correctly appending/injecting the `external_dirs` configuration at the top level. → **PASS**
- **Hermes config missing skills section** → The installer appends the complete `skills.external_dirs` structure to the end of the YAML file. → **PASS**

---

## Unchallenged Areas

- **Platform-specific CLI behaviors (except Hermes)** — CLIs for Codex, Claude Code, Opencode, and OpenClaw were not run directly to list their skills since they lack specific standalone CLI commands like `hermes skills list`, or because they rely on simple path-based automatic loading which was verified path-by-path.
