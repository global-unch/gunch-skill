# Adversarial Review Challenge Report

## Challenge Summary

**Overall risk assessment**: HIGH

---

## Challenges

### [Critical] Challenge 1: GitHub Remote URL Fallback returns 404
- **Assumption challenged**: The installation script assumes the remote repository `global-unch/gunch-skill` exists and has `SKILL.md` available on `main` branch.
- **Attack scenario**: Running `cat install.py | python3` from a directory that does not contain a local `SKILL.md` causes `urllib.request.urlopen` to attempt fetching from `https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md`.
- **Blast radius**: The network request returns an `HTTP Error 404: Not Found`, which causes the script to log `ERROR: Failed to download SKILL.md: HTTP Error 404: Not Found` and exit with code 1. The installation fails completely.
- **Mitigation**: Ensure that the `gunch-skill` repository is pushed to GitHub at `global-unch/gunch-skill` and the `main` branch has the `SKILL.md` file uploaded, or update the remote URL if it has moved.

### [High] Challenge 2: Hermes Configuration YAML Corruption via Naive String Matching
- **Assumption challenged**: The installation script assumes any line starting with `skills:` (after stripping whitespace) is the YAML skills configuration section block.
- **Attack scenario**: If the user's `~/.hermes/config.yaml` contains a multi-line description or block string literal that contains a line starting with `skills:` (e.g. in a description, message, or commented-out configuration), the script matches it and incorrectly injects `external_dirs:` within the block string context.
- **Blast radius**: Injects invalid YAML syntax into the block string literal, causing subsequent parses of `~/.hermes/config.yaml` to fail with parser errors, crashing the Hermes Agent CLI/IDE.
- **Mitigation**: Use a robust YAML parser (such as `ruamel.yaml` or `pyyaml`) if available, or enhance the regex/string matching parser to detect string literal blocks (e.g., checking if the previous section started with `|` or `>`) and ignore them.

---

## Stress Test Results

- **Run install from stdin without SKILL.md** → Script downloads fallback from GitHub and completes installation → Script fails with HTTP 404 Not Found and exits → **FAIL**
- **Hermes config with skills: inside block string** → Script ignores string literal content and appends/updates actual config → Script injects `external_dirs` inside the string block corrupting the YAML structure → **FAIL**
- **Verify skills listed in Hermes CLI** → `hermes skills list` displays the newly installed `gunch` skill correctly → `gunch` skill is correctly listed and enabled → **PASS**
- **Verify Codex configuration command description** → `~/.codex/commands/gunch.toml` matches parsed description → Codex description matches frontmatter → **PASS**

---

## Unchallenged Areas

- **Antigravity CLI behavior** — Antigravity loading behavior was not verified via its CLI because no dedicated Antigravity CLI commands (like lists or chats) were available in the workspace environment.
- **Claude Code/Opencode CLI integration** — Verifying that Claude Code and Opencode dynamically pick up the symlink and enable it was not fully verified via their respective CLIs due to lack of CLI testing support for these platforms in the sandbox.
